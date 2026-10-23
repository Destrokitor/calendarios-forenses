"""Motor do TJPE (Tribunal de Justiça de Pernambuco). Ficha: docs/fichas/TJPE.md.

Fonte única, oficial (ficha: docs/fichas/TJPE.md):

  Ato Conjunto nº 43, de 13/10/2025 (Presidência e Corregedoria-Geral), publicado no DJe
  Edição 304/2025, de 14/10/2025: calendário dos feriados forenses de 2026. PDF com camada de
  texto, lido com `pdftotext -layout`.

Abrangência:
  - Art. 1º, incisos I a XXI (feriados do Poder Judiciário estadual) -> `geral`, tipo
    sem_expediente. São 21 datas.
  - Art. 1º, parágrafo único (dias de recesso por dias soltos: 02 a 06/01; 23 e 25 a 30/06;
    20 a 24 e 26 a 31/12) -> `geral`, tipo recesso. O Natal (25/12) já está no inciso XXI e
    não se repete aqui.
  - Art. 2º (16/07, Nossa Senhora do Carmo, feriado municipal do Recife) -> `locais["RECIFE"]`,
    tipo sem_expediente. É o único local nominal do ato.

Fora do motor:
  - Art. 3º (13/02): expediente normal, com trabalho remoto em prédios específicos. Não há
    dia sem expediente, então não entra.
  - Art. 4º: os feriados municipais das comarcas do interior dependem de lei municipal e o
    ato não traz lista. Não entram (ver `parcial`).
  - Art. 5º (plantão judiciário) e Art. 6º (alterações do calendário): não geram dia.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_URL = "https://portal.tjpe.jus.br/documents/d/portal/feriados-2026-pdf"
FONTE_ID = "ato-conjunto-43"
FONTE_DESCRICAO = ("Ato Conjunto nº 43, de 13/10/2025 (Presidência e Corregedoria-Geral do TJPE), "
                   "DJe Edição 304/2025, de 14/10/2025: calendário de feriados forenses de 2026")

# Endereço do ato de cada ano. Só o de 2026 é conhecido. O ato do calendário de 2027 já saiu
# (ficha, em 09/2026), mas o endereço dele não foi achado (sem acesso à internet ao escrever
# este motor). DUVIDA: sem o endereço, 2027 levanta AindaNaoPublicado até alguém registrar o link.
EDICOES: Dict[int, str] = {2026: FONTE_URL}

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Inciso do Art. 1º: "II – 16 de fevereiro, segunda-feira – Carnaval". A data pode vir com "º"
# ("1º de janeiro") e o motivo vai até o início do inciso seguinte ou o fim do artigo.
_RE_INCISO = re.compile(
    r"(?:^|\s)([IVXL]+) – (\d{1,2})º? de ([a-zç]+), [^–]+– (.+?)(?=\s[IVXL]+ – \d|$)")
# "os dias 02, 03, 04, 05 e 06 de janeiro/2026"
_RE_PARAGRAFO = re.compile(r"os dias ([\d,\se]+?) de ([a-zç]+)/(\d{4})")
# "no dia 16 de julho de 2026, quinta-feira – Dia de Nossa Senhora do Carmo (feriado municipal)"
_RE_RECIFE = re.compile(
    r"no dia (\d{1,2}) de ([a-zç]+) de (\d{4}), [^–]+– (.+?)\s*\(feriado municipal\)")

PARCIAL = (
    "Lê só o Ato Conjunto nº 43/2025 (DJe 304/2025). Ficam de fora: (1) os feriados municipais "
    "das comarcas do interior, que o Art. 4º manda seguir pela lei de cada município, sem lista "
    "no ato (são cerca de cem municípios, e só Recife aparece nominal, com 16/07); (2) "
    "alterações posteriores do calendário, como prevê o Art. 6º, e portarias ou atos avulsos "
    "publicados em outras edições do DJe (não verificado); (3) o calendário de 2027, cujo "
    "endereço não está registrado (ver EDICOES). O motor não tem atributo de local para os "
    "municípios do interior: o app só mostra Recife na lista de comarcas."
)


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto com layout, via pdftotext."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _texto_limpo(conteudo: str) -> str:
    """Uma linha só, sem cabeçalho de edição do DJe nem número de página (que cairiam no meio
    do texto dos incisos)."""
    linhas = []
    for linha in conteudo.splitlines():
        limpa = " ".join(linha.split())
        if not limpa or "Edição nº" in limpa or re.fullmatch(r"\d{1,3}", limpa):
            continue
        linhas.append(limpa)
    return " ".join(linhas)


def _mes(nome: str) -> int:
    if nome not in MESES:
        raise ErroDeFonte("mês não reconhecido no ato: %r" % nome)
    return MESES[nome]


def _trecho(texto: str, inicio: str, fim: str) -> str:
    a = texto.find(inicio)
    if a == -1:
        raise ErroDeFonte("não achei %r no ato" % inicio)
    b = texto.find(fim, a + len(inicio))
    if b == -1:
        raise ErroDeFonte("não achei %r depois de %r" % (fim, inicio))
    return texto[a:b]


def _motivo(texto: str) -> str:
    limpo = " ".join(texto.split()).rstrip(" ;.")
    # Incisos XIII e XVI começam com "em razão do ..." no ato; o prefixo sai do motivo.
    return re.sub(r"^em razão d[oa] ", "", limpo)


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do ato (pdftotext -layout) -> calendário no formato de modelo.py. Sem rede."""
    texto = _texto_limpo(conteudo)
    if "ATO CONJUNTO Nº 43" not in texto:
        raise ErroDeFonte("o texto não é o Ato Conjunto nº 43 do TJPE")
    if not re.search(r"no ano de %d\b" % ano, texto):
        raise ErroDeFonte("o ato não é o calendário de %d" % ano)

    cal = calendario_vazio(MotorTJPE.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]

    # Art. 1º, incisos: 21 feriados. Cada um vira uma data em `geral`.
    incisos = _trecho(texto, "Art. 1º Determinar", "Parágrafo único.")
    achados = list(_RE_INCISO.finditer(incisos))
    if len(achados) != 21:
        raise ErroDeFonte("esperava 21 incisos no Art. 1º e achei %d" % len(achados))
    for n, m in enumerate(achados, 1):
        if m.group(1) != _romano(n):
            raise ErroDeFonte("incisos fora de ordem: esperava %s e achei %s" % (_romano(n), m.group(1)))
        data = datetime.date(ano, _mes(m.group(3)), int(m.group(2)))
        cal["geral"].append(dia(data, "sem_expediente", _motivo(m.group(4)), FONTE_ID))

    # Art. 1º, parágrafo único: recesso por dias soltos.
    # DUVIDA: o texto diz que esses dias "serão feriados" (com base no art. 94 do COJE), mas a
    # ficha os classifica como recesso forense. Seguido a ficha. O efeito sobre prazo (suspensão
    # ou não) fica para a revisão.
    paragrafo = _trecho(texto, "Parágrafo único.", "Art. 2º")
    segmentos = _RE_PARAGRAFO.findall(paragrafo)
    if len(segmentos) != 3:
        raise ErroDeFonte("esperava 3 trechos de recesso no parágrafo único e achei %d" % len(segmentos))
    for dias_txt, mes_nome, ano_txt in segmentos:
        if int(ano_txt) != ano:
            raise ErroDeFonte("recesso do parágrafo único é de %s, não de %d" % (ano_txt, ano))
        mes = _mes(mes_nome)
        for d in re.findall(r"\d{1,2}", dias_txt):
            data = datetime.date(ano, mes, int(d))
            cal["geral"].append(dia(data, "recesso", "Recesso forense (Art. 1º, parágrafo único)", FONTE_ID))

    # Art. 2º: feriado municipal do Recife, só para a Comarca do Recife.
    # Art. 3º (13/02): expediente normal, sem dia sem expediente. Fica fora de propósito.
    art2 = _trecho(texto, "Art. 2º", "Art. 3º")
    m = _RE_RECIFE.search(art2)
    if not m:
        raise ErroDeFonte("não achei o feriado municipal do Recife no Art. 2º")
    if int(m.group(3)) != ano:
        raise ErroDeFonte("feriado do Recife é de %s, não de %d" % (m.group(3), ano))
    data_recife = datetime.date(ano, _mes(m.group(2)), int(m.group(1)))
    motivo_recife = "%s (feriado municipal)" % _motivo(m.group(4))
    cal["locais"] = {normalizar_local("Recife"): [dia(data_recife, "sem_expediente", motivo_recife, FONTE_ID)]}

    return ordenar(cal)


def _romano(n: int) -> str:
    valores = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in valores:
        while n >= v:
            out += s
            n -= v
    return out


class MotorTJPE(Motor):
    sigla = "TJPE"
    precisa_ip_brasil = False  # PDF abriu na nuvem (run de 24/10: OK 200, application/pdf)
    parcial = PARCIAL
    esperado = {
        # A ficha não traz contagem. Lido no ato: 21 feriados + 23 dias de recesso = 44 gerais.
        "min_geral": 44,
        # Só Recife é nominal no ato (ficha). Piso = o lido.
        "min_locais": 1,
        # Conferidas à mão no ato (ficha, âncoras 1 a 5), todas em `geral`:
        "ancoras": {
            "2026-03-06": "Data Magna de Pernambuco (Art. 1º, inciso V)",
            "2026-06-22": "Corpus Christi, transferido de 04/06 (Art. 1º, inciso XI)",
            "2026-10-30": "Dia do Servidor Público, transferido de 28/10 (Art. 1º, inciso XVI)",
            "2026-12-20": "Recesso, início (Art. 1º, parágrafo único)",
            "2026-12-31": "Recesso, fim (Art. 1º, parágrafo único)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in EDICOES:
            # DUVIDA: o ato de 2027 já saiu (ficha), mas o endereço não está registrado. Até lá, o
            # robô só registra o fato e tenta de novo no dia seguinte.
            raise AindaNaoPublicado(
                "o TJPE não tem endereço registrado para o calendário de %d; o ato de 2026 "
                "(DJe 304/2025) é o único conhecido" % ano)
        return interpretar(pdf_para_texto(rede.baixar(EDICOES[ano])), ano)


MOTOR = MotorTJPE()
