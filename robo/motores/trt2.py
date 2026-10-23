"""Motor do TRT2 (Tribunal Regional do Trabalho da 2ª Região: São Paulo, Grande SP e Baixada Santista).

Fonte única, oficial: a página "Feriados e Suspensões de Expediente" da agenda do portal
(https://ww2.trt2.jus.br/servicos/agenda/feriados-e-suspensoes-de-expediente). Ver docs/fichas/TRT2.md.

A página traz os 12 meses numa só, em HTML, sem JavaScript. Cada dia com evento é um
<span class="label-calendar badge-*"> cujo atributo `title` tem os textos dos eventos separados
por " / ", e um link com dia, mês e ano. Os dias de meses vizinhos repetem eventos: deduplica
por (data, texto). A cor (badge-*) não decide o efeito: o texto decide.

Classificação, pelo texto de cada evento:
  "Recesso"                                         -> recesso (geral)
  "Suspensão dos prazos processuais ... todos ..."  -> suspensao_prazo (geral)
  "... em todos os órgãos que integram o TRT ..."   -> sem_expediente (geral), salvo as datas em
                                                       DATAS_SEM_DECISAO
  "... no Município de X" (feriado, aniversário)    -> sem_expediente no local X
  "Fórum ...", "12ª Vara ...", "Edifício Sede ..."  -> órgão específico: fica de fora (ver `parcial`)
Qualquer texto fora desses padrões levanta ErroDeFonte: é melhor parar do que adivinhar.

A página só mostra o ano de que trata: se o ano pedido não tiver nenhum dia, levanta
AindaNaoPublicado.
"""
from __future__ import annotations

import datetime
import html
import re
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT2"
URL = "https://ww2.trt2.jus.br/servicos/agenda/feriados-e-suspensoes-de-expediente"
FONTE_ID = "agenda"

# DUVIDA: 18/02/2026 (Quarta-feira de Cinzas) traz "Suspensão de expediente em todos os órgãos"
# (Portaria n. 50/GP). A ficha não decide se o expediente é pleno ou parcial, nem se o prazo corre.
# Por isso o dia fica de fora de `geral` e vai para `parcial`, até decisão do revisor.
DATAS_SEM_DECISAO = {"2026-02-18"}

# Eventos de órgão específico (fórum, vara, edifício). O texto curto não diz o efeito.
_ORGAO = re.compile(r"^(Fórum|12ª Vara|Edifício)")

_CLASSE = re.compile(r"^badge-[a-z]+")
_TITULO = re.compile(r'title="([^"]*)"')
_LINK_DATA = re.compile(r"day%5D=(\d{1,2})&amp;tx_calendarize_calendar%5Bmonth%5D=(\d{1,2})&amp;tx_calendarize_calendar%5Byear%5D=(\d{4})")
_MUNICIPIO = re.compile(r"Município de (.+?)(?:\s*\(sede\))?$", re.I)
_SEPARADOR = re.compile(r"\s*/\s*")


def _limpo(texto: str) -> str:
    return " ".join(texto.split())


def _classificar(texto: str, data: datetime.date) -> Tuple[str, Optional[str], Optional[str]]:
    """Devolve (onde, local, tipo). onde: "geral", "local" ou "fora". Puro."""
    if texto == "Recesso":
        return "geral", None, "recesso"

    m = _MUNICIPIO.search(texto)
    if m:
        # DUVIDA: feriado religioso e aniversário municipal são marcados como dia sem expediente
        # (badge-success), mas a fonte não diz se o fórum fecha. Tratados como sem_expediente
        # no local, igual aos feriados municipais. Vale só no município, nunca no tribunal todo.
        return "local", normalizar_local(m.group(1)), "sem_expediente"

    if "em todos os órgãos" in texto:
        if texto.startswith("Suspensão dos prazos processuais"):
            return "geral", None, "suspensao_prazo"
        if data.isoformat() in DATAS_SEM_DECISAO and texto.startswith("Suspensão de expediente"):
            return "fora", None, None
        if texto.startswith(("Suspensão de expediente", "Feriado", "Antecipação", "Transferência")):
            return "geral", None, "sem_expediente"
        raise ErroDeFonte("evento de jurisdição toda em formato não previsto: %r" % texto)

    if _ORGAO.match(texto):
        return "fora", None, None

    raise ErroDeFonte("evento não reconhecido na agenda do TRT2: %r" % texto)


def baixar(rede: Cliente) -> bytes:
    """Único ponto de rede do motor."""
    return rede.baixar(URL)


def interpretar(conteudo: Any, ano: int) -> Dict[str, Any]:
    """Lê o HTML da página (bytes ou texto) e devolve o calendário do ano pedido. Não usa rede."""
    texto = conteudo.decode("utf-8") if isinstance(conteudo, bytes) else conteudo

    partes = texto.split('<span class="label-calendar ')[1:]
    if not partes:
        raise ErroDeFonte("nenhum evento encontrado na agenda do TRT2: o formato da página mudou")

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{
        "id": FONTE_ID,
        "url": URL,
        "descricao": "Página 'Feriados e Suspensões de Expediente' da agenda do TRT2 (calendário do ano)",
    }]

    vistos = set()
    dias_do_ano = 0
    for parte in partes:
        classe = _CLASSE.match(parte)
        titulo = _TITULO.search(parte[:parte.find(">")])
        link = _LINK_DATA.search(parte)
        if not (classe and titulo and link):
            raise ErroDeFonte("evento da agenda do TRT2 sem classe, título ou data: o formato mudou")
        d, m, a = (int(x) for x in link.groups())
        data = datetime.date(a, m, d)
        if data.year != ano:
            continue  # meses vizinhos trazem datas de outro ano: não entram

        for evento in _SEPARADOR.split(_limpo(html.unescape(titulo.group(1)))):
            if not evento or (data.isoformat(), evento) in vistos:
                continue
            vistos.add((data.isoformat(), evento))
            dias_do_ano += 1
            onde, local, tipo = _classificar(evento, data)
            if onde == "fora":
                continue
            item = dia(data, tipo, evento, FONTE_ID)
            if onde == "geral":
                cal["geral"].append(item)
            else:
                cal["locais"].setdefault(local, []).append(item)

    if dias_do_ano == 0:
        raise AindaNaoPublicado("a agenda do TRT2 ainda não traz eventos de %d" % ano)
    return ordenar(cal)


class MotorTRT2(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False  # a página abre do GitHub (200), ver docs/fichas/TRT2.md
    parcial = (
        "Fora do calendário: (a) eventos de órgão específico (fóruns de Arujá, Cubatão, Zona Sul, Zona Leste; "
        "12ª Vara do Trabalho de São Paulo; Edifício Sede), cujo efeito só aparece na página de detalhe do dia; "
        "(b) 18/02/2026, Suspensão de expediente em todos os órgãos (Portaria n. 50/GP), sem decisão de efeito; "
        "(c) o art. 775-A da CLT (suspensão de 20/12 a 20/01) não é lançado pelo TRT2 como suspensão geral: "
        "o app precisa aplicar por fora; 07 a 20/01 não aparecem na grade. "
        "Locais: a página não traz lista fechada de municípios; só entram os que têm evento em 2026. "
        "Indisponibilidade de sistema fica em outra consulta, não lida."
    )
    esperado = {
        # A ficha não traz contagem. Contagem lida da fixture de 2026: 47 dias gerais. Piso abaixo disso.
        "min_geral": 40,
        "min_locais": 30,
        "ancoras": {        # só dias GERAIS: a validação confere em `geral`
            "2026-01-01": "Recesso",
            "2026-01-06": "Recesso",
            "2026-01-21": "Suspensão dos prazos processuais (Portaria n. 15/GP.CR)",
            "2026-01-22": "Suspensão dos prazos processuais (Portaria n. 15/GP.CR)",
            "2026-01-23": "Suspensão dos prazos processuais (Portaria n. 15/GP.CR)",
            "2026-02-16": "Feriado de Carnaval em todos os órgãos",
            "2026-02-17": "Feriado de Carnaval em todos os órgãos",
            "2026-04-20": "Suspensão de expediente em todos os órgãos (Portaria n. 50/GP)",
            "2026-04-21": "Feriado do Dia de Tiradentes em todos os órgãos",
            "2026-06-05": "Suspensão de expediente em todos os órgãos",
            "2026-12-20": "Recesso",
            "2026-12-31": "Recesso",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede), ano)


MOTOR = MotorTRT2()
