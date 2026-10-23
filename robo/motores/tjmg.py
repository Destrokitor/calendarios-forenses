"""Motor do TJMG (Tribunal de Justiça de Minas Gerais). Ficha: docs/fichas/TJMG.md.

Fonte única: o PDF compilado da Portaria Conjunta 1.798/PR/2026, com as alterações 1.814, 1.828 e
1.860 (www8.tjmg.jus.br), lido com `pdftotext -layout`. Duas partes:

  - Arts. 1º a 4º, em texto corrido: feriados do Judiciário mineiro (vale para o estado inteiro,
    `geral`), feriados municipais de Belo Horizonte (art. 2º) e a regra do dia 5/6 (art. 3º, § 1º);
  - ANEXO ÚNICO: tabela "Comarca x Feriados Municipais" das comarcas do interior (`locais`).

O PDF repete o ANEXO ÚNICO 4 vezes (a versão da Port. 1.860 primeiro, depois 1.828, 1.814 e a
original). Vale só o PRIMEIRO, que é o vigente; os outros são histórico e são ignorados.

Na tabela, o nome da comarca fica na coluna da esquerda, às vezes quebrado em 2 linhas ("Visconde do
Rio" / "Branco") e a linha com o nome nem sempre é a do item. Os itens são "I - 3 de abril: Paixão
de Cristo;", também quebrados em 2 linhas. Uma comarca começa em cada item "I -".
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

# PDF de cada ano. O número da portaria muda a cada ano (1798 é a de 2026), então o endereço de 2027
# vai ser outro: ver docs/fichas/TJMG.md. Ano que não está aqui levanta AindaNaoPublicado.
PORTARIAS: Dict[int, str] = {
    2026: "https://www8.tjmg.jus.br/institucional/at/pdf/pc17982026.pdf",
}
FONTE_ID = "portaria"

PARCIAL = (
    "Feriados municipais das comarcas do interior só até o que o Anexo Único da portaria lista: "
    "o Diretor do Foro de cada comarca ainda pode complementar com portaria local (Resolução da "
    "Corte Superior 458/2004, art. 6º), e essas portarias avulsas não são lidas. Também ficam de "
    "fora suspensões de expediente por portaria posterior à compilação (ex.: jogos da Copa) e a "
    "consulta 'Feriados Locais' do Guia Judiciário (por comarca). Só vale o primeiro Anexo Único "
    "do PDF (Port. 1.860); se sair nova alteração, o PDF compilado precisa ser relido."
)

_MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
          "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
_MES_RE = "|".join(_MESES)
_ITEM_ROMANO = re.compile(r"^([IVXL]+)\s+-\s+(.*)$")
_ITEM_DATA = re.compile(r"^(\d[^:]*?)\s+de\s+(%s)\s*:\s*(.*)$" % _MES_RE, re.I)


def pdf_para_texto(pdf: bytes) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=180)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _limpa(texto: str) -> str:
    return " ".join(texto.replace("“", "").replace("”", "").replace('"', "").split())


def _datas(expr: str, mes: str, ano: int) -> List[datetime.date]:
    """'16, 17 e 18' / '1º a 6' / '2 e 3' + mês -> datas. 'a' é intervalo; ',' e 'e' listam."""
    m = _MESES[mes.lower()]
    numeros = [int(n) for n in re.findall(r"\d+", expr)]
    separadores = re.findall(r"\d+º?\s*(,|e|a)\s*(?=\d)", expr)
    if not numeros or len(separadores) != len(numeros) - 1:
        raise ErroDeFonte("expressão de dias não reconhecida: %r" % expr)
    dias: List[int] = []
    for i, n in enumerate(numeros):
        if i > 0 and separadores[i - 1] == "a":
            dias.extend(range(dias[-1] + 1, n + 1))
        else:
            dias.append(n)
    try:
        return [datetime.date(ano, m, d) for d in dias]
    except ValueError:
        raise ErroDeFonte("data inexistente em %r de %s" % (expr, mes))


def _itens_do_artigo(artigo: str) -> List[Tuple[str, str, str]]:
    """(dias, mês, motivo) de cada item 'I - 16, 17 e 18 de fevereiro: Carnaval;' do artigo."""
    plano = _limpa(artigo)
    partes = re.split(r"(?:(?<=[;:.])|^)\s*(?=[IVXL]+ - \d)", plano)
    saida: List[Tuple[str, str, str]] = []
    for p in partes:
        m = _ITEM_ROMANO.match(p.strip())
        if not m:
            continue
        d = _ITEM_DATA.match(m.group(2).strip())
        if not d:
            continue
        motivo = d.group(3).strip()
        # o último item termina em '.', seguido do parágrafo único: corta no primeiro ponto final
        motivo = re.split(r"\.\s+(?:Parágrafo|Art\.)", motivo)[0].rstrip(";. ").strip()
        saida.append((d.group(1), d.group(2), motivo))
    return saida


def _artigo(plano: str, n: int, proximo: Optional[str]) -> str:
    ini = re.search(r"Art\.\s*%dº\s" % n, plano)
    if not ini:
        raise ErroDeFonte("não achei o art. %dº da portaria" % n)
    fim = re.search(r"Art\.\s*%s" % proximo, plano[ini.end():]) if proximo else None
    return plano[ini.end(): ini.end() + fim.start()] if fim else plano[ini.end():]


def _parte_anexo(texto: str) -> Tuple[str, str]:
    """(corpo, primeiro Anexo Único). Os outros 3 Anexos (históricos) ficam de fora."""
    i = texto.find("ANEXO ÚNICO")
    if i < 0:
        raise ErroDeFonte("não achei o ANEXO ÚNICO na portaria")
    corpo = texto[:i]
    # O ANEXO ÚNICO aparece 2 vezes seguidas no mesmo bloco (título da alteração e título original,
    # entre aspas). O bloco acaba na legenda '(Nova redação dada pela ...)' do Anexo seguinte.
    k = texto.find("\n(Nova redação", i)
    resto = texto[i:k] if k > 0 else texto[i:]
    return corpo, resto


def comarcas_do_anexo(anexo: str) -> Dict[str, List[Tuple[str, str]]]:
    """Primeiro Anexo -> {comarca: [(data como 'D de mês', motivo)]}. Mantém a ordem do PDF."""
    comarcas: List[Dict[str, Any]] = []
    atual: Optional[Dict[str, Any]] = None
    for pagina in anexo.split("\f"):
        linhas = [ln.rstrip() for ln in pagina.splitlines() if ln.strip()]
        ini = next((n for n, ln in enumerate(linhas)
                    if re.search(r"(^|\s{2,})[IVXL]+ - \d", ln)), None)
        if ini is None:
            continue
        linhas = linhas[ini:]
        recuo = lambda ln: len(ln) - len(ln.lstrip())  # noqa: E731
        base = min(recuo(ln) for ln in linhas)  # coluna dos nomes de comarca nesta página
        for ln in linhas:
            fragmento: Optional[str] = None
            texto_item: Optional[str] = None
            if recuo(ln) - base < 8:  # coluna da esquerda: nome (e talvez o item na mesma linha)
                partes = re.split(r"\s{2,}", ln.strip(), maxsplit=1)
                if len(partes) == 1:  # nome comprido: só um espaço antes do item ("... CLARO  III - 16")
                    colado = re.match(r"^(.*?\S)\s+([IVXL]+ - \d.*)$", partes[0])
                    if colado:
                        partes = [colado.group(1), colado.group(2)]
                if len(partes) == 1 and _ITEM_ROMANO.match(partes[0]):
                    texto_item = partes[0]
                else:
                    fragmento = partes[0].strip()
                    texto_item = partes[1].strip() if len(partes) > 1 else None
            else:
                texto_item = ln.strip()
            m = _ITEM_ROMANO.match(texto_item) if texto_item else None
            if m and m.group(1) == "I" and (atual is None or atual["itens"]):
                atual = {"nome": [], "itens": []}  # o 'I' abre a comarca seguinte
                comarcas.append(atual)
            if fragmento is not None:
                if atual is None:
                    atual = {"nome": [], "itens": []}
                    comarcas.append(atual)
                atual["nome"].append(fragmento)
            if texto_item is None:
                continue
            if atual is None:
                raise ErroDeFonte("item do Anexo sem comarca: %r" % texto_item)
            if m:
                atual["itens"].append(m.group(2).strip())
            else:
                if not atual["itens"]:
                    raise ErroDeFonte("continuação de item sem item: %r" % texto_item)
                atual["itens"][-1] += " " + texto_item
    saida: Dict[str, List[Tuple[str, str]]] = {}
    for c in comarcas:
        nome = normalizar_local(" ".join(c["nome"]))
        if not nome or not c["itens"]:
            raise ErroDeFonte("comarca mal lida no Anexo: %r" % c)
        if nome in saida:
            raise ErroDeFonte("comarca repetida no Anexo: %s" % nome)
        saida[nome] = [(i, "") for i in c["itens"]]  # texto cru; datas lidas em interpretar()
    return saida


def _dias_de_item(texto: str, ano: int) -> Tuple[List[datetime.date], str]:
    """'2 e 3 de maio: Festa da Padroeira' -> (datas, motivo)."""
    m = _ITEM_DATA.match(_limpa(texto))
    if not m:
        raise ErroDeFonte("item do Anexo não reconhecido: %r" % texto)
    motivo = m.group(3).rstrip(";. ").strip()
    if not motivo:
        raise ErroDeFonte("feriado sem motivo: %r" % texto)
    return _datas(m.group(1), m.group(2), ano), motivo


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do `pdftotext -layout` da portaria -> calendário no formato de modelo.py.

    Puro: não faz rede. Levanta ErroDeFonte se o texto não for o de `ano` ou faltar parte."""
    corpo, anexo = _parte_anexo(conteudo)
    plano = _limpa(corpo)
    achou = re.search(r"no ano de (\d{4}), fica suspenso", plano)
    if not achou or int(achou.group(1)) != ano:
        raise ErroDeFonte("a portaria não é a de %d (achei %s)" % (ano, achou.group(1) if achou else "nada"))

    cal = calendario_vazio("TJMG", ano)
    cal["fontes"] = [{
        "id": FONTE_ID, "url": PORTARIAS.get(ano, ""),
        "descricao": "Portaria Conjunta 1.798/PR/2026 compilada (alterações 1.814, 1.828 e 1.860): "
                     "feriados do Judiciário mineiro, Belo Horizonte e Anexo Único das comarcas",
    }]

    # Art. 1º: feriados nacionais, estaduais e da Justiça (estado inteiro).
    art1 = _artigo(plano, 1, "2º")
    itens1 = _itens_do_artigo(art1)
    if len(itens1) < 10:
        raise ErroDeFonte("art. 1º lido pela metade (%d itens)" % len(itens1))
    for expr, mes, motivo in itens1:
        tipo = "recesso" if motivo.lower().startswith("feriado forense") else "sem_expediente"
        for d in _datas(expr, mes, ano):
            cal["geral"].append(dia(d, tipo, motivo, FONTE_ID))

    # DUVIDA: 20/04 e 07/12 (parágrafo único do art. 1º): "não haverá expediente forense", sem
    # ser feriado. Tratado como sem_expediente (o art. 4º prorroga os prazos que vencem nos dias
    # dos arts. 1º a 3º); a ficha marca a dúvida (pontes: expediente x prazo). Quem revisa decide.
    unico = re.search(r"Parágrafo único\. Não haverá expediente forense nos dias (.*?) de %d" % ano, art1)
    if unico:
        for n, mes in re.findall(r"(\d+)º?\s+de\s+(%s)" % _MES_RE, unico.group(1)):
            for d in _datas(n, mes, ano):
                cal["geral"].append(dia(d, "sem_expediente", "Sem expediente forense (art. 1º, parágrafo único)", FONTE_ID))

    # Art. 4º, parágrafo único: prazos suspensos de 7 a 20/01 (LC 59/2001, art. 313, § 8º).
    susp = re.search(r"suspensos os prazos processuais no período compreendido entre os dias (\d+) e (\d+) de (%s) de %d"
                     % (_MES_RE, ano), plano)
    if susp:
        for d in _datas("%s a %s" % (susp.group(1), susp.group(2)), susp.group(3), ano):
            cal["geral"].append(dia(d, "suspensao_prazo",
                                    "Prazos processuais suspensos (art. 4º, parágrafo único; LC 59/2001, art. 313, § 8º)",
                                    FONTE_ID))

    # Art. 2º: Belo Horizonte.
    art2 = _artigo(plano, 2, "3º")
    bh: List[Dict[str, str]] = []
    itens2 = _itens_do_artigo(art2)
    if not itens2:
        raise ErroDeFonte("art. 2º (Belo Horizonte) sem itens")
    for expr, mes, motivo in itens2:
        for d in _datas(expr, mes, ano):
            bh.append(dia(d, "sem_expediente", motivo, FONTE_ID))
    ponte = re.search(r"Não haverá expediente forense na Comarca de Belo Horizonte no dia (\d+)º? de (%s)" % _MES_RE, art2)
    if ponte:
        bh.append(dia(_datas(ponte.group(1), ponte.group(2), ano)[0], "sem_expediente",
                      "Sem expediente forense (art. 2º, parágrafo único)", FONTE_ID))
    cal["locais"]["BELO HORIZONTE"] = bh

    # Anexo Único: comarcas do interior. Art. 3º, § 1º: 5/6 sem expediente onde 4/6 é Corpus Christi.
    comarcas = comarcas_do_anexo(anexo)
    if len(comarcas) < 250:
        raise ErroDeFonte("Anexo lido pela metade (%d comarcas)" % len(comarcas))
    ponte_cc = re.search(r"no dia (\d+)º? de (%s) de %d nas comarcas em que o dia de Corpus Christi" % (_MES_RE, ano),
                         _limpa(_artigo(plano, 3, "4º")))
    for nome, itens in comarcas.items():
        lista: List[Dict[str, str]] = []
        corpus = False
        for texto, _ in itens:
            datas, motivo = _dias_de_item(texto, ano)
            for d in datas:
                lista.append(dia(d, "sem_expediente", motivo, FONTE_ID))
            if "corpus christi" in motivo.lower():
                corpus = True
        if corpus and ponte_cc:
            lista.append(dia(_datas(ponte_cc.group(1), ponte_cc.group(2), ano)[0], "sem_expediente",
                             "Sem expediente forense (art. 3º, § 1º): Corpus Christi é feriado municipal", FONTE_ID))
        cal["locais"][nome] = lista
    return cal


class MotorTJMG(Motor):
    sigla = "TJMG"
    precisa_ip_brasil = False  # ficha: o PDF abriu na nuvem (GitHub Actions, 23/10/2026)
    parcial = PARCIAL
    esperado = {
        # A ficha não traz contagem. Lido na fixture de 23/10/2026: 51 dias gerais (art. 1º: 13
        # feriados + 6 de recesso de janeiro + 12 de recesso de dezembro + 3 de Carnaval etc., mais
        # 20/04 e 07/12 do parágrafo único e 14 de suspensão de prazo, 7 a 20/01) e 298 locais
        # (297 comarcas do Anexo + Belo Horizonte). Piso = o lido.
        "min_geral": 51,
        "min_locais": 298,
        # Ficha: âncoras 1 a 3 (geral); 4 e 5 são de local e ficam nos testes.
        "ancoras": {
            "2026-02-16": "Segunda-feira de Carnaval",
            "2026-02-17": "Terça-feira de Carnaval",
            "2026-02-18": "Quarta-feira de Cinzas",
            "2026-10-30": "Dia do Funcionário Público",
            "2026-12-20": "Feriado Forense (recesso)",
            "2026-12-31": "Feriado Forense (recesso)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in PORTARIAS:
            raise AindaNaoPublicado("o TJMG ainda não publicou a portaria de feriados de %d" % ano)
        return interpretar(pdf_para_texto(rede.baixar(PORTARIAS[ano])), ano)


MOTOR = MotorTJMG()
