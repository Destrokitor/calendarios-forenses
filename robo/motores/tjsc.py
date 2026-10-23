"""Motor do TJSC (Tribunal de Justiça de Santa Catarina). Ficha: docs/fichas/TJSC.md.

Fonte única, oficial: Resolução GP n. 1, de 16/01/2026 (Presidente), publicada no DJe de
19/01/2026, "Consolida o calendário de feriados para efeitos forenses ... para o ano de 2026".
A busca textual do TJSC expõe o ato num endpoint JSON aberto: o HTML do ato fica em
`resultado.resultados[0].documento.integra`, com a tabela do Anexo Único
(Data | Tipo | Fundamento | Comarcas afetadas).

Abrangência (coluna "Comarcas afetadas"):
  - "Tribunal de Justiça, Turmas Recursais e todas as comarcas do Estado" -> `geral`;
  - "Tribunal de Justiça, Turmas Recursais e a comarca da Capital" -> `locais[FLORIANÓPOLIS]`;
  - nome de município (comarca) -> `locais[MUNICÍPIO]`.
Datas por extenso ("1° de janeiro", "1º de março"): cada linha é um dia.

Efeito jurídico: todo item do Anexo é feriado para efeitos forenses (o título do ato diz
isso), então vira `sem_expediente`. Dúvidas de efeito ficam em `# DUVIDA:`.

Recesso: NÃO está nesta resolução (Art. 1º, parágrafo único: "será regulamentado por resolução
própria"). Por isso `exige_recesso` é False e a lacuna está em `parcial`.

Ano: a resolução de 2026 é a única que a ficha conhece. Para outro ano, a ficha não diz como
achar o endereço (cada ato tem um id próprio no sistema), então o motor levanta
AindaNaoPublicado. Quem achar o ato de 2027 acrescenta o endereço em `ATOS`.
"""
from __future__ import annotations

import datetime
import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TJSC"
FONTE_ID = "resolucao"
# Endereço que o robô lê (JSON). A página humana, que o app mostra ao usuário, é a de baixo.
ATOS: Dict[int, str] = {
    2026: "https://busca.tjsc.jus.br/buscatextual/rest/documento/integra/1/188428",
}
PAGINA_HUMANA = "https://busca.tjsc.jus.br/buscatextual/integra.do?cdSistema=1&cdDocumento=188428&cdCategoria=1"
FONTE_DESCRICAO = ("Resolução GP n. 1, de 16/01/2026 (Anexo Único: calendário de feriados para efeitos "
                   "forenses de 2026), DJe de 19/01/2026, pp. 1 a 4")

GERAL_PREFIXO = "Tribunal de Justiça, Turmas Recursais e todas as comarcas"
CAPITAL = "Tribunal de Justiça, Turmas Recursais e a comarca da Capital"
NOME_CAPITAL = "Florianópolis"
TIPOS_CONHECIDOS = (
    "Nacional",
    "Municipal",
    "Determinado por resolução do Tribunal de Justiça",
    "Efeitos Forenses",
)

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_DATA = re.compile(r"^(\d{1,2})\s*[º°]?\s+de\s+([A-Za-zçÇãéíóú]+)$")
_ANO_DO_ATO = re.compile(r"para o ano de (\d{4})", re.I)


class _Tabela(HTMLParser):
    """Junta o texto de cada <td> e todo o texto do ato (para ler o ano)."""

    def __init__(self) -> None:
        super().__init__()
        self.linhas: List[List[str]] = []
        self.texto: List[str] = []
        self._linha: Optional[List[str]] = None
        self._celula: Optional[List[str]] = None

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag == "tr":
            self._linha = []
        elif tag == "td" and self._linha is not None:
            self._celula = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._celula is not None and self._linha is not None:
            self._linha.append(" ".join("".join(self._celula).split()))
            self._celula = None
        elif tag == "tr" and self._linha is not None:
            self.linhas.append(self._linha)
            self._linha = None

    def handle_data(self, data: str) -> None:
        self.texto.append(data)
        if self._celula is not None:
            self._celula.append(data)


def _integra(conteudo: bytes) -> str:
    """Bytes do endpoint JSON -> HTML do ato. Levanta ErroDeFonte se a forma mudou."""
    try:
        dados = json.loads(conteudo.decode("utf-8"))
        return dados["resultado"]["resultados"][0]["documento"]["integra"]
    except (ValueError, KeyError, IndexError, TypeError, UnicodeDecodeError):
        raise ErroDeFonte("resposta do TJSC fora do formato esperado (resultado.resultados[0].documento.integra)")


def interpretar(conteudo: bytes, ano: int) -> Dict[str, Any]:
    """Bytes do endpoint JSON -> calendário no formato de modelo.py. Puro: sem rede."""
    parser = _Tabela()
    parser.feed(_integra(conteudo))
    parser.close()

    achou = _ANO_DO_ATO.search(" ".join("".join(parser.texto).split()))
    if not achou or int(achou.group(1)) != ano:
        raise ErroDeFonte("o ato não é o calendário de %d" % ano)

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": PAGINA_HUMANA, "descricao": FONTE_DESCRICAO}]
    locais: Dict[str, List[Dict[str, str]]] = {}

    linhas_de_dado = 0
    for celulas in parser.linhas:
        if len(celulas) != 4 or celulas[0] == "Data":
            continue  # cabeçalho ou linha de layout
        data_txt, tipo_txt, motivo, comarcas = celulas
        m = _DATA.match(data_txt)
        if not m or m.group(2).lower() not in MESES:
            raise ErroDeFonte("data fora do formato esperado: %r" % data_txt)
        data = datetime.date(ano, MESES[m.group(2).lower()], int(m.group(1)))  # ErroDeFonte se não existe
        if tipo_txt not in TIPOS_CONHECIDOS:
            raise ErroDeFonte("tipo de item desconhecido na tabela: %r" % tipo_txt)
        if not motivo:
            raise ErroDeFonte("item sem fundamento em %s" % data.isoformat())

        # DUVIDA: todo item é feriado para efeitos forenses (o título do ato), logo sem_expediente.
        # Dois casos pedem confirmação do efeito (a ficha também pede): 28/10 "Dia do Funcionário
        # Público" (determinado por resolução do TJ) e 08/12 "Dia da Justiça" (tipo "Efeitos
        # Forenses"). Se a revisão disser que um deles não suspende prazo, troque o tipo aqui.
        item = dia(data, "sem_expediente", motivo, FONTE_ID)
        linhas_de_dado += 1

        if comarcas.startswith(GERAL_PREFIXO):
            cal["geral"].append(item)
        elif comarcas == CAPITAL:
            locais.setdefault(normalizar_local(NOME_CAPITAL), []).append(item)
        else:
            if "," in comarcas or " e " in comarcas or "Tribunal" in comarcas:
                raise ErroDeFonte("comarca composta não prevista na tabela: %r" % comarcas)
            locais.setdefault(normalizar_local(comarcas), []).append(item)

    if linhas_de_dado == 0:
        raise ErroDeFonte("nenhuma linha de feriado na tabela do ato: o formato mudou")

    cal["locais"] = locais
    return ordenar(cal)


class MotorTJSC(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False  # a ficha registra o teste na nuvem (run 39986359557)
    parcial = (
        "Lê só a Resolução GP n. 1/2026 (feriados para efeitos forenses). Ficam de fora: "
        "(a) o recesso forense, que o Art. 1º, parágrafo único, manda regulamentar por resolução própria "
        "(a de 2025/26 foi a Resolução TJ n. 30/2025; a de 2026/27 não foi localizada), então este "
        "calendário não tem dia de recesso; "
        "(b) os ajustes pontuais de feriado municipal previstos no Art. 2º, que sairiam em norma nova "
        "não lida (não verificado); "
        "(c) comarca que não tem feriado municipal nesta resolução: o ato só lista os municípios com "
        "feriado, então ela não aparece em `locais`; "
        "(d) o calendário de 2027, que tem outro ato e não foi localizado (ver `ATOS`)."
    )
    esperado = {
        # A ficha não traz contagem. Lido na fixture de 2026: 16 dias gerais (9 nacionais, 6 determinados
        # por resolução do TJ, 1 de efeitos forenses). Piso = o lido.
        "min_geral": 16,
        # Lido na fixture: 110 locais distintos (195 linhas municipais, Florianópolis incluída). Piso = o lido.
        "min_locais": 110,
        # Conferidas à mão no ato (ficha, âncoras 1 a 4). Só dias GERAIS.
        "ancoras": {
            "2026-02-16": "Segunda-feira de Carnaval",
            "2026-02-17": "Terça-feira de Carnaval",
            "2026-04-02": "Quinta-feira da Semana Santa",
            "2026-04-03": "Sexta-feira Santa",
            "2026-06-04": "Corpus Christi",
            "2026-12-08": "Dia da Justiça (Efeitos Forenses)",
        },
        "exige_recesso": False,  # o recesso não está no ato (ver `parcial`)
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in ATOS:
            raise AindaNaoPublicado(
                "o TJSC: a ficha não traz como localizar o calendário de %d (cada ato tem id próprio); "
                "o de 2026 é o único conhecido" % ano)
        return interpretar(rede.baixar(ATOS[ano]), ano)


MOTOR = MotorTJSC()
