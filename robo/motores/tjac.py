"""Motor do TJAC (Tribunal de Justiça do Estado do Acre). Ficha: docs/fichas/TJAC.md.

Fonte única, oficial: Portaria PRESI nº 6569/2025 (DJe 7.950, de 3.2.2026, p. 18-19), que traz o
calendário de 2026 em uma tabela por mês com as colunas DIA | SEMANA | EVENTO | TIPO | NATUREZA |
LEGISLAÇÃO.

Leitura: o `pdftotext -bbox` dá a posição de cada palavra. Cada linha da tabela começa com o DIA
(âncora). Uma célula que quebra em várias linhas é centralizada na linha, então EVENTO, TIPO e
NATUREZA são atribuídos à âncora mais próxima pelo centro vertical. As colunas são medidas pelo
cabeçalho de cada mês (a posição muda um pouco de mês para mês).

Efeito de cada linha:
  - Feriado nacional, estadual, forense ou regimental -> sem_expediente em `geral`.
  - Feriado municipal -> sem_expediente em `locais[MUNICÍPIO]`, um dia para cada município citado.
    Aniversário de município conta como feriado municipal (Art. 2º).
  - Ponto facultativo (estadual ou municipal) -> FORA. O Art. 2º, parágrafo único, diz que o
    ponto municipal depende de adesão do foro, e o documento não diz se houve adesão. O estadual
    não diz o efeito sobre o prazo. # DUVIDA: a revisão decide se algum ponto vira sem_expediente.
  - Data "adiada" (a linha traz "Comemoração do dia X adiada para o dia Y"): a linha da data X
    fica FORA e a data Y não entra. # DUVIDA: o documento não diz qual vale para o expediente.
    Adiadas nesta portaria: 20/01 (Dia do Católico -> 22/01), 28/10 (Dia do Servidor -> 30/10),
    17/11 (Tratado de Petrópolis -> 19/11).

Não entra (ver `parcial`): ponto facultativo, datas adiadas, recesso de 20/12 a 20/01 (a portaria
não traz; o CPC art. 220 não é aplicado aqui por regra fixa) e os municípios sem ato no documento.
"""
from __future__ import annotations

import datetime
import html
import re
import subprocess
import unicodedata
from typing import Any, Dict, List

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_ID = "portaria"
FONTE_DESCRICAO = ("Portaria PRESI nº 6569/2025 (calendário 2026: feriados, pontos facultativos e "
                   "suspensão de expediente), DJe 7.950, de 3.2.2026, p. 18-19")

# Endereço de cada ano que o motor sabe ler. A ficha conhece só o de 2026; para os demais anos o
# motor levanta AindaNaoPublicado (ver coletar).
EDICOES: Dict[int, str] = {
    2026: "https://webdev.tjac.jus.br/wp-content/uploads/2025/12/Portaria_PRESI_TJAC_6569_2025.pdf",
}

MESES = {"JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
         "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12}
CABECALHOS = ("DIA", "SEMANA", "EVENTO", "TIPO", "NATUREZA", "LEGISLAÇÃO")

_RE_PALAVRA = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', re.S)
_RE_DIA = re.compile(r"(\d{1,2})[º°]?")
_RE_FORA = re.compile(r"PODER JUDICI|Tribunal de Justiça|Pág\. \d|Publicado no DJe|Documento assinado")
_RE_SEMANA = re.compile(r"^(Segunda|Ter[cç]a|Quarta|Quinta|Sexta|S[aá]bado|Domingo|[Ff]eira)")
_VOCAB_TIPO = {"Feriado", "Ponto", "facultativo", "Facultativo", "forense", "Forense", "regimental"}
_RE_INICIO_NAT =re.compile(r"(Feriado|Municipal|Estadual|Nacional|Regimental|Ponto)\b")
_RE_ADIADA_1 = re.compile(r"Comemoração do dia (\d{1,2})$")
_RE_ADIADA_2 = re.compile(r"adiada para o dia (\d{1,2})")


def pdf_para_palavras(pdf: bytes) -> str:
    """PDF em bytes -> saída do `pdftotext -bbox` (HTML com a posição de cada palavra)."""
    try:
        r = subprocess.run(["pdftotext", "-bbox", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


def _palavras(conteudo: str) -> List[Dict[str, Any]]:
    """Palavras com página e posição. `y` é uma escala única do PDF inteiro (página * 10000 + centro)."""
    palavras: List[Dict[str, Any]] = []
    for n, bloco in enumerate(conteudo.split("<page ")[1:], start=1):
        for m in _RE_PALAVRA.finditer(bloco):
            x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
            yc = (y0 + y1) / 2
            palavras.append({"p": n, "x0": x0, "x1": x1, "yc": yc, "y": n * 10000 + yc,
                           "t": _nfc(html.unescape(m.group(5)).strip())})
    return [w for w in palavras if w["t"]]


def _linhas(palavras: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Agrupa palavras em linhas (altura igual, até 3 pt de diferença), cada uma em ordem de x."""
    linhas: List[List[Dict[str, Any]]] = []
    for w in sorted(palavras, key=lambda w: w["y"]):
        if linhas and w["y"] - linhas[-1][-1]["y"] <= 3:
            linhas[-1].append(w)
        else:
            linhas.append([w])
    for linha in linhas:
        linha.sort(key=lambda w: w["x0"])
    return linhas


def _sem_cabecalho_e_rodape(palavras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Tira o cabeçalho da página ("PODER JUDICIÁRIO..."), o rodapé ("Pág. 3/7") e o DJe."""
    fora = set()
    for linha in _linhas(palavras):
        if _RE_FORA.search(" ".join(w["t"] for w in linha)):
            fora.update(id(w) for w in linha)
    return [w for w in palavras if id(w) not in fora]


def _secoes(palavras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Um trecho por mês: do nome do mês até o próximo nome de mês. Guarda o cabeçalho da tabela."""
    marcas = sorted([w for w in palavras if w["t"] in MESES], key=lambda w: w["y"])
    secoes = []
    for i, marca in enumerate(marcas):
        fim = marcas[i + 1]["y"] if i + 1 < len(marcas) else float("inf")
        cab: Dict[str, Dict[str, Any]] = {}
        for w in palavras:
            if marca["y"] < w["y"] < marca["y"] + 40 and w["t"] in CABECALHOS and w["t"] not in cab:
                cab[w["t"]] = w
        if len(cab) != len(CABECALHOS):
            raise ErroDeFonte("cabeçalho da tabela de %s incompleto (achei %s)" % (marca["t"], sorted(cab)))
        y_cab = cab["DIA"]["y"]
        trecho = [w for w in palavras
                  if marca["y"] < w["y"] < fim
                  and not (w["t"] in CABECALHOS and abs(w["y"] - y_cab) <= 3)]
        secoes.append({"mes": MESES[marca["t"]], "cab": cab, "palavras": trecho})
    return secoes


def _colunas(cab: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """Limites de coluna (x). Cada palavra cai na coluna pelo x inicial."""
    x = {k: v["x0"] for k, v in cab.items()}
    return {
        "dia": (x["DIA"] + x["SEMANA"]) / 2,          # número do dia
        "semana_fim": (x["SEMANA"] + x["EVENTO"]) / 2,  # SEMANA termina antes daqui
        "tipo": x["TIPO"] - 8,                       # EVENTO termina antes daqui
        "nat": (x["TIPO"] + x["NATUREZA"]) / 2,
        "leg": x["LEGISLAÇÃO"] - 40,                  # NATUREZA termina antes de ~423; LEGISLAÇÃO começa em ~426
    }


def _junta(palavras: List[Dict[str, Any]]) -> str:
    return " ".join(w["t"] for w in sorted(palavras, key=lambda w: (w["y"], w["x0"])))


def _aberto(texto: str) -> bool:
    return texto.count("(") > texto.count(")")


def _linhas_da_tabela(secao: Dict[str, Any], ano: int) -> List[Dict[str, Any]]:
    """Registros de um mês. Cada célula de NATUREZA é um registro (um feriado ou ponto). A data é a
    âncora de DIA mais próxima: um mesmo dia pode cobrir mais de um registro (célula DIA mesclada).
    EVENTO e TIPO vão para o registro de NATUREZA mais próximo pelo centro vertical."""
    c = _colunas(secao["cab"])
    palavras = secao["palavras"]
    ancoras = sorted([w for w in palavras if w["x0"] < c["dia"] and _RE_DIA.fullmatch(w["t"])],
                     key=lambda w: w["y"])
    if not ancoras:
        raise ErroDeFonte("nenhuma linha de dia no mês %d" % secao["mes"])
    ids_ancoras = {id(w) for w in ancoras}

    leg: List[Dict[str, Any]] = []
    nat_palavras: List[Dict[str, Any]] = []
    outras: List[Dict[str, Any]] = []
    for w in palavras:
        if id(w) in ids_ancoras or w["x0"] < c["dia"]:
            continue
        if w["x0"] >= c["leg"]:
            leg.append(w)
        elif w["x0"] >= c["nat"]:
            nat_palavras.append(w)
        elif w["x0"] >= c["tipo"] or (w["t"] in _VOCAB_TIPO and w["x0"] >= c["semana_fim"]):
            # "facultativo" e "forense" podem começar um pouco antes do limite da coluna TIPO
            outras.append(dict(w, coluna="tipo"))
        elif w["x0"] < c["semana_fim"] and _RE_SEMANA.match(w["t"]):
            continue  # coluna SEMANA (ex.: "Segunda-", "feira")
        else:
            outras.append(dict(w, coluna="ev"))

    # NATUREZA: uma célula pode quebrar em linhas; "(...)" aberto junta a linha seguinte.
    celulas: List[Dict[str, Any]] = []
    for linha in _linhas(nat_palavras):
        texto = " ".join(w["t"] for w in linha)
        y = sum(w["y"] for w in linha) / len(linha)
        if celulas and (_aberto(celulas[-1]["texto"]) or not _RE_INICIO_NAT.match(texto)):
            celulas[-1]["texto"] += " " + texto
            celulas[-1]["ys"].append(y)
        else:
            celulas.append({"texto": texto, "ys": [y]})
    if not celulas:
        raise ErroDeFonte("nenhuma NATUREZA no mês %d" % secao["mes"])

    registros: List[Dict[str, Any]] = []
    for cel in celulas:
        centro = sum(cel["ys"]) / len(cel["ys"])
        dia_ = min(ancoras, key=lambda a: abs(a["y"] - centro))
        registros.append({"y": centro, "nat": cel["texto"], "tipo": [], "ev": [], "adiada": None,
                          "dia": int(_RE_DIA.fullmatch(dia_["t"]).group(1))})

    def mais_perto(y: float) -> Dict[str, Any]:
        return min(registros, key=lambda r: abs(r["y"] - y))

    for w in outras:
        r = mais_perto(w["y"])
        r["tipo" if w["coluna"] == "tipo" else "ev"].append(w)

    # Data adiada: "Comemoração do dia X" + "adiada para o dia Y" em linhas seguidas da coluna
    # LEGISLAÇÃO. O registro de dia X mais próximo do aviso é o adiado.
    lg = [(" ".join(w["t"] for w in linha), sum(w["y"] for w in linha) / len(linha))
          for linha in _linhas(leg)]
    for i in range(len(lg) - 1):
        m1 = _RE_ADIADA_1.search(lg[i][0])
        m2 = _RE_ADIADA_2.search(lg[i + 1][0])
        if not (m1 and m2):
            continue
        orig = int(m1.group(1))
        candidatos = [r for r in registros if r["dia"] == orig]
        if not candidatos:
            raise ErroDeFonte("aviso de adiamento para o dia %d sem registro correspondente" % orig)
        alvo = min(candidatos, key=lambda r: abs(r["y"] - lg[i][1]))
        alvo["adiada"] = int(m2.group(1))

    for r in registros:
        r["tipo"] = _junta(r["tipo"])
        r["ev"] = _junta(r["ev"])
        r["data"] = _data(ano, secao["mes"], r["dia"])
    return registros


def _data(ano: int, mes: int, dia_: int) -> datetime.date:
    try:
        return datetime.date(ano, mes, dia_)
    except ValueError:
        raise ErroDeFonte("data inexistente na tabela: %02d/%02d/%d" % (dia_, mes, ano))


def _municipios(nat: str, ev: str) -> List[str]:
    """Nomes de municípios: o que está entre parênteses na NATUREZA; sem parênteses, o nome do
    EVENTO ("Aniversário do Município de Porto Walter")."""
    grupos = re.findall(r"\(([^()]*)\)", nat)
    if not grupos:
        m = re.search(r"Munic[ií]pios? de (.+)$", ev)
        grupos = [m.group(1)] if m else []
    nomes: List[str] = []
    for g in grupos:
        for parte in re.split(r",|\s+e\s+", g):
            limpo = " ".join(parte.split())
            if limpo:
                nomes.append(limpo)
    return nomes


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Saída do `pdftotext -bbox` da portaria -> calendário no formato de modelo.py. Sem rede."""
    palavras = _sem_cabecalho_e_rodape(_palavras(conteudo))
    if not palavras:
        raise ErroDeFonte("o PDF não tem texto (pdftotext não leu palavras)")

    pag1 = " ".join(w["t"] for w in palavras if w["p"] == 1)
    m = re.search(r"ano de (\d{4})", pag1)
    if not m or int(m.group(1)) != ano:
        raise ErroDeFonte("a Portaria não é a do exercício de %d" % ano)

    secoes = _secoes(palavras)
    if len(secoes) != 12:
        raise ErroDeFonte("esperava 12 meses na tabela, achei %d" % len(secoes))

    cal = calendario_vazio("TJAC", ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": EDICOES.get(ano, ""), "descricao": FONTE_DESCRICAO}]
    geral: List[Dict[str, str]] = []
    locais: Dict[str, List[Dict[str, str]]] = {}
    conhecidos = set()

    for secao in secoes:
        for r in _linhas_da_tabela(secao, ano):
            nat = r["nat"]
            municipal = "Municipal" in nat
            if municipal:
                for nome in _municipios(nat, r["ev"]):
                    conhecidos.add(normalizar_local(nome))
            if "facultativ" in r["tipo"].lower():
                continue  # ponto facultativo: fora (ver DUVIDA no topo)
            if r["adiada"] is not None:
                continue  # data adiada: fora (ver DUVIDA no topo)
            if "Feriado" not in r["tipo"]:
                raise ErroDeFonte("TIPO não reconhecido em %s: %r" % (r["data"].isoformat(), r["tipo"]))
            if not r["ev"]:
                raise ErroDeFonte("linha sem evento em %s" % r["data"].isoformat())
            # DUVIDA: "Feriado regimental" (11/08 Dia do Advogado, 08/12 Dia da Justiça) entra como
            # sem_expediente: a tabela cita o Art. 37 §1º IV da LC 221/2010, o mesmo artigo que traz
            # os feriados forenses. Confirmar na revisão.
            if municipal:
                nomes = _municipios(nat, r["ev"])
                if not nomes:
                    raise ErroDeFonte("feriado municipal sem município em %s" % r["data"].isoformat())
                for nome in nomes:
                    chave = normalizar_local(nome)
                    locais.setdefault(chave, []).append(dia(r["data"], "sem_expediente", r["ev"], FONTE_ID))
            elif re.search(r"Nacional|Estadual|Regimental|Forense", nat, re.I) or nat == "":
                geral.append(dia(r["data"], "sem_expediente", r["ev"], FONTE_ID))
            else:
                raise ErroDeFonte("NATUREZA não reconhecida em %s: %r" % (r["data"].isoformat(), nat))

    for chave in conhecidos:
        locais.setdefault(chave, [])
    cal["geral"] = geral
    cal["locais"] = locais
    return ordenar(cal)


PARCIAL = (
    "Lê só a Portaria PRESI nº 6569/2025 (DJe 7.950, 3.2.2026). Ficam de fora: (a) os PONTOS "
    "FACULTATIVOS estaduais (04/06, 06/08, 24/12, 31/12) e municipais (ex.: 18/05, 13/07, 22/08, "
    "08/09, 25/09, 31/10), porque o efeito sobre o prazo não é dito e o ponto municipal depende de "
    "adesão do foro (Art. 2º, parágrafo único); (b) as datas ADIADAS: 20/01 (Dia do Católico, "
    "transferido para 22/01), 28/10 (Dia do Servidor, para 30/10) e 17/11 (Tratado de Petrópolis, "
    "para 19/11): nenhuma das datas entra; (c) o recesso de 20/12 a 20/01, que o ato não traz; "
    "(d) os municípios sem ato citado no documento (não aparecem em locais, exceto os que têm "
    "ponto facultativo); (e) alterações da Portaria publicadas depois, que este motor não lê."
)


class MotorTJAC(Motor):
    sigla = "TJAC"
    precisa_ip_brasil = False  # a ficha registra o teste na nuvem (OK 200): ver docs/fichas/TJAC.md
    parcial = PARCIAL
    esperado = {
        # min_geral e min_locais: lidos na fixture de 23/10/2026 (ver tests/test_tjac.py).
        "min_geral": 1,
        "min_locais": 1,
        # Âncoras da ficha (1 a 3), conferidas à mão no PDF. Os locais (4 e 5) ficam nos testes.
        "ancoras": {
            "2026-01-01": "Confraternização Universal",
            "2026-02-16": "Carnaval",
            "2026-02-18": "Quarta-feira de Cinzas",
            "2026-06-15": "Aniversário do Estado do Acre",
        },
        "exige_recesso": False,  # o ato não traz recesso
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in EDICOES:
            # DUVIDA: a ficha não diz como achar a portaria de 2027. Enquanto não houver regra,
            # o robô só registra o fato.
            raise AindaNaoPublicado("o TJAC ainda não tem calendário de %d conhecido" % ano)
        return interpretar(pdf_para_palavras(rede.baixar(EDICOES[ano])), ano)


MOTOR = MotorTJAC()
