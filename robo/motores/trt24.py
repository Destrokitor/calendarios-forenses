"""Motor do TRT24 (Tribunal Regional do Trabalho da 24ª Região, Mato Grosso do Sul).

Fonte única, oficial: a página "Calendário Institucional" do portal
(https://www.trt24.jus.br/calendario). Ela traz uma tabela HTML com as colunas
`Data | Localidade | Descrição | Legislação`, com o ano inteiro, todas as cidades.
Ver docs/fichas/TRT24.md.

  - Localidade "Nacional", "Estadual" ou "Tribunal" vale para o tribunal inteiro: vai em `geral`.
  - Localidade com nome de município vai em `locais[MUNICÍPIO]`.
  - O tipo do dia sai do TEXTO da Descrição (a tabela não tem coluna de tipo):
      "Recesso Forense"                     -> recesso
      "Suspensão de prazos processuais"     -> suspensao_prazo
      "Suspensão expediente até as Xh"      -> parcial (horario "até as Xh")
      "Suspensão expediente"                -> sem_expediente
      "Expediente das Xh às Yh"             -> parcial (horario "das Xh às Yh")
      qualquer outra (feriados)             -> sem_expediente

A página só mostra o ano escolhido no seletor (2026 nesta fixture). Se o ano pedido não
estiver na tabela, o motor levanta AindaNaoPublicado. Não há POST do formulário.
"""
from __future__ import annotations

import datetime
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT24"
URL = "https://www.trt24.jus.br/calendario"
FONTE_ID = "calendario"

# Localidades que valem para o tribunal inteiro (vão em `geral`).
LOCAIS_GERAIS = ("Nacional", "Estadual", "Tribunal")

# DUVIDA: as linhas de Rio Brilhante (26/09 e 08/12) e de Maracaju (12/10) vêm sem a coluna
# Legislação. Foram tratadas como feriado local (sem_expediente), pelo mesmo padrão de
# "Aniversário de X" e "Padroeiro de X". A ficha registra a falta de legislação mas não decide
# o efeito. Quem revisa confirma.

# Os dias de 7 a 20/01 NÃO entram: a fonte não os lista (ver a ficha). Não inventar.

_DATA = re.compile(r"\d{2}/\d{2}/\d{4}$")
_SUSP_ATE = re.compile(r"Suspensão expediente até as (\d{1,2})h")
_EXPEDIENTE = re.compile(r"Expediente das (\d{1,2})h às (\d{1,2})h$")


class _Tabelas(HTMLParser):
    """Coleta as linhas de todas as tabelas (só células <td>) e as opções de todos os <select>.

    A página tem uma tabela de calendário mensal (cujas células não são data) e a lista de
    feriados. Quem decide o que é linha de dado é `interpretar`, pela forma da primeira célula.
    """

    def __init__(self) -> None:
        super().__init__()
        self.linhas: List[List[str]] = []
        self.selects: List[List[str]] = []
        self._linha: Optional[List[str]] = None
        self._celula: Optional[List[str]] = None
        self._opcao: Optional[List[str]] = None
        self._dentro_select = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "tr":
            self._linha = []
        elif tag == "td" and self._linha is not None:
            self._celula = []
        elif tag == "select":
            self.selects.append([])
            self._dentro_select = True
        elif tag == "option" and self._dentro_select:
            self._opcao = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._celula is not None and self._linha is not None:
            self._linha.append(" ".join("".join(self._celula).split()))
            self._celula = None
        elif tag == "tr" and self._linha is not None:
            self.linhas.append(self._linha)
            self._linha = None
        elif tag == "option" and self._opcao is not None:
            self.selects[-1].append(" ".join("".join(self._opcao).split()))
            self._opcao = None
        elif tag == "select":
            self._dentro_select = False

    def handle_data(self, data: str) -> None:
        # Texto solto entre células (ex.: o "<" perdido do HTML "<<td>") não entra em lugar nenhum.
        if self._celula is not None:
            self._celula.append(data)
        if self._opcao is not None:
            self._opcao.append(data)


def _classificar(descricao: str) -> Tuple[str, str]:
    """Devolve (tipo, horario) a partir do texto da Descrição. Horario só no tipo parcial."""
    if descricao.startswith("Suspensão de prazos"):
        return "suspensao_prazo", ""
    if descricao == "Recesso Forense":
        return "recesso", ""
    m = _SUSP_ATE.match(descricao)
    if m:
        return "parcial", "até as %sh" % m.group(1)
    if descricao.startswith("Suspensão expediente"):
        return "sem_expediente", ""
    m = _EXPEDIENTE.match(descricao)
    if m:
        return "parcial", "das %sh às %sh" % (m.group(1), m.group(2))
    if descricao.startswith("Expediente"):
        # Formato novo que este motor não conhece: melhor parar do que adivinhar o horário.
        raise ErroDeFonte("descrição de expediente em formato não previsto: %r" % descricao)
    return "sem_expediente", ""  # feriado (nacional, estadual, do tribunal ou municipal)


def _cidades(selects: List[List[str]]) -> List[str]:
    """Nomes dos municípios: opções do seletor que tem 'Todas as cidades.'."""
    for opcoes in selects:
        if any(o.startswith("Todas as cidades") for o in opcoes):
            return [o for o in opcoes if o and not o.startswith("Todas as cidades")]
    return []


def baixar(rede: Cliente) -> bytes:
    """Único ponto de rede do motor."""
    return rede.baixar(URL)


def interpretar(conteudo: Any, ano: int) -> Dict[str, Any]:
    """Lê o HTML da página (bytes ou texto) e devolve o calendário do ano pedido. Não usa rede."""
    texto = conteudo.decode("utf-8") if isinstance(conteudo, bytes) else conteudo
    parser = _Tabelas()
    parser.feed(texto)
    parser.close()

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{
        "id": FONTE_ID,
        "url": URL,
        "descricao": "Calendário Institucional do TRT24 (lista de feriados, expedientes e suspensões)",
    }]
    # Todo município do seletor entra em `locais`, mesmo sem dia (lista vazia é válida).
    for nome in _cidades(parser.selects):
        cal["locais"][normalizar_local(nome)] = []

    total_datadas = 0
    for celulas in parser.linhas:
        if len(celulas) != 4 or not _DATA.match(celulas[0]):
            continue  # cabeçalho, calendário mensal, linha vazia
        data = datetime.datetime.strptime(celulas[0], "%d/%m/%Y").date()
        total_datadas += 1
        if data.year != ano:
            continue
        localidade, descricao = celulas[1], celulas[2]
        tipo, horario = _classificar(descricao)
        item = dia(data, tipo, descricao, FONTE_ID, horario)
        if localidade in LOCAIS_GERAIS:
            cal["geral"].append(item)
        else:
            cal["locais"].setdefault(normalizar_local(localidade), []).append(item)

    if total_datadas == 0:
        raise ErroDeFonte("nenhuma linha de data encontrada na tabela: o formato da página mudou")
    if not cal["geral"] and not any(cal["locais"].values()):
        raise AindaNaoPublicado("o TRT24 ainda não publicou dias de %d na página do calendário" % ano)
    return ordenar(cal)


class MotorTRT24(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = ""
    esperado = {
        # A ficha não traz contagem de dias gerais. 40 é um piso conservador (ver test_trt24).
        "min_geral": 40,
        "min_locais": 22,   # os 22 municípios do seletor, na ficha
        "ancoras": {        # só dias GERAIS: a validação confere em `geral`
            "2026-02-16": "Carnaval (Nacional)",
            "2026-02-17": "Carnaval (Nacional)",
            "2026-02-18": "Suspensão expediente até as 13h (RA 92/2025), parcial",
            "2026-06-24": "Expediente das 8h às 15h (RA 79/2026), parcial",
            "2026-06-29": "Expediente das 7h às 11h (RA 81/2026), parcial",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede), ano)


MOTOR = MotorTRT24()
