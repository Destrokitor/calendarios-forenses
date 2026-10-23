"""Motor do TJPR (Tribunal de Justiça do Estado do Paraná). Ficha: docs/fichas/TJPR.md.

Fonte única, oficial (ficha: docs/fichas/TJPR.md):

  Decreto Judiciário n.º 621/2025 - P-SEP (SEI 0064955-90.2025.8.16.6000), assinado em 19/11/2025.
  PDF com texto, lido com `pdftotext`. Quatro artigos:

  - Art. 1º: feriados do tribunal -> geral (exceto 08/09, "somente no Município de Curitiba" -> locais).
  - Art. 2º: suspensões do expediente com compensação de 1h -> geral, sem_expediente.
  - Art. 3º: suspensões do expediente sem compensação (24 e 31/12) -> geral, sem_expediente.
  - Art. 4º: feriados locais dos municípios-sede de comarca, mês a mês ("dia N: Município (motivo), ...")
    -> locais[MUNICÍPIO], sem_expediente.

Não entra: RECESSO FORENSE (20/12 a 06/01). O decreto NÃO o menciona, e o motor não o inventa:
`exige_recesso` é False. Ver `parcial`.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_ID = "decreto"
FONTE_DESCRICAO = ("Decreto Judiciário n.º 621/2025 - P-SEP (SEI 0064955-90.2025.8.16.6000), "
                   "assinado em 19/11/2025: feriados, suspensões e feriados locais de 2026")

# Endereço de cada ano. A ficha só conhece o de 2026. Para o ano seguinte, a ficha não diz como achar
# o decreto (ver AindaNaoPublicado em coletar).
DECRETOS: Dict[int, str] = {
    2026: "https://portal.tjpr.jus.br/pesquisa_athos/anexo/7104379",
}

MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
_MESES_RE = "|".join(MESES)

# Rodapé de página do decreto ("Decreto Judiciário n.º 621/2025 (12428873)  SEI ... / pg. 2"):
# sai antes de ler, senão o número da página cairia no meio de um motivo.
_RE_RODAPE = re.compile(r"Decreto Judiciário n\.º 621/2025 \(\d+\)\s+SEI [\d.\-]+ / pg\. \d+")
_RE_ANO = re.compile(r"no ano de (\d{4})")
_RE_ARTIGO = re.compile(r"Art\.\s*([1-5])\s*[º°]")
# Cabeçalho de mês nos Art. 1º a 4º ("janeiro:", "Março:") e cabeçalho ou "dia N:" do Art. 4º.
_RE_TOKEN_ART4 = re.compile(r"(%s)\s*:|dia\s+(\d{1,2})\s*[º°]?\s*:" % _MESES_RE, re.I)
_RE_MES_ART123 = re.compile(r"(%s)\s*:" % _MESES_RE, re.I)
# Item dos Art. 1º a 3º: "17 (terça-feira) - Carnaval". O motivo vai até o próximo item.
_RE_ITEM_DIA = re.compile(r"(?<![\d/])(\d{1,2})\s*[º°]?\s*\(([^()]*)\)")
# Item do Art. 4º: "Astorga (Fundação do Município - transferido do dia 14/12/25)".
_RE_MUNICIPIO = re.compile(r"([^(),;]+?)\s*\(([^()]*)\)?")
_RE_SOMENTE = re.compile(r",?\s*somente no Município de (.+)$")

# Grafias do próprio decreto que trocam o nome do município: a chave é a forma oficial.
ALIAS_MUNICIPIO = {"BOCAÍUVA DO SUL": "BOCAIÚVA DO SUL"}

# Efeito de todo dia dos Art. 1º a 3º e do Art. 4º: o decreto manda "suspenso o expediente". Não se
# decide aqui suspensão de prazo. Ver os DUVIDA abaixo.
TIPO_PADRAO = "sem_expediente"

PARCIAL = (
    "Lê só o Decreto Judiciário n.º 621/2025 (exercício de 2026). NÃO entra o RECESSO FORENSE "
    "(20/12 a 06/01): o decreto não o menciona, e a fonte dele precisa ser outra (DUVIDA na ficha). "
    "Também ficam de fora: feriado municipal decretado à parte depois do Art. 4º (ex.: portaria "
    "de um município no meio do ano; não verificado), pontos facultativos, e qualquer alteração "
    "de decreto posterior ao de 19/11/2025 (não lida)."
)


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto, via pdftotext (sem colunas: o decreto é de uma coluna só)."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _data(ano: int, mes: int, dia_: int) -> datetime.date:
    try:
        return datetime.date(ano, mes, dia_)
    except ValueError:
        raise ErroDeFonte("data inexistente no decreto: %02d/%02d/%d" % (dia_, mes, ano))


def _motivo(resto: str) -> str:
    """Texto que segue um item ("- Carnaval, e" -> "Carnaval"). Tira o traço, a vírgula, o ponto e
    o "e" que liga ao item seguinte."""
    s = re.sub(r"^\s*-\s*", "", resto.strip())
    while True:
        novo = re.sub(r"[\s;.,]+$", "", s)
        novo = re.sub(r"\s+e$", "", novo)
        if novo == s:
            return s
        s = novo


def _por_mes(corpo: str) -> List[Tuple[int, str]]:
    """Divide um artigo em (mês, trecho) pelos cabeçalhos 'janeiro:' ... 'dezembro:'."""
    marcas = list(_RE_MES_ART123.finditer(corpo))
    saida = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(corpo)
        saida.append((MESES.index(m.group(1).lower()) + 1, corpo[m.end():fim]))
    return saida


def _itens_dia(trecho: str) -> List[Tuple[int, str]]:
    """(dia, motivo) de cada item de um trecho mensal. Item sem motivo volta com motivo vazio."""
    marcas = list(_RE_ITEM_DIA.finditer(trecho))
    saida = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(trecho)
        saida.append((int(m.group(1)), _motivo(trecho[m.end():fim])))
    return saida


def _art4(corpo: str, ano: int) -> List[Tuple[datetime.date, str, str]]:
    """Art. 4º -> (data, município, motivo). Cada "dia N:" lista municípios separados por vírgula;
    o ponto e vírgula fecha o dia."""
    saida: List[Tuple[datetime.date, str, str]] = []
    marcas = list(_RE_TOKEN_ART4.finditer(corpo))
    mes: Optional[int] = None
    for i, m in enumerate(marcas):
        if m.group(1):  # cabeçalho de mês
            mes = MESES.index(m.group(1).lower()) + 1
            continue
        if mes is None:
            raise ErroDeFonte("Art. 4º: dia antes do primeiro mês")
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(corpo)
        trecho = re.sub(r"[\s;:.]+$", "", corpo[m.end():fim].strip())
        data = _data(ano, mes, int(m.group(2)))
        if trecho.count("(") == 0:
            raise ErroDeFonte("Art. 4º: dia %s sem município entre parênteses" % data.isoformat())
        itens = _RE_MUNICIPIO.findall(trecho)
        if trecho.count("(") != len(itens):
            raise ErroDeFonte("Art. 4º: item sem parênteses em %s: %r" % (data.isoformat(), trecho[:120]))
        for nome, motivo in itens:
            nome = ALIAS_MUNICIPIO.get(" ".join(nome.upper().split()), nome)
            motivo = " ".join(motivo.split())
            if not nome.strip() or not motivo:
                raise ErroDeFonte("Art. 4º: item incompleto em %s" % data.isoformat())
            saida.append((data, nome.strip(), motivo))
    return saida


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do decreto (pdftotext) -> calendário no formato de modelo.py. Puro: sem rede."""
    texto = " ".join(_RE_RODAPE.sub(" ", conteudo).split())
    achou = _RE_ANO.search(texto)
    if not achou or int(achou.group(1)) != ano:
        raise ErroDeFonte("o decreto não é do exercício de %d" % ano)

    partes = _RE_ARTIGO.split(texto)
    artigos = {int(partes[i]): partes[i + 1] for i in range(1, len(partes) - 1, 2)}
    for n in (1, 2, 3, 4):
        if n not in artigos:
            raise ErroDeFonte("não achei o Art. %d.º no decreto" % n)

    cal = calendario_vazio("TJPR", ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": DECRETOS.get(ano, ""), "descricao": FONTE_DESCRICAO}]
    geral: List[Dict[str, str]] = []
    locais: Dict[str, List[Dict[str, str]]] = {}

    # Art. 1º (feriados), Art. 2º (suspensões com compensação de 1h) e Art. 3º (suspensões sem compensação).
    for n in (1, 2, 3):
        for mes, trecho in _por_mes(artigos[n]):
            for d, motivo in _itens_dia(trecho):
                data = _data(ano, mes, d)
                if not motivo:
                    # DUVIDA: o Art. 2º (05/06 e 20/04) e o Art. 3º não dão motivo. Registro honesto.
                    motivo = "Suspensão do expediente (sem motivo no decreto)"
                local: Optional[str] = None
                so = _RE_SOMENTE.search(motivo)
                if so:  # "Padroeira de Curitiba, somente no Município de Curitiba"
                    local = normalizar_local(so.group(1))
                    motivo = motivo[:so.start()].strip()
                motivo = motivo[:1].upper() + motivo[1:]
                # DUVIDA: "suspenso o expediente" (Art. 2º e 3º) é tratado como sem_expediente, o mais
                # conservador sem invocar suspensão de prazo. Quem revisa confirma o efeito.
                # DUVIDA: no Art. 2º a compensação de 1h não muda o efeito do dia (dia sem expediente).
                item = dia(data, TIPO_PADRAO, motivo, FONTE_ID)
                if local:
                    locais.setdefault(local, []).append(item)
                else:
                    geral.append(item)

    # Art. 4º: feriados dos municípios-sede de comarca.
    for data, nome, motivo in _art4(artigos[4], ano):
        locais.setdefault(normalizar_local(nome), []).append(dia(data, TIPO_PADRAO, motivo, FONTE_ID))

    cal["geral"] = geral
    cal["locais"] = locais
    return ordenar(cal)  # deixa a saída determinística (dias por data, locais por nome)


class MotorTJPR(Motor):
    sigla = "TJPR"
    precisa_ip_brasil = False  # ficha: abriu na nuvem (200 em 22,3 s; 503 numa tentativa)
    parcial = PARCIAL
    esperado = {
        # min_geral: a ficha não traz contagem. Lido na fixture: 20 dias gerais (14 do Art. 1º,
        # 4 do Art. 2º, 2 do Art. 3º). Piso = o lido.
        "min_geral": 20,
        # min_locais: a ficha diz "~150 municípios-sede". Lido na fixture: 162 locais (161 do Art. 4º
        # + Curitiba do Art. 1º). Piso = o lido.
        "min_locais": 162,
        # Conferidas à mão no decreto (ficha, âncoras 1, 2, 3 e 4), todas no Art. 1º ou no Art. 2º.
        # A âncora 5 (São José dos Pinhais, 19/03) é de município: fica no teste, não em `geral`.
        "ancoras": {
            "2026-02-17": "Carnaval (Art. 1º)",
            "2026-06-04": "Corpus Christi (Art. 1º)",
            "2026-12-18": "Dia da Justiça, transferido do dia 08/12 (Art. 1º)",
            "2026-02-16": "Véspera de Carnaval, suspensão com compensação de 1h (Art. 2º)",
        },
        "exige_recesso": False,  # o decreto não traz o recesso forense (20/12 a 06/01)
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in DECRETOS:
            # DUVIDA: a ficha não diz onde sai o decreto do ano seguinte. Enquanto não houver a regra,
            # o robô só registra o fato.
            raise AindaNaoPublicado("a ficha do TJPR não diz como localizar o decreto de %d" % ano)
        return interpretar(pdf_para_texto(rede.baixar(DECRETOS[ano])), ano)


MOTOR = MotorTJPR()
