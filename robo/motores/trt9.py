"""Motor do TRT9 (Tribunal Regional do Trabalho da 9ª Região, Paraná).

Fonte única, oficial: "Calendário do Judiciário e dos feriados locais"
(https://www.trt9.jus.br/institucional/calendario.xhtml). A página é HTML (JSF/PrimeFaces) com
uma tabela já no HTML, do ano corrente, sem JavaScript. Colunas:
`Data Feriado | Descrição | Abrangência | Origem | Legislação`. Ver docs/fichas/TRT9.md.

  - Abrangência "Nacional" e "Estadual" valem para o tribunal inteiro: vão em `geral`.
    "Estadual" também traz suspensões de prazo avulsas (Portarias Presid-Correg).
  - Abrangência "Municipal": a chave é a Origem ("PARANAVAI-PR"), em `locais`.
  - Abrangência "Órgão Julgador": a chave é a Origem (nome da unidade), em `locais`.
    Nunca vai para `geral`.

O tipo do dia sai do TEXTO da Descrição (a tabela não tem coluna de tipo):
  "Recesso Judiciário"                                  -> recesso
  "Suspensão ... prazo(s)" (sem "expediente")           -> suspensao_prazo
  "Suspensão de expediente e prazos processuais"        -> sem_expediente
  qualquer outra (feriados, padroeiros, transferências) -> sem_expediente
"""
from __future__ import annotations

import datetime
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT9"
URL = "https://www.trt9.jus.br/institucional/calendario.xhtml"
FONTE_ID = "calendario"

# Abrangências que valem para o tribunal inteiro (vão em `geral`).
ABRANGENCIAS_GERAIS = ("Nacional", "Estadual")
# Abrangências que são locais (vão em `locais`, pela Origem).
ABRANGENCIAS_LOCAIS = ("Municipal", "Órgão Julgador")

# DUVIDA: 18/02/2026 "Quarta-Feira de Cinzas" (Nacional, Art. 292 "b" do Reg. Interno). A tabela
# não diz se é expediente parcial, e a ficha proíbe lançar como sem_expediente sem revisor.
# Como não há outro tipo que caiba sem inventar horário, o dia NÃO entra. Quem revisa decide.
DUVIDA_NAO_LANCADOS = ("Quarta-Feira de Cinzas",)

_DATA = re.compile(r"\d{2}/\d{2}/\d{4}$")


class _Linhas(HTMLParser):
    """Coleta o texto de cada célula <td> de cada linha <tr>, na ordem do HTML.

    Cabeçalhos (<th>) geram linhas vazias, que `interpretar` ignora pela forma.
    """

    def __init__(self) -> None:
        super().__init__()
        self.linhas: List[List[str]] = []
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
        if self._celula is not None:
            self._celula.append(data)


def _tipo(descricao: str) -> str:
    """Tipo do dia a partir do texto da Descrição (ver o cabeçalho do módulo)."""
    d = descricao.lower()
    if descricao == "Recesso Judiciário":
        return "recesso"
    if "suspens" in d and "prazo" in d:
        if "expediente" in d:
            # Portarias Presid-Correg 2/2026 (20/04 e 05/06): expediente E prazos. O dia não é
            # de expediente e o prazo não corre: é o tipo mais protetivo que cabe.
            return "sem_expediente"
        return "suspensao_prazo"
    return "sem_expediente"  # feriado, padroeiro, aniversário, transferência de feriado


def baixar(rede: Cliente) -> bytes:
    """Único ponto de rede do motor."""
    return rede.baixar(URL)


def interpretar(conteudo: Any, ano: int) -> Dict[str, Any]:
    """Lê o HTML da página (bytes ou texto) e devolve o calendário do ano pedido. Não usa rede."""
    texto = conteudo.decode("utf-8") if isinstance(conteudo, bytes) else conteudo
    parser = _Linhas()
    parser.feed(texto)
    parser.close()

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{
        "id": FONTE_ID,
        "url": URL,
        "descricao": "Calendário do Judiciário e dos feriados locais do TRT9 (tabela da página)",
    }]

    total_datadas = 0
    for celulas in parser.linhas:
        if len(celulas) != 5 or not _DATA.match(celulas[0]):
            continue  # cabeçalho, linha vazia ou formato que não é de dado
        try:
            data = datetime.datetime.strptime(celulas[0], "%d/%m/%Y").date()
        except ValueError:
            raise ErroDeFonte("data inválida na tabela: %r" % celulas[0])
        total_datadas += 1
        if data.year != ano:
            continue
        descricao, abrangencia, origem = celulas[1], celulas[2], celulas[3]
        if not descricao:
            raise ErroDeFonte("linha sem descrição em %s" % celulas[0])
        if descricao in DUVIDA_NAO_LANCADOS:
            continue

        item = dia(data, _tipo(descricao), descricao, FONTE_ID)
        if abrangencia in ABRANGENCIAS_GERAIS:
            cal["geral"].append(item)
        elif abrangencia in ABRANGENCIAS_LOCAIS:
            if not origem:
                raise ErroDeFonte("local sem Origem em %s: %r" % (celulas[0], descricao))
            cal["locais"].setdefault(normalizar_local(origem), []).append(item)
        else:
            raise ErroDeFonte("abrangência desconhecida %r em %s" % (abrangencia, celulas[0]))

    if total_datadas == 0:
        raise ErroDeFonte("nenhuma linha de data encontrada na tabela: o formato da página mudou")
    if not cal["geral"] and not any(cal["locais"].values()):
        raise AindaNaoPublicado("o TRT9 ainda não publicou dias de %d na página do calendário" % ano)
    return ordenar(cal)


class MotorTRT9(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = (
        "Fica de fora ou incompleto: (1) 18/02/2026 Quarta-Feira de Cinzas, por dúvida de efeito "
        "(ver DUVIDA no código e na ficha); (2) 29/06/2026 sai só como suspensao_prazo: a Portaria "
        "Presid-Correg 5/2026, citada na 7/2026, encerrou o expediente às 12h e isso não é lido; "
        "(3) feriados e suspensões municipais ou de unidades que não estão nesta tabela (ela só traz "
        "quem tem dia próprio, não todas as varas); (4) atos publicados depois da leitura que não "
        "apareçam na tabela; (5) horário de expediente parcial, que a tabela não informa."
    )
    esperado = {
        # 61 linhas Nacional + Estadual em 2026 na fixture, menos a DUVIDA (18/02): 60. Piso conservador.
        "min_geral": 50,
        "min_locais": 40,   # origens distintas (municípios e unidades) na fixture de 23/10/2026
        "ancoras": {        # só dias GERAIS: a validação confere em `geral`
            "2026-01-01": "Recesso Judiciário (Lei 5.010/1966)",
            "2026-01-07": "Suspensão de prazo - Art. 220 CPC",
            "2026-01-20": "Suspensão de prazo - Art. 220 CPC",
            "2026-01-21": "Suspensão de prazos 21 a 23/01 (Portaria Presid-Correg 6/2025)",
            "2026-01-23": "Suspensão de prazos 21 a 23/01 (Portaria Presid-Correg 6/2025)",
            "2026-04-20": "Suspensão de expediente e prazos processuais (Portaria Presid-Correg 2/2026)",
            "2026-04-21": "Tiradentes (Nacional)",
            "2026-06-04": "Corpus Christi (Nacional)",
            "2026-06-05": "Suspensão de expediente e prazos processuais (Portaria Presid-Correg 2/2026)",
            "2026-06-29": "Suspensão de Prazos - jogo da copa 2026 (Portaria Presid-Correg 7/2026)",
            "2026-08-14": "Transferência do feriado de 11/8 (Portaria Presid-Correg 1/2025)",
            "2026-10-30": "Transferência do feriado do Dia do Servidor Público (Portaria Presid-Correg 1/2025)",
            "2026-12-18": "Transferência do feriado de 8/12 (Portaria Presid-Correg 1/2025)",
            "2026-12-31": "Recesso Judiciário (Lei 5.010/1966)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede), ano)


MOTOR = MotorTRT9()
