"""Motor do TJDFT (Tribunal de Justiça do Distrito Federal e dos Territórios).

Fonte (ver docs/fichas/TJDFT.md):

  Tabela HTML "Feriados e expedientes suspensos" do portal do tribunal
  (https://www.tjdft.jus.br/feriados-e-expedientes-suspensos). Uma linha por dia, colunas
  "Data | Descrição", data dd/mm/aaaa. Traz feriados, recesso, pontos facultativos e as
  suspensões publicadas durante o ano. A portaria (Portaria Conjunta 105/2025, no SEI) entra
  só como fonte de comprovação: nenhum dia do calendário sai do texto dela.

O DF é uma jurisdição só: tudo vai em `geral`. `locais` tem uma chave única, "DISTRITO FEDERAL",
com lista vazia, para o app ter o que listar.

Não entra aqui: a regra de prorrogação de prazo que cai em feriado (Portaria Conjunta 105/2025,
art. 5º): é regra de contagem do app, não um dia do calendário. Também fica de fora o calendário
dos ofícios extrajudiciais (art. 3º da portaria), que tem lista própria e não é o calendário
judicial.
"""
from __future__ import annotations

import datetime
import html
import re
from typing import Any, Dict, List, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

URL_PAGINA = "https://www.tjdft.jus.br/feriados-e-expedientes-suspensos"
URL_PORTARIA = ("https://sei.tjdft.jus.br/sei/publicacoes/controlador_publicacoes.php"
                "?acao=publicacao_visualizar&id_orgao_publicacao=0&id_documento=5146952")
LOCAL_UNICO = "DISTRITO FEDERAL"

_LINHA = re.compile(r"<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>", re.S)
_TABELA = re.compile(r'<table summary="Tabela de Feriados"[^>]*>(.*?)</table>', re.S)


def _texto(celula: str) -> str:
    """Tira as tags e as entidades HTML, e junta os espaços."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", celula)).split())


def _data_br(texto: str) -> datetime.date:
    d, m, a = texto.split("/")
    return datetime.date(int(a), int(m), int(d))


def _tipo(motivo: str) -> str:
    """Efeito do dia, pelo que a tabela diz. Nunca inventa suspensão de prazo."""
    if motivo.upper().startswith("RECESSO FORENSE"):
        return "recesso"
    # DUVIDA: feriado, véspera, Natal e ponto facultativo viram sem_expediente, igual aos feriados.
    # A ficha manda tratar pontos facultativos assim (o site chama de "expedientes suspensos") e
    # deixar para revisão: 20/04, 04/06, 05/06, 29/06, 10/08, 30/10, 07/12, 24/12 e 31/12 de 2026.
    # Não viram suspensao_prazo.
    return "sem_expediente"


def baixar(rede: Cliente) -> bytes:
    """Rede: a tabela da página. Única chamada de rede do motor."""
    return rede.baixar(URL_PAGINA)


def interpretar(conteudo: bytes, ano: int) -> Dict[str, Any]:
    """Do HTML da tabela para o calendário. Puro: sem rede, para os testes usarem a fixture."""
    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = conteudo.decode("iso-8859-1")  # a página é utf-8; o ISO-8859-1 cobre o caso do SEI

    tabela = _TABELA.search(texto)
    if not tabela:
        raise ErroDeFonte("tabela 'Tabela de Feriados' não encontrada na página do TJDFT")

    cal = calendario_vazio("TJDFT", ano)
    cal["fontes"] = [
        {"id": "tabela", "url": URL_PAGINA,
         "descricao": "Tabela 'Feriados e expedientes suspensos' do TJDFT (feriados, recesso, pontos facultativos e suspensões do ano)"},
        {"id": "portaria", "url": URL_PORTARIA,
         "descricao": "Portaria Conjunta 105/2025 do TJDFT (comprovação; a tabela é a fonte dos dias)"},
    ]
    cal["locais"] = {normalizar_local(LOCAL_UNICO): []}

    lidas: List[Tuple[datetime.date, str]] = []
    for celula_data, celula_desc in _LINHA.findall(tabela.group(1)):
        data_txt = _texto(celula_data)
        motivo = _texto(celula_desc)
        try:
            data = _data_br(data_txt)
        except (ValueError, TypeError):
            raise ErroDeFonte("data que não está em dd/mm/aaaa na tabela do TJDFT: %r" % data_txt)
        if data.year != ano:
            continue  # a tabela é de um ano; linha de outro ano não entra
        if not motivo:
            raise ErroDeFonte("linha sem descrição na tabela do TJDFT: %s" % data_txt)
        lidas.append((data, motivo))

    if not lidas:
        raise AindaNaoPublicado("a tabela do TJDFT ainda não traz dias de %d" % ano)

    for data, motivo in lidas:
        cal["geral"].append(dia(data, _tipo(motivo), motivo, "tabela"))

    return ordenar(cal)


class MotorTJDFT(Motor):
    sigla = "TJDFT"
    precisa_ip_brasil = False  # testado do GitHub: a tabela abre (200), ver docs/fichas/TJDFT.md
    parcial = (
        "Fora: a regra de prorrogação de prazo que cai em feriado (Portaria Conjunta 105/2025, art. 5º), "
        "que é regra de contagem e não um dia; o calendário dos ofícios extrajudiciais (art. 3º da "
        "portaria, com outra lista, p. ex. 18/02 só até 12h); e o endereço do SEI, que não foi testado "
        "no workflow da nuvem (a tabela basta para o motor). Não há dia parcial no calendário judicial."
    )
    esperado = {
        # 43 dias lidos da fixture de 2026; a ficha diz "cerca de 45 linhas". Piso abaixo disso.
        "min_geral": 40,
        "min_locais": 1,
        # Conferidas à mão na ficha (tabela da página e art. 2º da Portaria Conjunta 105/2025).
        "ancoras": {
            "2026-01-01": "Confraternização Universal",
            "2026-02-16": "Carnaval (feriado forense)",
            "2026-02-17": "Carnaval (feriado forense)",
            "2026-02-18": "Quarta-feira de Cinzas (feriado forense)",
            "2026-04-20": "Ponto facultativo (Portaria Conjunta 105/2025)",
            "2026-10-30": "Dia do Servidor transferido do 28/10",
            **{"2026-12-%02d" % n: "Recesso forense" for n in (20, 21, 22, 23, 26, 27, 28, 29, 30)},
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede), ano)


MOTOR = MotorTJDFT()
