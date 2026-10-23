"""Motor do TJBA (Tribunal de Justiça do Estado da Bahia) - COBERTURA PARCIAL.

Fonte (ficha: docs/fichas/TJBA.md): Decreto Judiciário nº 1050, de 04/12/2025, DJe nº 3.944, de
05/12/2025, pp. 6-8 (PDF com texto; a página do DJe traz outros atos, por isso o motor recorta só
o decreto 1050). Lê:
  - art. 2º: recesso (20/12/2025 a 06/01/2026) -> `recesso`; só os dias do ano pedido entram;
  - art. 4º: 07 a 20/01/2026, prazos suspensos e expediente normal -> `suspensao_prazo`;
  - art. 5º: feriados e pontos facultativos (incisos com datas) -> `sem_expediente`.
Um dia pode ter dois registros (01 e 02/01: feriado + recesso).

Feriados municipais (Decreto Judiciário nº 09/2026 e alterações) NÃO são lidos: ver `parcial`.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_URL = "https://www.tjba.jus.br/portal/wp-content/uploads/2025/12/Decreto-1050-25_-expediente-forense-2026.pdf"
FONTE_ID = "decreto"
FONTE_DESCRICAO = "Decreto Judiciário nº 1050, de 04/12/2025 (expediente forense 2026), DJe nº 3.944, de 05/12/2025, pp. 6-8"

# Ano de exercício que cada decreto cobre. A ficha só conhece o de 2026.
EDICOES: Dict[int, str] = {2026: FONTE_URL}

# DUVIDA: a ficha não indica a lista de comarcas (anexo do Decreto 09/2026 deu 503). Chave única.
LOCAL_UNICO = "SALVADOR"

MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
_MES = "(" + "|".join(MESES) + ")"


def pdf_para_texto(pdf: bytes) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _decreto(texto: str, ano: int) -> str:
    """Texto do decreto 1050 numa linha só (sem rodapés do DJe nem hifenização de quebra)."""
    m = re.search(r"DECRETO JUDICI[ÁA]RIO N[ºO°] 1050\b", texto)
    if not m:
        raise ErroDeFonte("não achei o Decreto Judiciário nº 1050 no texto")
    fim = re.search(r"DECRETO JUDICI[ÁA]RIO N[ºO°] 10(?!50)\d\d\b", texto[m.end():])
    corpo = texto[m.start(): m.end() + fim.start()] if fim else texto[m.start():]
    corpo = re.sub(r"TJBA - DI[ÁA]RIO DA JUSTI[ÇC]A ELETR[ÔO]NICO[^\n]*", " ", corpo)
    corpo = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", corpo)   # "proces-\nsuais"
    corpo = " ".join(corpo.replace("ﬁ", "fi").split())
    if not re.search(r"exerc[íi]cio de %d\b" % ano, corpo):
        raise ErroDeFonte("o Decreto 1050 não é o do exercício de %d" % ano)
    return corpo


def _artigo(corpo: str, inicio: str, fim: str) -> str:
    m = re.search(inicio + r"(.*?)" + fim, corpo)
    if not m:
        raise ErroDeFonte("não achei o trecho %r do decreto" % inicio)
    return m.group(1)


def _intervalo(d1: datetime.date, d2: datetime.date) -> List[datetime.date]:
    return [d1 + datetime.timedelta(days=k) for k in range((d2 - d1).days + 1)]


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do DJe (pdftotext) -> calendário no formato de modelo.py. Sem rede."""
    corpo = _decreto(conteudo, ano)
    cal = calendario_vazio(MotorTJBA.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]
    cal["locais"] = {normalizar_local(LOCAL_UNICO): []}

    # Art. 2º: recesso "entre os dias 20 de dezembro de 2025 e 6 de janeiro de 2026".
    t2 = _artigo(corpo, r"Art\. 2º", r"Art\. 3º")
    m = re.search(r"entre os dias (\d+) de %s de (\d{4}) e (\d+) de %s de (\d{4})" % (_MES, _MES), t2)
    if not m:
        raise ErroDeFonte("não achei o período do recesso no art. 2º")
    ini = datetime.date(int(m.group(3)), MESES[m.group(2)], int(m.group(1)))
    fim = datetime.date(int(m.group(6)), MESES[m.group(5)], int(m.group(4)))
    for d in _intervalo(ini, fim):
        if d.year == ano:
            cal["geral"].append(dia(d, "recesso", "Recesso judiciário (art. 2º)", FONTE_ID))

    # Art. 4º: "entre os dias 7 e 20 de janeiro de 2026": prazos suspensos, expediente normal.
    t4 = _artigo(corpo, r"Art\. 4º", r"DOS FERIADOS")
    m = re.search(r"entre os dias (\d+) e (\d+) de %s de (\d{4})" % _MES, t4)
    if not m:
        raise ErroDeFonte("não achei o período do art. 4º")
    mes, a = MESES[m.group(3)], int(m.group(4))
    # DUVIDA: o art. 4º ressalva réus presos, Lei Maria da Penha e medidas urgentes (art. 798-A
    # CPP); como suspensao_prazo vale a regra geral (CPC art. 220), sem tratar essas exceções penais.
    for d in _intervalo(datetime.date(a, mes, int(m.group(1))), datetime.date(a, mes, int(m.group(2)))):
        if d.year == ano:
            cal["geral"].append(dia(d, "suspensao_prazo",
                                    "Prazos suspensos de 7 a 20/01, expediente normal (art. 4º)", FONTE_ID))

    # Art. 5º: incisos "II - 12, 13, 16, 17 e 18 de fevereiro: Carnaval e Quarta-feira de Cinzas;".
    t5 = _artigo(corpo, r"Art\. 5º", r"Art\. 6º").strip()
    n = 0
    # DUVIDA: o decreto junta "feriados ou pontos facultativos" sem distinguir e diz que não há
    # expediente forense nem administrativo; tratado todo como sem_expediente (art. 8º prorroga prazo).
    for m in re.finditer(r"\b[IVXL]+ - ([\d\sº,e]+?) de %s: (.*?)(?:;|\.(?= Art\.)|\.$)" % _MES, t5):
        mes = MESES[m.group(2)]
        motivo = m.group(3).strip()
        dias = [int(x) for x in re.findall(r"\d+", m.group(1))]
        for numero in dias:
            cal["geral"].append(dia(datetime.date(ano, mes, numero), "sem_expediente", motivo, FONTE_ID))
        n += 1
    if n != 15:
        raise ErroDeFonte("esperava 15 incisos no art. 5º e li %d" % n)
    return ordenar(cal)


class MotorTJBA(Motor):
    sigla = "TJBA"
    precisa_ip_brasil = False  # PDF do portal abriu na nuvem (ficha)
    parcial = (
        "Lê só o Decreto Judiciário nº 1050/2025 (calendário geral). Ficam de fora os feriados "
        "municipais por comarca (Decreto Judiciário nº 09/2026, ~193 comarcas, e decretos que o "
        "alteram, como o nº 144/2026 - Sapeaçu, 27/04): o anexo está em www7.tjba.jus.br, que deu "
        "503. `locais` tem só a chave SALVADOR, vazia, como marcador, não a lista de comarcas. "
        "Também não entram alterações posteriores do decreto (art. 9º) nem o recesso de "
        "20 a 31/12/2026 (virá no decreto de 2027)."
    )
    esperado = {
        "min_geral": 30,  # a ficha não traz contagem; lidos: 6 recesso + 14 suspensão + 28 feriados
        "min_locais": 1,
        "ancoras": {
            "2026-02-12": "Carnaval (inciso II)",
            "2026-02-18": "Quarta-feira de Cinzas (inciso II)",
            "2026-04-03": "Sexta-feira Santa (inciso III)",
            "2026-06-24": "São João (inciso VII)",
            "2026-07-02": "Independência da Bahia (inciso VIII)",
            "2026-12-08": "Dia da Justiça (inciso XV)",
            "2026-01-06": "Fim do recesso (art. 2º)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in EDICOES:
            # DUVIDA: o decreto de 2027 sai em dezembro, com número e endereço novos; a ficha não
            # traz regra para localizá-lo.
            raise AindaNaoPublicado("o decreto do expediente forense de %d ainda não é conhecido" % ano)
        return interpretar(pdf_para_texto(rede.baixar(EDICOES[ano])), ano)


MOTOR = MotorTJBA()
