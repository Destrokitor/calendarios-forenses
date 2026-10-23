"""Motor do TJSP (Tribunal de Justiça de São Paulo): o MOTOR MODELO dos demais.

Fontes, todas oficiais do TJSP (ver docs/fichas/TJSP.md):

  1. Consulta pública "Expediente Forense / Suspensão de Prazos" do portal do tribunal
     (https://www.tjsp.jus.br/CanaisComunicacao/Feriados/ExpedienteForense). A página
     preenche duas tabelas chamando dois endereços que devolvem JSON, por comarca e ano:
       .../Feriados/PesquisarFeriados?nomeMunicipio=X&codigoMunicipio=0&ano=AAAA
       .../Feriados/PesquisarSuspensoes?nomeMunicipio=X&codigoMunicipio=0&ano=AAAA
     É a fonte principal porque já traz as ALTERAÇÕES posteriores ao provimento (em 2026,
     o Dia do Servidor passou de 28/10 para 30/10) e os feriados municipais de cada comarca.
  2. Lista das comarcas: página "Regiões Administrativas Judiciárias" do portal.
  3. Provimento CSM do ano (PDF do DJE, e-SAJ), lido com `pdftotext`: só para o que a
     consulta pública NÃO traz: o recesso de 20 a 31/12 e a Quarta-feira de Cinzas
     (expediente a partir das 13h). O endereço do PDF muda todo ano (é um código aleatório
     do e-SAJ): ver PROVIMENTOS e a ficha.
  4. Anos disponíveis na consulta (`ObterAnos`): é como o motor sabe se o ano seguinte já saiu.

Abrangência: o que vale para o estado inteiro vai em `geral`; o que é de uma comarca vai em
`locais[COMARCA]`. "Geral" é a data presente em pelo menos 90% das comarcas consultadas
(o portal mistura numa só lista os dias do provimento e os feriados municipais, e só o
texto "PROVIMENTO CSM" os distingue; contar as comarcas não depende desse texto).
"""
from __future__ import annotations

import collections
import datetime
import json
import re
import subprocess
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

BASE = "https://www.tjsp.jus.br"
URL_ANOS = BASE + "/CanaisComunicacao/Feriados/ObterAnos"
URL_COMARCAS = BASE + "/QuemSomos/QuemSomos/RegioesAdministrativasJudiciarias"
URL_FERIADOS = BASE + "/CanaisComunicacao/Feriados/PesquisarFeriados"
URL_SUSPENSOES = BASE + "/CanaisComunicacao/Feriados/PesquisarSuspensoes"
URL_PAGINA = BASE + "/CanaisComunicacao/Feriados/ExpedienteForense"

# Provimento CSM de cada ano (PDF do DJE no e-SAJ). O código na URL é aleatório e novo a cada
# ano: o do próximo sai por volta de novembro (ver ficha). Ano que não está aqui NÃO impede o
# motor: ele usa só a consulta pública e cobre o recesso de dezembro pela regra do CPC art. 220.
PROVIMENTOS: Dict[int, str] = {
    2026: "https://esaj.tjsp.jus.br/gcn-services/api/publico/origemnormaleg/arquivo/lXJ1041xK4/RY1PXz518K",
}

# Nome da RAJ (lista de comarcas) -> nome que a consulta pública conhece. Descoberto
# comparando as duas listas; sem isto a consulta devolve vazio para estas comarcas.
ALIAS_PORTAL: Dict[str, str] = {
    "Carapicuiba": "Carapicuíba",
    "Estrela D'Oeste": "Estrela dOeste",
    "Cerqueira Cesar": "Cerqueira César",
    "Rio Grande de Serra": "Rio Grande da Serra",
    "Santa Rosa do Viterbo": "Santa Rosa de Viterbo",
    "Santana do Parnaíba": "Santana de Parnaíba",
    "São Luis do Paraitinga": "São Luiz do Paraitinga",
}
# Aparece na lista de comarcas do portal mas a consulta pública não a conhece (e o DJE
# também não a lista entre as comarcas com feriado municipal).
SEM_CALENDARIO_NO_PORTAL = {"Vila Mimosa"}
LIMITE_COMARCAS_SEM_DADO = 5  # mais que isso = a leitura quebrou, não é detalhe de cadastro

FRACAO_GERAL = 0.9  # data presente em >= 90% das comarcas = vale para o estado todo

_MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def pascoa(ano: int) -> datetime.date:
    """Domingo de Páscoa (algoritmo de Meeus/Jones/Butcher, calendário gregoriano).

    Dá as datas móveis: Carnaval = Páscoa - 48 e - 47 dias; Sexta-feira da Paixão =
    Páscoa - 2; Corpus Christi = Páscoa + 60. O motor não INVENTA data com isto (tudo vem
    da fonte); os testes usam para conferir que a fonte bate com o calendário."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia_ = divmod(h + l - 7 * m + 114, 31)
    return datetime.date(ano, mes, dia_ + 1)


def _json(corpo: bytes, url: str) -> Any:
    try:
        return json.loads(corpo.decode("utf-8-sig"))
    except ValueError as e:
        raise ErroDeFonte("resposta que não é JSON em %s: %s" % (url, e))


def _data_br(texto: str) -> datetime.date:
    d, m, a = texto.strip().split("/")
    return datetime.date(int(a), int(m), int(d))


def _intervalo(texto: str) -> List[datetime.date]:
    """'07/01/2026 a 20/01/2026' ou '30/06/2026' -> lista de datas (inclusive)."""
    partes = [p.strip() for p in texto.split(" a ")]
    ini = _data_br(partes[0])
    fim = _data_br(partes[-1])
    return [ini + datetime.timedelta(days=n) for n in range((fim - ini).days + 1)]


def ler_anos(html: bytes) -> Set[int]:
    return {int(x) for x in re.findall(r'<option value="(\d{4})"', html.decode("utf-8", "replace"))}


def ler_comarcas(html: bytes) -> List[str]:
    """Nomes das comarcas na página das RAJ: itens 'Nome - 44ª CJ' ou 'São Paulo - Capital'."""
    texto = html.decode("utf-8", "replace")
    nomes: List[str] = []
    for item in re.findall(r"<li[^>]*>(.*?)</li>", texto, flags=re.S):
        item = re.sub(r"<[^>]+>", "", item).replace("\xa0", " ").strip()
        m = re.match(r"^(.+?) - (?:\d+ª CJ|Capital)$", item)
        if m:
            nome = " ".join(m.group(1).replace("’", "'").split())
            if nome not in nomes:
                nomes.append(nome)
    return nomes


def nome_no_portal(nome_raj: str) -> str:
    return ALIAS_PORTAL.get(nome_raj, nome_raj)


def _tipo_suspensao(motivo: str) -> Optional[str]:
    """Só entram as suspensões estruturadas do estado inteiro: o recesso e a suspensão de
    prazos do art. 116 §2º do RITJSP. Comunicado conjunto (texto livre) devolve None."""
    m = motivo.lower()
    if m.startswith("recesso forense"):
        return "recesso"
    if re.match(r"^suspens[ãa]o dos prazos processuais( - art\. 116.*)?$", m):
        return "suspensao_prazo"
    return None


def _horario(motivo: str) -> str:
    """'A PARTIR DAS 12 HORAS - ...' -> 'a partir das 12h' (dia parcial); senão ''."""
    m = re.search(r"A PARTIR DAS (\d{1,2})(?::(\d{2}))? ?(?:HORAS|H)", motivo.upper())
    if m:
        return "a partir das %sh%s" % (int(m.group(1)), m.group(2) or "")
    m = re.search(r"AT[ÉE] (?:AS|ÀS) (\d{1,2})(?::(\d{2}))? ?(?:HORAS|H)", motivo.upper())
    if m:
        return "até as %sh%s" % (int(m.group(1)), m.group(2) or "")
    return ""


def pdf_para_texto(pdf: bytes) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def ler_provimento(texto: str, ano: int) -> Dict[str, Any]:
    """Do texto do Provimento CSM: recesso de dezembro e Quarta-feira de Cinzas.

    Devolve {"recesso": [datas], "cinzas": (data, 'a partir das 13h') ou None}."""
    plano = " ".join(texto.split())
    m = re.search(r"suspens[ãa]o do expediente forense no exerc[íi]cio de (\d{4})", plano, flags=re.I)
    if not m or int(m.group(1)) != ano:
        raise ErroDeFonte("o PDF do provimento não é o de %d" % ano)
    plano = plano[m.start():]
    achou: Dict[str, Any] = {"recesso": [], "cinzas": None}
    r = re.search(r"per[íi]odo de (\d{1,2})º? a (\d{1,2}) de janeiro e de (\d{1,2}) a (\d{1,2}) (?:de )?dezembro de %d" % ano,
                  plano, flags=re.I)
    if not r:
        raise ErroDeFonte("não achei o período de recesso no provimento de %d" % ano)
    j1, j2, d1, d2 = (int(x) for x in r.groups())
    achou["recesso"] = (
        [datetime.date(ano, 1, n) for n in range(j1, j2 + 1)]
        + [datetime.date(ano, 12, n) for n in range(d1, d2 + 1)]
    )
    c = re.search(r"No dia (\d{2})/(\d{2})/%d \(Quarta-?[Ff]eira de Cinzas\).{0,600}?a partir das (\d{1,2}) horas" % ano, plano)
    if c:
        achou["cinzas"] = (datetime.date(ano, int(c.group(2)), int(c.group(1))), "a partir das %sh" % int(c.group(3)))
    return achou


class MotorTJSP(Motor):
    sigla = "TJSP"
    precisa_ip_brasil = False  # testado do GitHub: os três endereços (portal e e-SAJ) respondem
    parcial = (
        "Ficam de fora as suspensões de prazo de UNIDADES específicas (varas, anexos, juizados, "
        "RAJ inteira) por comunicado conjunto: o portal as entrega como texto livre, sem campo "
        "estruturado de qual unidade é afetada, e lançá-las na comarca inteira suspenderia prazo "
        "de quem não foi afetado. Também fora: suspensões do 2º grau e de processos físicos "
        "(páginas próprias do tribunal), indisponibilidade de sistema (página própria) e "
        "feriados municipais de município que não é sede de comarca. Vila Mimosa consta da lista "
        "de comarcas do portal mas não tem calendário na consulta pública."
    )
    esperado = {
        "min_geral": 40,
        "min_locais": 300,
        # Conferidas à mão no Provimento CSM 2.813/2025 (art. 1º) E na consulta pública.
        # 28/10 (Dia do Servidor) NÃO é âncora: foi movido para 30/10 por provimento de 2026.
        "ancoras": {
            "2026-02-16": "Carnaval",
            "2026-02-17": "Carnaval",
            "2026-04-02": "Endoenças",
            "2026-04-03": "Sexta-feira da Paixão",
            "2026-05-01": "Dia do Trabalho",
            "2026-11-20": "Consciência Negra",
            "2026-12-08": "Dia da Justiça",
        },
        "exige_recesso": True,
    }

    # --- coleta -------------------------------------------------------------------------

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        anos = ler_anos(rede.baixar(URL_ANOS))
        if ano not in anos:
            raise AindaNaoPublicado("a consulta pública do TJSP ainda não lista %d (lista: %s)" % (ano, sorted(anos)))

        nomes_raj = [n for n in ler_comarcas(rede.baixar(URL_COMARCAS)) if n not in SEM_CALENDARIO_NO_PORTAL]
        if len(nomes_raj) < 300:
            raise ErroDeFonte("lista de comarcas lida pela metade (%d)" % len(nomes_raj))

        feriados: Dict[str, List[Dict[str, Any]]] = {}
        suspensoes: Dict[str, List[Dict[str, Any]]] = {}
        sem_dado: List[str] = []
        for nome in nomes_raj:
            portal = nome_no_portal(nome)
            fer = self._consultar(rede, URL_FERIADOS, portal, ano)
            if not fer:
                sem_dado.append(nome)  # nome que a consulta não reconhece
                continue
            feriados[portal] = fer
            suspensoes[portal] = self._consultar(rede, URL_SUSPENSOES, portal, ano)
        if len(sem_dado) > LIMITE_COMARCAS_SEM_DADO:
            raise ErroDeFonte("consulta sem dados para %d comarcas (ex.: %s): o nome ou o formato mudou"
                              % (len(sem_dado), ", ".join(sem_dado[:5])))

        return self.montar(ano, feriados, suspensoes, self._provimento(ano, rede))

    @staticmethod
    def _consultar(rede: Cliente, base: str, nome: str, ano: int) -> List[Dict[str, Any]]:
        url = base + "?" + urllib.parse.urlencode({"nomeMunicipio": nome, "codigoMunicipio": 0, "ano": ano})
        dados = _json(rede.baixar(url), url)
        if not isinstance(dados, dict) or not isinstance(dados.get("data"), list):
            raise ErroDeFonte("formato inesperado em %s" % url)
        return dados["data"]

    @staticmethod
    def _provimento(ano: int, rede: Cliente) -> Optional[Dict[str, Any]]:
        url = PROVIMENTOS.get(ano)
        if not url:
            return None
        return ler_provimento(pdf_para_texto(rede.baixar(url)), ano)

    # --- montagem (sem rede: é o que os testes exercitam) -------------------------------

    def montar(self, ano: int, feriados: Dict[str, List[Dict[str, Any]]],
               suspensoes: Dict[str, List[Dict[str, Any]]], prov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        cal = calendario_vazio(self.sigla, ano)
        cal["fontes"] = [
            {"id": "portal", "url": URL_PAGINA,
             "descricao": "Consulta pública do TJSP: feriados e suspensões por comarca (JSON do portal)"},
            {"id": "comarcas", "url": URL_COMARCAS,
             "descricao": "Lista de comarcas (Regiões Administrativas Judiciárias) do portal do TJSP"},
        ]
        n = len(feriados)
        minimo = max(1, int(FRACAO_GERAL * n + 0.9999))  # teto: 90% de n

        # 1) feriados: data -> quantas comarcas a têm; descrição mais comum
        contagem: collections.Counter = collections.Counter()
        descricoes: Dict[datetime.date, collections.Counter] = collections.defaultdict(collections.Counter)
        por_comarca: Dict[str, Dict[datetime.date, List[str]]] = {}
        for comarca, itens in feriados.items():
            mapa: Dict[datetime.date, List[str]] = collections.defaultdict(list)
            for it in itens:
                data = _data_br(it["Data"])
                motivo = " ".join(str(it["Descricao"]).split())
                if data.year != ano or not motivo:
                    continue
                if motivo not in mapa[data]:
                    mapa[data].append(motivo)
            por_comarca[comarca] = mapa
            for data, motivos in mapa.items():
                contagem[data] += 1
                for m in motivos:
                    descricoes[data][m] += 1
        datas_gerais = {d for d, c in contagem.items() if c >= minimo}
        if len(datas_gerais) < 10 and ano > datetime.date.today().year:
            # o ano já aparece na consulta mas só com cadastro parcial: ainda não saiu o provimento
            raise AindaNaoPublicado("consulta do TJSP lista %d mas sem os dias do provimento" % ano)
        for data in sorted(datas_gerais):
            motivo = sorted(descricoes[data].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            # DUVIDA: "SUSPENSÃO DO EXPEDIENTE" (20/04, 05/06, 10/07, 07/12 de 2026) tem horas a
            # repor pelos servidores, mas o art. 1º do provimento diz "não haverá expediente":
            # tratado como sem_expediente, igual aos feriados.
            cal["geral"].append(dia(data, "sem_expediente", motivo, "portal"))

        # 2) suspensões e recesso do estado inteiro (mesma regra dos 90%)
        contagem_s: collections.Counter = collections.Counter()
        desc_s: Dict[datetime.date, collections.Counter] = collections.defaultdict(collections.Counter)
        susp_comarca: Dict[str, Dict[datetime.date, str]] = {}
        for comarca, itens in suspensoes.items():
            mapa_s: Dict[datetime.date, str] = {}
            for it in itens:
                motivo = " ".join(str(it["Descricao"]).split())
                tipo = _tipo_suspensao(motivo)
                if tipo is None:  # comunicado de unidade específica: fora (ver `parcial`)
                    continue
                for data in _intervalo(it["Data"]):
                    if data.year == ano:
                        mapa_s.setdefault(data, motivo)
            susp_comarca[comarca] = mapa_s
            for data, motivo in mapa_s.items():
                contagem_s[data] += 1
                desc_s[data][motivo] += 1
        for data, c in sorted(contagem_s.items()):
            if c < minimo:
                continue  # suspensão que só algumas comarcas têm (ex.: todas as de uma RAJ): ver abaixo
            motivo = sorted(desc_s[data].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            # DUVIDA: 07 a 20/01 é "suspensão dos prazos processuais" (art. 116 §2º do RITJSP),
            # não "sem expediente": o fórum abre, o prazo não corre. Tipo suspensao_prazo.
            cal["geral"].append(dia(data, _tipo_suspensao(motivo) or "suspensao_prazo", motivo, "portal"))

        # 3) o que só o provimento traz: recesso de dezembro e Quarta-feira de Cinzas
        ja_recesso = {d["data"] for d in cal["geral"] if d["tipo"] == "recesso"}
        if prov is not None:
            cal["fontes"].append({"id": "provimento", "url": PROVIMENTOS[ano],
                                  "descricao": "Provimento CSM nº 2.813/2025 (DJE de 25/11/2025), art. 1º §1º e art. 2º"
                                  if ano == 2026 else "Provimento CSM do exercício de %d (DJE)" % ano})
            for data in prov["recesso"]:
                if data.isoformat() not in ja_recesso:
                    cal["geral"].append(dia(data, "recesso", "Recesso forense (art. 116, §2º do RITJSP)", "provimento"))
            if prov["cinzas"]:
                data, horario = prov["cinzas"]
                # DUVIDA: a norma fixa o início do ATENDIMENTO ao público às 13h (art. 2º §2º);
                # tratado como dia parcial (CPC art. 224 §1º): conta, mas não pode ser começo nem fim.
                cal["geral"].append(dia(data, "parcial", "Quarta-feira de Cinzas", "provimento", horario))
        else:
            # Sem o provimento do ano: o recesso de 20 a 31/12 vem da lei, não do provimento.
            cal["fontes"].append({"id": "cpc-220", "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm",
                                  "descricao": "CPC, art. 220: suspensão dos prazos de 20 de dezembro a 20 de janeiro"})
            # DUVIDA: sem o provimento do ano, 20 a 31/12 entra como suspensao_prazo (lei), não
            # como "recesso" sem expediente; o provimento (publicado em nov.) é que confirma o recesso.
            for n_ in range(20, 32):
                cal["geral"].append(dia(datetime.date(ano, 12, n_), "suspensao_prazo",
                                        "Suspensão dos prazos processuais de 20/12 a 20/01 (CPC, art. 220)", "cpc-220"))

        # 4) locais: todo o resto, por comarca (TODAS entram, mesmo sem dia próprio)
        for comarca in sorted(feriados):
            lista: List[Dict[str, str]] = []
            for data, motivos in sorted(por_comarca[comarca].items()):
                if data in datas_gerais:
                    continue
                for motivo in motivos:
                    hora = _horario(motivo)
                    # DUVIDA: feriado MUNICIPAL: o juiz/tribunal pode exigir prova (CPC art. 1.003 §6º,
                    # para recurso). O motor só registra o que o tribunal publicou.
                    lista.append(dia(data, "parcial" if hora else "sem_expediente", motivo, "portal", hora))
            cal["locais"][normalizar_local(comarca)] = lista
        return cal


MOTOR = MotorTJSP()
