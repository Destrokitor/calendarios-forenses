"""Motor do TJMA (Tribunal de Justiça do Estado do Maranhão). Ficha: docs/fichas/TJMA.md.

Fonte única, oficial (ficha): Resolução-GP nº 131, de 04/11/2025 (DJe de 06/11/2025), que
"relaciona os dias em que não haverá expediente" no Poder Judiciário estadual em 2026. O PDF tem
camada de texto; o motor junta o texto (`pdftotext -layout`) e lê por regex.

Abrangência:
  - Art. 1º, incisos I a XVII -> `geral`, tipo sem_expediente (inclui os "Feriado Forense" da LC 14/1991);
  - Art. 1º, parágrafo único -> `locais["SÃO LUÍS"]`: 29/06 (São Pedro) e 08/09 (Fundação da Cidade),
    só no Termo Judiciário de São Luís (Comarca da Ilha de São Luís);
  - Art. 3º, pontos facultativos (18/02, 01/04, 05/06): NÃO entram. O ato não diz se suspendem
    prazo; não inventar suspensão. Ver DUVIDA abaixo e `parcial`;
  - Art. 2º, feriados municipais do interior: o ato não traz lista (remete a lei municipal). Ficam de fora.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_ID = "resolucao"
FONTE_URL = ("https://novogerenciador.tjma.jus.br/storage/arquivos/resolucoes_2025/"
             "resolucao_gp_n_131_de_4_de_novembro_de_2025_05_11_2025_17_12_45.pdf")
FONTE_DESCRICAO = "Resolução-GP nº 131, de 04/11/2025 (DJe de 06/11/2025): dias sem expediente em 2026"

# Calendário de cada ano. Ano que não está aqui levanta AindaNaoPublicado.
# DUVIDA: a ficha não diz como achar o ato de 2027 (o endereço tem a data de publicação no nome).
# Enquanto não houver a regra, o robô só registra o fato.
CALENDARIOS: Dict[int, str] = {2026: FONTE_URL}

LOCAL_SAO_LUIS = "SÃO LUÍS"

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
           "XV", "XVI", "XVII"]

MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

# Início de inciso: "II – 16 de fevereiro (segunda-feira) - " (travessão ou hífen; "IX–" sem espaço).
_INICIO_INCISO = re.compile(r"\b([IVXL]+)\s*[–-]\s*(\d{1,2})º?\s+de\s+([a-zç]+)\s*\([^)]*\)\s*[–-]\s*")
# Parágrafo único: "29 de junho (segunda-feira), dia de São Pedro e 08 de setembro (terça-feira), dia da ..."
_MUNICIPAL = re.compile(
    r"(\d{1,2})\s+de\s+([a-zç]+)\s*\([^)]*\),\s*(dia de São Pedro|dia da Fundação da Cidade de São Luís)")
_MOTIVO_MUNICIPAL = {
    "dia de São Pedro": "São Pedro (feriado municipal de São Luís)",
    "dia da Fundação da Cidade de São Luís": "Fundação da Cidade de São Luís (feriado municipal de São Luís)",
}

PARCIAL = (
    "Lê só a Resolução-GP nº 131/2025 (ano de 2026). LACUNA: a Resolução-GP nº 26, de 07/04/2026, "
    "alterou o ato e o que ela mudou NÃO foi conferido (a versão consolidada não abriu, 404); por isso "
    "as datas podem estar defasadas. Ficam de fora: (1) os pontos facultativos do Art. 3º (18/02, 01/04, "
    "05/06), porque o ato não diz se suspendem prazo; (2) os feriados municipais do interior (Art. 2º), "
    "que dependem de lei municipal sem lista no ato: só São Luís tem os dois feriados nomeados "
    "(29/06 e 08/09); (3) decretos e portarias posteriores de outros Poderes ou da Corregedoria. "
    "Em 2027 não há ato conhecido."
)


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto, via pdftotext."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _data(dia_txt: str, mes_txt: str, ano: int) -> datetime.date:
    mes = MESES.get(mes_txt.lower())
    if mes is None:
        raise ErroDeFonte("mês não reconhecido no ato: %r" % mes_txt)
    return datetime.date(ano, mes, int(dia_txt))


def _incisos(secao: str, ano: int) -> List[Tuple[datetime.date, str]]:
    """Incisos do Art. 1º: (data, motivo). Cada motivo vai até o início do inciso seguinte."""
    inicios = list(_INICIO_INCISO.finditer(secao))
    if [m.group(1) for m in inicios] != ROMANOS:
        raise ErroDeFonte("incisos do Art. 1º diferentes do esperado (%d achados)" % len(inicios))
    itens = []
    for i, m in enumerate(inicios):
        fim = inicios[i + 1].start() if i + 1 < len(inicios) else len(secao)
        motivo = secao[m.end():fim]
        motivo = re.sub(r"\s*\(§[^)]*\)", "", motivo)   # cita a LC 14/1991; o motivo fica sem a citação
        motivo = re.sub(r"[\s;.]+$", "", motivo.strip())
        itens.append((_data(m.group(2), m.group(3), ano), motivo))
    return itens


def _municipais(secao: str, ano: int) -> List[Tuple[datetime.date, str]]:
    itens = [(_data(m.group(1), m.group(2), ano), _MOTIVO_MUNICIPAL[m.group(3)])
             for m in _MUNICIPAL.finditer(secao)]
    if len(itens) != 2:
        raise ErroDeFonte("esperava 2 feriados municipais de São Luís e achei %d" % len(itens))
    return itens


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do ato (pdftotext) -> calendário no formato de modelo.py. Puro: sem rede."""
    texto = " ".join(conteudo.split())
    m = re.search(r"no ano de (\d{4})", texto)
    if not m:
        raise ErroDeFonte("não achei o ano do ato")
    if int(m.group(1)) != ano:
        raise ErroDeFonte("o ato é de %s, não de %d" % (m.group(1), ano))

    i_art1 = texto.find("Art. 1º")
    i_par = texto.find("Parágrafo único.")
    i_art2 = texto.find("Art. 2º")
    if not (0 <= i_art1 < i_par < i_art2):
        raise ErroDeFonte("estrutura do ato diferente do esperado (Art. 1º, parágrafo único, Art. 2º)")

    cal = calendario_vazio(MotorTJMA.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]
    chave_sl = normalizar_local(LOCAL_SAO_LUIS)
    cal["locais"] = {chave_sl: []}

    for data, motivo in _incisos(texto[i_art1:i_par], ano):
        cal["geral"].append(dia(data, "sem_expediente", motivo, FONTE_ID))
    for data, motivo in _municipais(texto[i_par:i_art2], ano):
        cal["locais"][chave_sl].append(dia(data, "sem_expediente", motivo, FONTE_ID))

    # DUVIDA: os pontos facultativos do Art. 3º (18/02, 01/04, 05/06) não entram. O ato não diz se
    # suspendem prazo, e marcar como sem_expediente ou suspensao_prazo seria inventar o efeito.
    # Quem revisa decide se entram (e com qual tipo).
    return ordenar(cal)


class MotorTJMA(Motor):
    sigla = "TJMA"
    precisa_ip_brasil = False  # ficha: testado do GitHub Actions, o PDF abre (200)
    parcial = PARCIAL
    esperado = {
        "min_geral": 17,   # Art. 1º, incisos I a XVII (ato de 2026)
        "min_locais": 1,   # só SÃO LUÍS tem feriados nomeados no ato
        # Conferidas à mão no ato (ficha, âncoras 1, 2 e 5). Só dias gerais: o validador confere `geral`.
        # As âncoras 3 e 4 (29/06 e 08/09) são de `locais` e são conferidas nos testes.
        "ancoras": {
            "2026-01-01": "Dia da Confraternização Universal (inciso I)",
            "2026-07-28": "Adesão do Maranhão à Independência do Brasil (inciso IX)",
            "2026-08-11": "Dia do Advogado, feriado forense (inciso X)",
        },
        "exige_recesso": False,  # o ato não traz recesso de fim de ano (CPC 20/12 a 20/01 não consta)
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in CALENDARIOS:
            raise AindaNaoPublicado(
                "a ficha do TJMA não diz como localizar o ato de %d; a única resolução conhecida "
                "(Res.-GP 131/2025) traz só o exercício de 2026" % ano)
        return interpretar(pdf_para_texto(rede.baixar(CALENDARIOS[ano])), ano)


MOTOR = MotorTJMA()
