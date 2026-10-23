"""Motor do TRT11 (Tribunal Regional do Trabalho da 11ª Região, Amazonas e Roraima).

COBERTURA PARCIAL. Ver docs/fichas/TRT11.md. Este motor lê SÓ a página de suspensões do portal
(Joomla/iCagenda, eventos com categoria):

  https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-susp

  - A lista traz uma linha por data, com categoria "Suspensão de Prazos" ou "Suspensão de
    Expediente", em ordem decrescente de data. Os eventos de 2026 estão na página 1; se a
    última linha lida ainda for do ano pedido, o motor pede a página seguinte.
  - A lista mostra só o INÍCIO de um evento de vários dias. Para "Suspensão de Prazos", o motor
    abre a página do próprio evento e lê o fim do período (ex.: 07 a 20/01/2026).

Não entram neste motor (ver `parcial`): feriados nacionais, estaduais e municipais; o calendário
anual em PDF (barrado pelo robots.txt na nuvem: não é usado); o dia parcial de 29/06/2026
(Portaria 238/2026, Copa); suspensões de Varas e Fóruns locais.

Tipos (ver a ficha):
  "Suspensão dos prazos, audiências e sessões"  -> suspensao_prazo, um dia por data do período
  "Suspensão do expediente RA nº 322/2025"      -> sem_expediente, com DUVIDA (ver abaixo)
"""
from __future__ import annotations

import datetime
import html
import re
import urllib.parse
from typing import Any, Dict, List, Tuple

from ..modelo import calendario_vazio, dia, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT11"
URL_BASE = "https://portal.trt11.jus.br"
URL_LISTA = URL_BASE + "/index.php/sociedades/calendarios/calendario-susp"
FONTE_ID = "suspensoes"
CAT_PRAZO = "Suspensão de Prazos"
CAT_EXPEDIENTE = "Suspensão de Expediente"

# Abreviação de três letras (lista: "Abr", "Mai") ou nome por extenso (evento: "Março").
MESES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
         "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}

_EVENTO = re.compile(r'<div class="ic-event.*?</h2>', re.S)
_DIA = re.compile(r'class="ic-day">\s*(\d{1,2})\s*<')
_MES = re.compile(r'class="ic-month">\s*(\w+)\s*<')
_ANO = re.compile(r'class="ic-year">\s*(\d{4})\s*<')
_CAT = re.compile(r'class="ic-cat">\s*(.*?)\s*</div>', re.S)
_LINK = re.compile(r'<a href="([^"]+)" title="([^"]+)"')
_PAGINAS = re.compile(r"Página (\d+) / (\d+)")
_PERIODO = re.compile(
    r'ic-period-startdate">[^<]*?(\d{1,2}) de (\w+) de (\d{4})</span>'
    r'.*?ic-period-enddate">[^<]*?(\d{1,2}) de (\w+) de (\d{4})</span>',
    re.S,
)
_LOCAL = re.compile(r"\bVara\b|\bFórum\b|\bForo\b", re.I)


def _texto(corpo: bytes) -> str:
    """Bytes da página para texto: entidades HTML desfeitas e espaço não-quebrável trocado."""
    try:
        bruto = corpo.decode("utf-8")
    except UnicodeDecodeError:
        raise ErroDeFonte("página do TRT11 não está em utf-8")
    return html.unescape(bruto).replace("\xa0", " ")


def _mes(nome: str) -> int:
    mes = MESES.get(nome.strip().lower()[:3])
    if mes is None:
        raise ErroDeFonte("mês não reconhecido na página do TRT11: %r" % nome)
    return mes


def _eventos(texto: str) -> List[Tuple[datetime.date, str, str, str]]:
    """(data de início, categoria, título, href) de cada linha da lista, na ordem da página."""
    saida = []
    for bloco in _EVENTO.findall(texto):
        d, m, a = _DIA.search(bloco), _MES.search(bloco), _ANO.search(bloco)
        cat, link = _CAT.search(bloco), _LINK.search(bloco)
        if not (d and m and a and cat and link):
            raise ErroDeFonte("evento da lista do TRT11 em formato não previsto")
        data = datetime.date(int(a.group(1)), _mes(m.group(1)), int(d.group(1)))
        saida.append((data, " ".join(cat.group(1).split()), " ".join(link.group(2).split()), link.group(1)))
    return saida


def _periodo(texto: str) -> Tuple[datetime.date, datetime.date]:
    """Início e fim do período no bloco 'Datas' da página do evento."""
    m = _PERIODO.search(texto)
    if not m:
        raise ErroDeFonte("período do evento não encontrado na página do TRT11")
    ini = datetime.date(int(m.group(3)), _mes(m.group(2)), int(m.group(1)))
    fim = datetime.date(int(m.group(6)), _mes(m.group(5)), int(m.group(4)))
    return ini, fim


def baixar(rede: Cliente, ano: int) -> Dict[str, Any]:
    """Única parte com rede: páginas da lista (até cobrir o ano) e página de cada evento de
    'Suspensão de Prazos' do ano (para ler o fim do período)."""
    listas: List[bytes] = []
    eventos: List[Tuple[datetime.date, str, str, str]] = []
    pagina, total = 1, 1
    while True:
        url = URL_LISTA if pagina == 1 else "%s?page=%d" % (URL_LISTA, pagina)
        corpo = rede.baixar(url)
        listas.append(corpo)
        texto = _texto(corpo)
        if pagina == 1:
            m = _PAGINAS.search(texto)
            total = int(m.group(2)) if m else 1
        lidos = _eventos(texto)
        eventos.extend(lidos)
        # Ordem decrescente: quando a última linha já é de ano anterior, o ano pedido acabou.
        if not lidos or pagina >= total or min(e[0].year for e in lidos) < ano:
            break
        pagina += 1

    detalhes: Dict[str, bytes] = {}
    for data, cat, _titulo, href in eventos:
        if data.year == ano and cat == CAT_PRAZO:
            url = urllib.parse.urljoin(URL_BASE, href.split("?")[0])
            detalhes[url] = rede.baixar(url)
    return {"listas": listas, "detalhes": detalhes}


def interpretar(conteudo: Dict[str, Any], ano: int) -> Dict[str, Any]:
    """Do conteúdo baixado (ver `baixar`) para o calendário do ano. Puro: sem rede."""
    eventos: List[Tuple[datetime.date, str, str, str]] = []
    for corpo in conteudo["listas"]:
        eventos.extend(_eventos(_texto(corpo)))

    datas = [e[0] for e in eventos]
    if any(a < b for a, b in zip(datas, datas[1:])):
        raise ErroDeFonte("a lista do TRT11 não está mais em ordem decrescente: a paginação não é confiável")

    do_ano = [e for e in eventos if e[0].year == ano]
    if not do_ano:
        raise AindaNaoPublicado("a página de suspensões do TRT11 ainda não traz eventos de %d" % ano)

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{
        "id": FONTE_ID,
        "url": URL_LISTA,
        "descricao": "Página de suspensões do TRT11 (calendário iCagenda): suspensão de prazos e de expediente",
    }]
    cal["locais"] = {}

    for data, cat, titulo, href in do_ano:
        if _LOCAL.search(titulo):
            # Evento de Vara ou Fórum: não é do tribunal inteiro e a fonte não diz a comarca. Parar.
            raise ErroDeFonte("evento local no calendário do TRT11 (não tratado): %r" % titulo)
        if cat == CAT_EXPEDIENTE:
            # DUVIDA: "suspensão do expediente" (RA 322/2025) não diz se suspende prazo. O PDF anual
            # (inacessível) chama de "Ponto Facultativo". Tratado como sem_expediente, o mais
            # conservador que não inventa suspensão de prazo. Quem revisa confirma.
            cal["geral"].append(dia(data, "sem_expediente", titulo, FONTE_ID))
        elif cat == CAT_PRAZO:
            url = urllib.parse.urljoin(URL_BASE, href.split("?")[0])
            if url not in conteudo["detalhes"]:
                raise ErroDeFonte("página do evento %s não foi lida: não sei o fim do período" % url)
            ini, fim = _periodo(_texto(conteudo["detalhes"][url]))
            if ini != data:
                raise ErroDeFonte("início do evento na lista (%s) diferente da página (%s)" % (data, ini))
            if fim < ini:
                raise ErroDeFonte("fim do período antes do início: %s" % titulo)
            d = ini
            while d <= fim:
                cal["geral"].append(dia(d, "suspensao_prazo", titulo, FONTE_ID))
                d += datetime.timedelta(days=1)
        else:
            raise ErroDeFonte("categoria nova na lista do TRT11: %r" % cat)

    return ordenar(cal)


class MotorTRT11(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False  # não testado: a nuvem abriu a página com 200 (ficha)
    parcial = (
        "COBERTURA PARCIAL: só a página de suspensões do portal (suspensão de prazos e de expediente, "
        "de 2026 em diante na lista). FORA: (1) feriados nacionais, estaduais e municipais de Manaus, "
        "Boa Vista e demais municípios: só estão no calendário anual em PDF, que o robots.txt barra na "
        "nuvem (não é usado); (2) o dia parcial de 29/06/2026 (Copa, expediente até 11h, Portaria "
        "238/2026/SGP), que não consta na lista; (3) suspensões de Varas e Fóruns locais, que o motor "
        "recusa e interrompe; (4) alterações feitas depois da leitura; (5) o efeito do 'Ponto Facultativo' "
        "(RA 322/2025) está em DUVIDA: tratado como sem_expediente até revisão. Sem locais."
    )
    esperado = {
        # Contagem lida da fixture (14 dias de 07 a 20/01 + 3 dias de 'Suspensão do expediente').
        # A ficha não traz contagem.
        "min_geral": 17,
        "min_locais": 0,
        "ancoras": {  # conferidas à mão na ficha, na página de suspensões
            "2026-01-07": "Suspensão dos prazos, audiências e sessões (início)",
            "2026-01-20": "Suspensão dos prazos, audiências e sessões (fim)",
            "2026-04-20": "Suspensão do expediente RA nº 322/2025",
            "2026-06-05": "Suspensão do expediente RA nº 322/2025",
            "2026-08-10": "Suspensão do expediente RA nº 322/2025",
        },
        "exige_recesso": False,  # a fonte não traz recesso
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede, ano), ano)


MOTOR = MotorTRT11()
