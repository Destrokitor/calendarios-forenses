"""Motor do TRT19 (Tribunal Regional do Trabalho da 19ª Região, Alagoas).

Fonte única (ficha: docs/fichas/TRT19.md): Ato nº 170/GP/TRT 19ª, de 29/09/2025 (Boletim Interno
nº 10, DEJT de 08/10/2025). PDF de 2 páginas com a tabela MÊS | DIAS | FERIADOS. O Art. 1º diz
"no exercício de 2026", então o ato serve ao ano de 2026.

Como a tabela é lida:
  - Cada linha tem `DIA (dia da semana)` ou um intervalo/lista: "02 a 06 (sexta a terça-feira)",
    "16 e 17 (segunda e terça-feira)". Cada data vira um Dia.
  - A coluna MÊS não é confiável no texto (o rótulo do mês cai no meio do grupo de linhas). O mês
    sai do DIA DA SEMANA impresso na linha: a linha é o primeiro mês, a partir do mês anterior, em
    que a data cai no dia da semana citado. As linhas vêm em ordem cronológica.
  - "Recesso Forense" -> recesso; os demais itens da coluna FERIADOS -> sem_expediente.
  - "Ponto Facultativo" NÃO entra (ver DUVIDA e `parcial`).
  - Recesso de 20/12 a 31/12 vem como linha própria; 25/12 (Natal) tem dois registros.

Abrangência: todos os itens são do tribunal inteiro (o ato se divulga "no âmbito da Justiça do
Trabalho da 19ª Região"), então tudo vai para `geral`. `locais` fica vazio: o ato não lista
feriado de nenhuma comarca do interior (Art. 3º manda observar os feriados locais, sem listá-los).
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT19"
URL = "https://asp1.trt19.jus.br/docspdf/rhdocs/BOLETIM_20251008092236621.PDF"
FONTE_ID = "ato170"
FONTE_DESCRICAO = ("Ato nº 170/GP/TRT 19ª, de 29/09/2025 (Boletim Interno nº 10, DEJT de 08/10/2025): "
                   "feriados e pontos facultativos do exercício de 2026")

# Só o ato de 2026 foi localizado. Outros anos: AindaNaoPublicado (não é falha).
ATOS: Dict[int, str] = {2026: URL}

# Recuo da coluna de descrição no texto do pdftotext -layout. Linha com esse recuo logo após uma
# linha de feriado é continuação da descrição ("Dia do Advogado", "para efeitos forenses...").
RECUO_DESCRICAO = 50

_RE_ART1 = re.compile(r"Art\. 1[º°]")
_RE_ART2 = re.compile(r"Art\. 2[º°]")
_RE_EXERCICIO = re.compile(r"exerc[ií]cio de (\d{4})")
# Linha de dados: [MÊS opcional] DIA [a|e DIA] (DIA DA SEMANA)   DESCRIÇÃO
_RE_LINHA = re.compile(
    r"^\s*(?:[A-ZÇÃÉÊÓÍÚ]{4,}\s+)?(\d{2})(?:\s+(a|e)\s+(\d{2}))?\s*\(([^)]*)\)\s{2,}(\S.*?)\s*$"
)
_RE_SOMENTE_NUMERO = re.compile(r"\d+")
_RE_ROTULO_MES = re.compile(r"(JANEIRO|FEVEREIRO|MARÇO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)")
_SEMANAS = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6}
_RE_SEMANA = re.compile(r"(segunda|terça|quarta|quinta|sexta|sábado|domingo)")

PARCIAL = (
    "Só o que o Ato 170/2025 lista para o tribunal inteiro (feriados e recesso de 2026). Ficam de fora: "
    "(a) feriados locais do interior de Alagoas: o Art. 3º manda observar os feriados locais das Varas "
    "do interior, mas o ato não os lista; (b) os pontos facultativos de 20/04, 05/06, 10/08 e 07/12, "
    "porque o ato não diz se suspendem prazo; (c) alterações posteriores ao ato: não há ato de 2026 "
    "localizado no Boletim Interno."
)


def _bate(ano: int, mes: int, dia_: int, semana: str) -> bool:
    try:
        return datetime.date(ano, mes, dia_).weekday() == _SEMANAS[semana]
    except ValueError:
        return False


def _mes_da_linha(ano: int, minimo: int, pares: List[Tuple[int, str]], rotulo: str) -> int:
    """Primeiro mês >= `minimo` em que cada (dia, dia da semana) da linha confere."""
    for mes in range(minimo, 13):
        if all(_bate(ano, mes, d, s) for d, s in pares):
            return mes
    raise ErroDeFonte("linha do ato não confere com o calendário de %d (dia da semana): %s" % (ano, rotulo))


def _linhas_da_tabela(texto: str) -> List[str]:
    ini = _RE_ART1.search(texto)
    fim = _RE_ART2.search(texto)
    if not ini or not fim or fim.start() < ini.end():
        raise ErroDeFonte("tabela de feriados (entre Art. 1º e Art. 2º) não encontrada no texto do ato")
    return texto[ini.end():fim.start()].replace("\f", "\n").splitlines()


def _ler_linhas(texto: str) -> List[Dict[str, Any]]:
    """Junta as linhas da tabela: cada item com seus dias (texto), dia da semana e descrição."""
    itens: List[Dict[str, Any]] = []
    continua = False  # a linha anterior foi item (ou continuação de item)?
    for bruta in _linhas_da_tabela(texto):
        linha = bruta.rstrip()
        if not linha.strip():
            continue
        m = _RE_LINHA.match(linha)
        if m:
            itens.append({"d1": int(m.group(1)), "conector": m.group(2),
                          "d2": int(m.group(3)) if m.group(3) else None,
                          "semanas": m.group(4), "desc": m.group(5)})
            continua = True
            continue
        texto_linha = linha.strip()
        if _RE_SOMENTE_NUMERO.fullmatch(texto_linha):
            continue  # número de página
        if _RE_ROTULO_MES.fullmatch(texto_linha):
            continue  # rótulo de mês (" DEZEMBRO") solto: não interrompe a descrição
        recuo = len(linha) - len(linha.lstrip(" "))
        if continua and itens and recuo >= RECUO_DESCRICAO:
            itens[-1]["desc"] += " " + texto_linha
        else:
            continua = False
    return itens


def _numeros(item: Dict[str, Any]) -> List[int]:
    if item["conector"] is None:
        return [item["d1"]]
    if item["conector"] == "e":
        return [item["d1"], item["d2"]]
    if item["d2"] < item["d1"]:
        raise ErroDeFonte("intervalo ao contrário no ato: %s a %s" % (item["d1"], item["d2"]))
    return list(range(item["d1"], item["d2"] + 1))


def interpretar(texto: str, ano: int) -> Dict[str, Any]:
    """Texto do ato (pdftotext -layout) -> calendário do ano pedido. Puro: sem rede, sem pdftotext."""
    m = _RE_EXERCICIO.search(texto)
    if not m:
        raise ErroDeFonte("o ato não diz o exercício a que se refere")
    if int(m.group(1)) != ano:
        raise ErroDeFonte("o ato é do exercício de %s, não de %d" % (m.group(1), ano))

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": URL, "descricao": FONTE_DESCRICAO}]

    # DUVIDA: o ato põe na coluna FERIADOS datas que não são feriado nacional nem de fórum
    # (01 a 03/04, Semana Santa; 11/08, Dia do Advogado; 27/08, Padroeira de Maceió, municipal).
    # O motor segue a coluna FERIADOS e trata tudo como feriado do tribunal. Quem revisa confirma.
    itens = _ler_linhas(texto)
    if not itens:
        raise ErroDeFonte("nenhuma linha de feriado lida na tabela do ato")

    mes_atual = 1
    pontos = 0
    for item in itens:
        descricao = item["desc"]
        tokens = _RE_SEMANA.findall(item["semanas"])
        numeros = _numeros(item)
        if item["conector"] is None:
            if len(tokens) != 1:
                raise ErroDeFonte("dia da semana ilegível na linha: %s" % descricao)
            pares = [(item["d1"], tokens[0])]
        else:
            if len(tokens) != 2:
                raise ErroDeFonte("dias da semana ilegíveis na linha: %s" % descricao)
            pares = [(item["d1"], tokens[0]), (item["d2"], tokens[1])]
        if descricao.startswith("Ponto Facultativo"):
            # DUVIDA: ponto facultativo não entra. O ato não diz se suspende prazo; marcar como
            # sem_expediente inventaria suspensão. Fica na ficha e no atributo `parcial`.
            pontos += len(numeros)
            continue
        mes = _mes_da_linha(ano, mes_atual, pares, descricao)
        mes_atual = mes
        tipo = "recesso" if descricao.startswith("Recesso Forense") else "sem_expediente"
        for n in numeros:
            cal["geral"].append(dia(datetime.date(ano, mes, n), tipo, descricao, FONTE_ID))

    if not cal["geral"]:
        raise ErroDeFonte("nenhum dia lido: o formato do ato mudou")
    return ordenar(cal)


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto com layout (colunas preservadas), via pdftotext."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0:
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def baixar(rede: Cliente, ano: int) -> bytes:
    """Único ponto de rede do motor."""
    return rede.baixar(ATOS[ano])


class MotorTRT19(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = PARCIAL
    esperado: Dict[str, Any] = {
        # A ficha não traz contagem. Lido no ato (23/10/2026): 39 registros gerais (38 datas,
        # 25/12 aparece como feriado e como recesso). Piso = o lido.
        "min_geral": 39,
        "min_locais": 0,  # nenhum local listado no ato
        "ancoras": {
            "2026-01-01": "Confraternização universal",
            "2026-01-02": "Recesso forense",
            "2026-01-06": "Recesso forense",
            "2026-02-16": "Carnaval",
            "2026-02-17": "Carnaval",
            "2026-02-18": "Cinzas",
            "2026-06-24": "São João (Lei Estadual 5508/1993)",
            "2026-08-27": "Padroeira de Maceió",
            "2026-12-20": "Recesso forense",
            "2026-12-31": "Recesso forense",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in ATOS:
            raise AindaNaoPublicado("o TRT19 ainda não publicou ato de feriados de %d" % ano)
        return interpretar(pdf_para_texto(baixar(rede, ano)), ano)


MOTOR = MotorTRT19()
