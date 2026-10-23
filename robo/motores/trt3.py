"""Motor do TRT3 (Tribunal Regional do Trabalho da 3ª Região, Minas Gerais).

Duas páginas HTML oficiais do portal (ver docs/fichas/TRT3.md):

  - Calendário 2026 (`calendario-2026`): tabela "Feriados da Justiça do Trabalho de Minas
    Gerais" (`Dias do mês | Dia da semana | Motivo`), que vale para o tribunal inteiro. Vai em
    `geral`. Traz feriados nacionais, Carnaval, Cinzas, Semana Santa, recesso (1 a 6/01 e 20 a
    31/12) e as datas remarcadas. As tabelas mensais (7 colunas) são só a grade do mês: ignoradas.
  - Feriados locais 2026 (`feriados-locais-2026`): uma tabela por mês (`Data | Localidade |
    Motivo`; a data é só o dia, o mês vem da legenda "<Mês> / 2026"). Vai em `locais`, com o nome
    do município normalizado. Inclui a "Suspensão do expediente" de 05/06 por município (RA 109).

Regras de efeito (decisão da ficha):
  - Corpus Christi (04/06) é feriado LOCAL, não geral: a linha "4 e 5 de junho" da tabela geral é
    deixada de fora (o 04 e o 05 entram pela tabela de locais, só nas localidades listadas).
  - A suspensão de 05/06 vale só nos municípios da tabela de locais, nunca em `geral`.
  - Recesso vira `recesso`; os demais dias da tabela geral viram `sem_expediente`.

O 1º de maio (Dia do Trabalhador) não está na tabela geral da página; aparece como parágrafo
solto entre os meses. O motor acrescenta esse dia fixo (Lei 662/1949) só se o texto
"Dia do Trabalhador" estiver na página: se sair da página, levanta ErroDeFonte.
"""
from __future__ import annotations

import datetime
import re
import unicodedata
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT3"

FONTE_GERAL = "calendario"
FONTE_LOCAIS = "feriados-locais"
FONTE_RA = "ra109"

URL_GERAL_2026 = "https://portal.trt3.jus.br/internet/institucional/calendario/calendario-2026"
URL_LOCAIS_2026 = "https://portal.trt3.jus.br/internet/institucional/calendario/feriados-locais-1/feriados-locais-2026"

# Endereço de cada página por ano. DUVIDA: a ficha não localizou o endereço de 2027; até lá,
# qualquer ano fora deste mapa levanta AindaNaoPublicado (o robô tenta de novo depois).
PAGINAS: Dict[int, Dict[str, str]] = {
    2026: {"geral": URL_GERAL_2026, "locais": URL_LOCAIS_2026},
}

_MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

_UM_DIA = re.compile(r"^(\d{1,2})º? de (\w+)$")
_DOIS_DIAS = re.compile(r"^(\d{1,2}) e (\d{1,2}) de (\w+)$")
_INTERVALO = re.compile(r"^(\d{1,2})º? a (\d{1,2}) de (\w+)$")
_LEGENDA_LOCAL = re.compile(r"^(\w+) / (\d{4})$")       # "Janeiro / 2026" (tabela de locais)
_LEGENDA_MENSAL = re.compile(r"^(\w+) (\d{4})$")         # "Janeiro 2026" (grade mensal)
_TABELA_GERAL = "Feriados da Justiça"                    # legenda da tabela que vale para todo o estado
_CABECALHO_GERAL = "Dias do mês"

# Linha da tabela geral que é local (Corpus Christi, com a suspensão do dia 5 condicionada).
_MARCA_LOCAL = "Corpus Christi"

PARCIAL = (
    "Feriados locais só dos municípios que aparecem na tabela da página (66 localidades). "
    "Feriado municipal não publicado pelo TRT3 fica de fora. Suspensões avulsas de prazo, como "
    "as dos jogos do Brasil na Copa do Mundo (portaria da Presidência, sem lista estruturada), "
    "não entram. Alterações posteriores só valem se a página já as trouxer. Ano sem endereço "
    "registrado no motor (hoje só 2026) levanta AindaNaoPublicado."
)


def _limpar(texto: str) -> str:
    return " ".join(texto.split())


def _mes(nome: str) -> int:
    """'março' -> 3. Ignora acento e maiúscula."""
    semacento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    numero = _MESES.get(semacento.lower())
    if numero is None:
        raise ErroDeFonte("mês desconhecido na página: %r" % nome)
    return numero


class _Tabelas(HTMLParser):
    """Coleta cada tabela com sua legenda (<caption>) e as linhas de células de texto."""

    def __init__(self) -> None:
        super().__init__()
        self.tabelas: List[Dict[str, Any]] = []
        self._tabela: Optional[Dict[str, Any]] = None
        self._linha: Optional[List[str]] = None
        self._celula: Optional[List[str]] = None
        self._legenda: Optional[List[str]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "table":
            self._tabela = {"legenda": "", "linhas": []}
            self.tabelas.append(self._tabela)
        elif tag == "caption" and self._tabela is not None:
            self._legenda = []
        elif tag == "tr" and self._tabela is not None:
            self._linha = []
        elif tag in ("td", "th") and self._linha is not None:
            self._celula = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "caption" and self._legenda is not None and self._tabela is not None:
            self._tabela["legenda"] = _limpar("".join(self._legenda))
            self._legenda = None
        elif tag in ("td", "th") and self._celula is not None and self._linha is not None:
            self._linha.append(_limpar("".join(self._celula)))
            self._celula = None
        elif tag == "tr" and self._linha is not None and self._tabela is not None:
            self._tabela["linhas"].append(self._linha)
            self._linha = None
        elif tag == "table":
            self._tabela = None

    def handle_data(self, data: str) -> None:
        if self._celula is not None:
            self._celula.append(data)
        if self._legenda is not None:
            self._legenda.append(data)


def _tabelas(conteudo: Any) -> _Tabelas:
    texto = conteudo.decode("utf-8") if isinstance(conteudo, bytes) else conteudo
    parser = _Tabelas()
    parser.feed(texto)
    parser.close()
    return parser


def _datas(periodo: str, ano: int) -> List[datetime.date]:
    """'1º de janeiro' -> [01/01]; '16 e 17 de fevereiro' -> [16/02, 17/02];
    '1º a 6 de janeiro' -> [01/01 ... 06/01]. Formato fora disso: não adivinha."""
    m = _UM_DIA.match(periodo)
    if m:
        return [datetime.date(ano, _mes(m.group(2)), int(m.group(1)))]
    m = _DOIS_DIAS.match(periodo)
    if m:
        mes = _mes(m.group(3))
        return [datetime.date(ano, mes, int(m.group(1))), datetime.date(ano, mes, int(m.group(2)))]
    m = _INTERVALO.match(periodo)
    if m:
        mes = _mes(m.group(3))
        inicio, fim = int(m.group(1)), int(m.group(2))
        return [datetime.date(ano, mes, n) for n in range(inicio, fim + 1)]
    raise ErroDeFonte("período da tabela geral em formato não previsto: %r" % periodo)


def baixar(rede: Cliente, ano: int) -> Tuple[bytes, bytes]:
    """Único ponto de rede do motor: devolve (página geral, página de locais)."""
    paginas = PAGINAS.get(ano)
    if paginas is None:
        raise AindaNaoPublicado("o TRT3 não tem endereço registrado para %d no motor" % ano)
    return rede.baixar(paginas["geral"]), rede.baixar(paginas["locais"])


def interpretar(conteudo_geral: Any, conteudo_locais: Any, ano: int) -> Dict[str, Any]:
    """Lê as duas páginas e devolve o calendário do ano pedido. Não usa rede."""
    texto_geral = conteudo_geral.decode("utf-8") if isinstance(conteudo_geral, bytes) else conteudo_geral
    geral = _tabelas(texto_geral)
    locais = _tabelas(conteudo_locais)

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [
        {
            "id": FONTE_GERAL,
            "url": URL_GERAL_2026,
            "descricao": "Calendário Institucional 2026 do TRT3: feriados da Justiça do Trabalho de MG, "
                         "recesso e suspensões (reproduz a Resolução Administrativa 109/2025)",
        },
        {
            "id": FONTE_LOCAIS,
            "url": URL_LOCAIS_2026,
            "descricao": "Feriados locais 2026 do TRT3 (tabela por mês; Portaria TRT3/SEGP 991/2025)",
        },
    ]

    # Página geral: precisa mostrar o ano pedido na grade mensal, senão a página é de outro ano.
    anos_na_pagina = set()
    for t in geral.tabelas:
        m = _LEGENDA_MENSAL.match(t["legenda"])
        if m:
            anos_na_pagina.add(int(m.group(2)))
    if not anos_na_pagina:
        raise ErroDeFonte("nenhuma grade mensal na página geral: o formato da página mudou")
    if ano not in anos_na_pagina:
        raise AindaNaoPublicado("a página do calendário do TRT3 não traz o ano %d" % ano)

    tabela_geral = [t for t in geral.tabelas if t["legenda"].startswith(_TABELA_GERAL)]
    if len(tabela_geral) != 1:
        raise ErroDeFonte("tabela 'Feriados da Justiça do Trabalho' não encontrada: o formato da página mudou")

    for linha in tabela_geral[0]["linhas"]:
        if len(linha) != 3 or linha[0] == _CABECALHO_GERAL:
            continue
        periodo, _dia_da_semana, motivo = linha
        if _MARCA_LOCAL in motivo:
            # DUVIDA: Corpus Christi (04/06) é local (RA 109 II e III; ficha). A linha também traz
            # "Suspensão de expediente no dia 5 ... nas localidades". Ambos vêm da tabela de locais.
            continue
        tipo = "recesso" if motivo.startswith("Recesso") else "sem_expediente"
        # DUVIDA: 18/02 (Cinzas): a RA 109 diz "suspensão de expediente em todos os órgãos", mas
        # sem horário; a página só traz "Cinzas". Tratado como dia inteiro (sem_expediente).
        for data in _datas(periodo, ano):
            cal["geral"].append(dia(data, tipo, motivo, FONTE_GERAL))

    # 1º de maio: presente no texto da página (parágrafo entre os meses), fora da tabela geral.
    if "Dia do Trabalhador" not in texto_geral:
        raise ErroDeFonte("'Dia do Trabalhador' não encontrado na página geral: o formato mudou")
    primeiro_maio = datetime.date(ano, 5, 1)
    if not any(d["data"] == primeiro_maio.isoformat() for d in cal["geral"]):
        cal["geral"].append(dia(primeiro_maio, "sem_expediente", "Dia do Trabalhador", FONTE_RA))
        cal["fontes"].append({
            "id": FONTE_RA,
            "url": URL_GERAL_2026,
            "descricao": "Resolução Administrativa 109/2025 (Art. 1º da Lei 662/1949): o 1º de maio "
                         "não está na tabela da página, só no texto",
        })

    total_locais = 0
    for tabela in locais.tabelas:
        m = _LEGENDA_LOCAL.match(tabela["legenda"])
        if not m or int(m.group(2)) != ano:
            continue
        mes = _mes(m.group(1))
        for linha in tabela["linhas"]:
            if len(linha) != 3 or not linha[0].isdigit():
                continue  # cabeçalho ("Data | Localidade | Motivo") ou linha vazia
            data = datetime.date(ano, mes, int(linha[0]))
            localidade, motivo = linha[1], linha[2]
            cal["locais"].setdefault(normalizar_local(localidade), []).append(
                dia(data, "sem_expediente", motivo, FONTE_LOCAIS)
            )
            total_locais += 1

    if total_locais == 0:
        raise ErroDeFonte("nenhuma linha de feriado local em %d: o formato da página mudou" % ano)
    if not cal["geral"]:
        raise ErroDeFonte("nenhum dia geral lido: o formato da página mudou")
    return ordenar(cal)


class MotorTRT3(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = PARCIAL
    esperado = {
        # A ficha não traz contagem de dias gerais. Lidos 40 entradas em 2026 (1/01 e 25/12 contam
        # duas vezes: feriado e recesso). 30 é um piso conservador.
        "min_geral": 30,
        "min_locais": 66,   # localidades distintas na tabela, na ficha
        "ancoras": {        # só dias GERAIS, conferidos à mão na ficha
            "2026-02-16": "Carnaval",
            "2026-02-17": "Carnaval",
            "2026-02-18": "Cinzas",
            "2026-04-20": "Suspensão de expediente em decorrência do feriado de Tiradentes",
            "2026-04-21": "Tiradentes",
            "2026-08-14": "Dia dos Cursos Jurídicos (movido do dia 11)",
            "2026-10-30": "Dia do Servidor Público (movido do dia 28)",
            "2026-12-08": "Dia da Justiça",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        geral, locais = baixar(rede, ano)
        return interpretar(geral, locais, ano)


MOTOR = MotorTRT3()
