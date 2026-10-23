"""Motor do TJAL (Tribunal de Justiça do Estado de Alagoas). Ficha: docs/fichas/TJAL.md.

Fontes: dois atos normativos do próprio tribunal, baixados da API JSON do portal de
documentos. O ato vem em HTML no campo `texto`.

  - Ato Normativo nº 03/2026 (feriados de 2026): suspensões com compensação de horas.
    Entram como `suspensao_prazo` os arts. 1º (20/04), 2º (05/06), 3º (10/08) e 5º (07/12).
  - Ato Normativo nº 22/2025: suspende 02/01/2026 (`suspensao_prazo`) e fixa o recesso
    de 20/12/2025 a 04/01/2026 (§2º). Entram como `recesso` os dias de 01 a 04/01/2026.

Fora do calendário (cobertura parcial, ver PARCIAL):
  - 28/08 (art. 4º do Ato 03/2026): a suspensão vale só nos municípios que preveem o feriado
    de N. Sra. dos Prazeres, e o ato não diz quais. Não entra em `geral` (valeria para o estado
    inteiro) nem em `locais` (não há lista). DUVIDA: a revisão precisa de decreto municipal.
  - Feriados nacionais e estaduais, feriados municipais e o recesso de 20 a 31/12/2026: estão
    em decretos do Executivo e na Lei 6.564/2005, não nos atos. DUVIDA.
  - Por isso `locais` fica vazio: não há nenhum local conhecido nas fontes lidas.
"""
from __future__ import annotations

import datetime
import html
import json
import re
from typing import Any, Dict

from ..modelo import calendario_vazio, dia, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

URL_ATO_03_2026 = "https://documentos.tjal.jus.br/api/documentos/detalhes/34801"
URL_ATO_22_2025 = "https://documentos.tjal.jus.br/api/documentos/detalhes/34091"
FONTE_ATO_03 = "ato03"
FONTE_ATO_22 = "ato22"

# Só há ato lido para 2026. Para 2027, achar o ato de feriados de 2027 (ver ficha) e trocar aqui.
ANOS_COBERTOS = (2026,)

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Artigos do Ato 03/2026 que entram em `geral`. O art. 4º (28/08, municipal) fica de fora.
ART_MUNICIPAL_03 = 4
MOTIVOS_03 = {
    1: "Feriado de Tiradentes (suspensão com compensação, Ato 03/2026, art. 1º)",
    2: "Feriado de Corpus Christi (suspensão com compensação, Ato 03/2026, art. 2º)",
    3: "Dia do Jurista (suspensão com compensação, Ato 03/2026, art. 3º)",
    5: "Dia da Justiça (suspensão com compensação, Ato 03/2026, art. 5º)",
}
MOTIVO_22_SUSPENSAO = "Dia Mundial da Paz e encerramento do recesso (Ato 22/2025, art. 1º)"
MOTIVO_RECESSO_22 = "Recesso forense (Ato 22/2025, §2º)"

PARCIAL = (
    "Cobertura parcial. Entram só as suspensões e o recesso que os atos do TJAL trazem: "
    "20/04, 05/06, 10/08 e 07/12/2026 (Ato 03/2026), 02/01/2026 e recesso de 01 a 04/01/2026 "
    "(Ato 22/2025). Ficam de fora: (1) 28/08/2026 (Ato 03/2026, art. 4º), suspensão só nos "
    "municípios que preveem o feriado de N. Sra. dos Prazeres, que o ato não identifica; "
    "(2) feriados nacionais e estaduais (Decreto Estadual 106.093/2025), que não são do tribunal; "
    "(3) feriados municipais, que dependem de decreto de cada município (art. 6º do Ato 03/2026); "
    "(4) recesso de fim de ano de 2026 (20 a 31/12), que está na Lei 6.564/2005 e não no ato; "
    "(5) feriados forenses da Lei 6.564/2005 (arts. 36-38). Por isso `locais` fica vazio."
)

_TAG = re.compile(r"<[^>]+>")
_ESPACOS = re.compile(r"\s+")
# Cada artigo começa em "Art. N". O corte é feito antes do marcador, para o texto de cada artigo
# ficar junto. "art. 13" (minúsculo, citação) não casa.
_INICIO_ARTIGO = re.compile(r"(?=Art\.\s*\d+)")
_CABECALHO_ARTIGO = re.compile(r"Art\.\s*(\d+)\s*[ºo°]?\s*(.*)", re.S)
_DATA_SUSPENSAO = re.compile(r"Suspender\b.*?\bno dia\s+(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})", re.I)
_PERIODO_RECESSO = re.compile(
    r"per[ií]odo de (\d{1,2}) de ([a-zç]+) (?:de )?(\d{4}) a (\d{1,2}) de ([a-zç]+) de (\d{4})", re.I)


def _texto_do_ato(texto_html: str) -> str:
    """HTML do ato -> texto corrido, com espaços únicos."""
    return _ESPACOS.sub(" ", html.unescape(_TAG.sub(" ", texto_html))).strip()


def _data_extenso(dd: str, mes: str, aa: str) -> datetime.date:
    numero_mes = MESES.get(mes.lower())
    if numero_mes is None:
        raise ErroDeFonte("mês não reconhecido no ato: %r" % mes)
    return datetime.date(int(aa), numero_mes, int(dd))


def _suspensoes(texto: str) -> Dict[int, datetime.date]:
    """Artigo -> data suspensa, para os artigos que começam por 'Suspender ... no dia'."""
    achados: Dict[int, datetime.date] = {}
    for parte in _INICIO_ARTIGO.split(texto):
        m = _CABECALHO_ARTIGO.match(parte)
        if not m:
            continue
        numero, corpo = int(m.group(1)), m.group(2).strip()
        if not corpo.startswith("Suspender"):
            continue
        d = _DATA_SUSPENSAO.search(corpo)
        if not d:
            raise ErroDeFonte("art. %d suspende, mas a data não está no formato esperado" % numero)
        achados[numero] = _data_extenso(*d.groups())
    return achados


def _texto_de(ato: Dict[str, Any], nome: str) -> str:
    bruto = ato.get("texto")
    if not isinstance(bruto, str) or not bruto.strip():
        raise ErroDeFonte("%s sem o campo 'texto'" % nome)
    return _texto_do_ato(bruto)


def _json(conteudo: bytes, nome: str) -> Dict[str, Any]:
    try:
        dados = json.loads(conteudo.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise ErroDeFonte("%s não é JSON" % nome)
    if not isinstance(dados, dict):
        raise ErroDeFonte("%s não é um documento" % nome)
    return dados


def interpretar(ato03: Dict[str, Any], ato22: Dict[str, Any], ano: int) -> Dict[str, Any]:
    """Os dois atos (JSON já lido) -> calendário no formato de modelo.py. Puro: sem rede.

    Levanta ErroDeFonte se os artigos mudarem em relação ao que foi conferido à mão, ou se
    alguma data cair fora do ano pedido."""
    cal = calendario_vazio("TJAL", ano)
    cal["fontes"] = [
        {"id": FONTE_ATO_03, "url": URL_ATO_03_2026,
         "descricao": "Ato Normativo TJAL nº 03/2026 (feriados de 2026: suspensões com compensação de horas)"},
        {"id": FONTE_ATO_22, "url": URL_ATO_22_2025,
         "descricao": "Ato Normativo TJAL nº 22/2025 (suspensão de 02/01/2026 e recesso de 20/12/2025 a 04/01/2026)"},
    ]

    # Ato 03/2026: tem de ter exatamente os artigos 1 a 5 suspendendo um dia cada.
    suspensoes_03 = _suspensoes(_texto_de(ato03, "Ato 03/2026"))
    if sorted(suspensoes_03) != [1, 2, 3, 4, 5]:
        raise ErroDeFonte("suspensões do Ato 03/2026 mudaram: artigos lidos %s" % sorted(suspensoes_03))
    for artigo, data in sorted(suspensoes_03.items()):
        if data.year != ano:
            raise ErroDeFonte("Ato 03/2026 traz data de %d, não de %d" % (data.year, ano))
        if artigo == ART_MUNICIPAL_03:
            # DUVIDA: suspensão só nos municípios que preveem o feriado; o ato não lista quais.
            continue
        cal["geral"].append(dia(data, "suspensao_prazo", MOTIVOS_03[artigo], FONTE_ATO_03))

    # Ato 22/2025: suspende 02/01 (art. 1º) e fixa o período de recesso (§2º).
    texto_22 = _texto_de(ato22, "Ato 22/2025")
    suspensoes_22 = _suspensoes(texto_22)
    if sorted(suspensoes_22) != [1]:
        raise ErroDeFonte("suspensões do Ato 22/2025 mudaram: artigos lidos %s" % sorted(suspensoes_22))
    data_22 = suspensoes_22[1]
    if data_22.year != ano:
        raise ErroDeFonte("Ato 22/2025 traz data de %d, não de %d" % (data_22.year, ano))
    cal["geral"].append(dia(data_22, "suspensao_prazo", MOTIVO_22_SUSPENSAO, FONTE_ATO_22))

    m = _PERIODO_RECESSO.search(texto_22)
    if not m:
        raise ErroDeFonte("não achei o período de recesso no Ato 22/2025 (§2º)")
    ini = _data_extenso(m.group(1), m.group(2), m.group(3))
    fim = _data_extenso(m.group(4), m.group(5), m.group(6))
    for n in range((fim - ini).days + 1):
        d = ini + datetime.timedelta(days=n)
        if d.year == ano:
            cal["geral"].append(dia(d, "recesso", MOTIVO_RECESSO_22, FONTE_ATO_22))

    # Nenhum local é conhecido: as fontes não trazem lista de municípios. `locais` fica vazio.
    cal["locais"] = {}
    return ordenar(cal)


class MotorTJAL(Motor):
    sigla = "TJAL"
    precisa_ip_brasil = False  # os dois JSON abriram da nuvem (200), ver docs/fichas/TJAL.md
    parcial = PARCIAL
    esperado = {
        # Lido nos atos: 4 suspensões do Ato 03/2026 (sem 28/08), 1 suspensão do Ato 22/2025 e
        # 4 dias de recesso (01 a 04/01/2026). Piso = o lido.
        "min_geral": 9,
        # Nenhum local conhecido nas fontes.
        "min_locais": 0,
        # Conferidas à mão nos atos (ficha, âncoras 1, 2, 3, 5 e a de 02/01 do Ato 22/2025).
        # A âncora 4 (28/08) fica fora de `geral` de propósito (ver docstring do módulo).
        "ancoras": {
            "2026-01-02": "Encerramento do recesso (Ato 22/2025)",
            "2026-04-20": "Tiradentes (Ato 03/2026, art. 1º)",
            "2026-06-05": "Corpus Christi (Ato 03/2026, art. 2º)",
            "2026-08-10": "Dia do Jurista (Ato 03/2026, art. 3º)",
            "2026-12-07": "Dia da Justiça (Ato 03/2026, art. 5º)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in ANOS_COBERTOS:
            raise AindaNaoPublicado("o TJAL ainda não publicou ato de feriados de %d" % ano)
        ato03 = _json(rede.baixar(URL_ATO_03_2026), "Ato 03/2026")
        ato22 = _json(rede.baixar(URL_ATO_22_2025), "Ato 22/2025")
        return interpretar(ato03, ato22, ano)


MOTOR = MotorTJAL()
