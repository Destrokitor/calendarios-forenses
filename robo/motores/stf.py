"""Motor do STF (Supremo Tribunal Federal). Tribunal único, sem locais (chave "BRASÍLIA").

Fontes oficiais (ficha: docs/fichas/STF.md). Todas abrem na nuvem, exceto as duas marcadas:

  calendario   Calendário oficial 2026 (PDF com texto): recesso de 20/12/2026 (o lado de 2027
               não entra aqui).
  portaria_189 Portaria GDG 189/2025: feriados (art. 1º, incisos) e pontos facultativos (§ 1º).
  portaria_250 Portaria GDG 250/2025: recesso de 20/12/2025 a 06/01/2026 e suspensão de prazos
               até 31/01/2026 (art. 1º e 4º).
  portaria_124 Portaria GDG 124/2026: suspensão de prazos de 2 a 31/07/2026 (art. 1º).
  portaria_146 Portaria GDG 146/2026: ponto facultativo em 29/06/2026, prazos prorrogados
               para 30/06 (art. 1º e 3º).   # DUVIDA: URL NÃO verificada na nuvem (padrão da ficha).
  portaria_112 Portaria GDG 112/2026: expediente de 24/06/2026, das 11h às 18h (art. 1º).
               # DUVIDA: URL NÃO verificada na nuvem (padrão da ficha).

Efeito de cada item:
  - feriado da Portaria 189 (incisos I a XII de 2026) -> sem_expediente;
  - recesso forense -> recesso;
  - suspensão de prazos (Portarias 250 e 124) -> suspensao_prazo;
  - ponto facultativo de 29/06 (Portaria 146, com prorrogação expressa) -> sem_expediente;
  - expediente reduzido (24/06, Portaria 112; Quarta-feira de Cinzas até as 14h) -> parcial.

Não entra (conservador: marcar ponto como sem expediente prorrogaria prazos sem a fonte dizer
isso; deixar de marcar pode antecipar um vencimento, o que é o lado seguro para o advogado):
  pontos facultativos da Portaria 189 (§ 1º, II a VII: 20/04, 04/06, 05/06, 10/08, 30/10, 07/12).
  Ver `parcial` e a DUVIDA abaixo.

Ano 2027: a Portaria 189 traz só os feriados de 2027, sem recesso de dez/2027 nem suspensões.
Levantar o calendário de 2027 pela metade seria perigoso, então o motor espera a fonte do ano
(AindaNaoPublicado) até que haja um calendário oficial de 2027.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "STF"
BASE_NORMA = "https://www.stf.jus.br/arquivo/norma/"

# id da fonte -> (URL, descrição). O id é o que cada dia aponta em `fonte`.
FONTES: Dict[str, Tuple[str, str]] = {
    "calendario": ("http://www.stf.jus.br/arquivo/cms/processoCalendarioStf/anexo/CalendarioSTFOficial2026.pdf",
                   "Calendário oficial 2026 do STF (PDF, versão de 12/11/2025)"),
    "portaria_189": (BASE_NORMA + "portariadg189-2025.pdf",
                     "Portaria GDG 189/2025 (feriados e pontos facultativos de jan/2026 a set/2027)"),
    "portaria_250": (BASE_NORMA + "portariadg250-2025.pdf",
                     "Portaria GDG 250/2025 (recesso de 20/12/2025 a 06/01/2026; suspensão de prazos até 31/01/2026)"),
    "portaria_124": (BASE_NORMA + "portariadg124-2026.pdf",
                     "Portaria GDG 124/2026 (suspensão de prazos de 2 a 31/07/2026)"),
    "portaria_146": (BASE_NORMA + "portariadg146-2026.pdf",
                     "Portaria GDG 146/2026 (ponto facultativo em 29/06/2026; prazos prorrogados para 30/06)"),
    "portaria_112": (BASE_NORMA + "portariadg112-2026.pdf",
                     "Portaria GDG 112/2026 (expediente de 24/06/2026, das 11h às 18h)"),
}

# Nome de cada feriado da Portaria 189 (art. 1º, incisos I a XII, que caem em 2026).
FERIADOS_2026: Dict[str, str] = {
    "I": "Confraternização Universal",
    "II": "Carnaval",
    "III": "Semana Santa",
    "IV": "Tiradentes",
    "V": "Dia do Trabalho",
    "VI": "Fundação dos Cursos Jurídicos",
    "VII": "Dia da Independência",
    "VIII": "Nossa Senhora Aparecida",
    "IX": "Finados",
    "X": "Dia Nacional de Zumbi e da Consciência Negra",
    "XI": "Dia da Justiça",
    "XII": "Natal",
}
PONTOS_2026_QTD = 7  # Portaria 189, § 1º, incisos I a VII são de 2026

MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
         "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

_RE_DATA = re.compile(r"^(\d{1,2})[º°]?(?: (?:a|e) (\d{1,2})[º°]?)? de ([a-zç]+) de (\d{4})")
_RE_EXTENSA = re.compile(r"^(\d{1,2}) de ([a-zç]+) de (\d{4})$")
_RE_INCISO = re.compile(r"^([IVXL]+) *[–−\-] *(\d.*)$")


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto com layout, via pdftotext."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _norm(texto: str) -> str:
    return " ".join(texto.split())


def _linhas(texto: str) -> List[str]:
    return [" ".join(l.split()) for l in texto.splitlines() if l.strip()]


def _indice(linhas: List[str], trecho: str, inicio: int = 0) -> int:
    for i in range(inicio, len(linhas)):
        if trecho in linhas[i]:
            return i
    raise ErroDeFonte("não achei %r no texto da portaria" % trecho)


def _mes(nome: str) -> int:
    n = MESES.get(nome.lower())
    if n is None:
        raise ErroDeFonte("mês desconhecido na fonte: %r" % nome)
    return n


def _extensa(trecho: str) -> datetime.date:
    """'20 de dezembro de 2025' -> date."""
    m = _RE_EXTENSA.match(trecho.strip())
    if not m:
        raise ErroDeFonte("data não reconhecida na fonte: %r" % trecho)
    return datetime.date(int(m.group(3)), _mes(m.group(2)), int(m.group(1)))


def _intervalo(ini: datetime.date, fim: datetime.date) -> List[datetime.date]:
    if fim < ini:
        raise ErroDeFonte("intervalo ao contrário: %s a %s" % (ini, fim))
    return [ini + datetime.timedelta(days=k) for k in range((fim - ini).days + 1)]


def _data_inicial(trecho: str) -> Tuple[datetime.date, datetime.date]:
    """Início de um item da Portaria 189: '1º a 03 de abril de 2026' -> (1/4, 3/4)."""
    m = _RE_DATA.match(trecho)
    if not m:
        raise ErroDeFonte("data não reconhecida no item: %r" % trecho)
    mes = _mes(m.group(3))
    ano = int(m.group(4))
    ini = datetime.date(ano, mes, int(m.group(1)))
    fim = datetime.date(ano, mes, int(m.group(2) or m.group(1)))
    return ini, fim


def _feriados_189(texto: str, ano: int) -> Tuple[List[Dict[str, str]], int]:
    """Art. 1º, incisos: feriados que caem no ano pedido. Devolve (dias, quantos incisos de 2026)."""
    linhas = _linhas(texto)
    inicio = _indice(linhas, "Art. 1º Divulgar")
    fim = _indice(linhas, "Haverá ponto facultativo", inicio)
    dias: List[Dict[str, str]] = []
    incisos = set()
    for l in linhas[inicio:fim]:
        m = _RE_INCISO.match(l)
        if not m:
            continue
        ini, last = _data_inicial(m.group(2))
        if ini.year != ano:
            continue
        if m.group(1) not in FERIADOS_2026:
            raise ErroDeFonte("inciso %s da Portaria 189 sem nome conhecido" % m.group(1))
        incisos.add(m.group(1))
        for d in _intervalo(ini, last):
            dias.append(dia(d, "sem_expediente", FERIADOS_2026[m.group(1)], "portaria_189"))
    if len(incisos) != len(FERIADOS_2026):
        raise ErroDeFonte("Portaria 189: achei %d feriados de %d, esperava %d" % (len(incisos), ano, len(FERIADOS_2026)))
    return dias, len(incisos)


def _pontos_189(texto: str, ano: int) -> Tuple[List[Dict[str, str]], List[str], int]:
    """§ 1º, pontos facultativos de 2026: (dias parciais, datas omitidas, quantos)."""
    linhas = _linhas(texto)
    inicio = _indice(linhas, "Haverá ponto facultativo")
    fim = _indice(linhas, "§ 2º", inicio)
    parciais: List[Dict[str, str]] = []
    omitidos: List[str] = []
    for l in linhas[inicio:fim]:
        m = _RE_INCISO.match(l)
        if not m:
            continue
        ini, last = _data_inicial(m.group(2))
        if ini.year != ano:
            continue
        if "até às 14 horas" in m.group(2):
            parciais.append(dia(ini, "parcial", "Quarta-feira de Cinzas (ponto facultativo até as 14h)",
                                "portaria_189", horario="até as 14h"))
        else:
            # DUVIDA: a Portaria 189 não diz se o ponto facultativo suspende prazo. Não lançado (ver docstring).
            omitidos.append(ini.isoformat())
    return parciais, omitidos, len(parciais) + len(omitidos)


def interpretar(textos: Dict[str, str], ano: int) -> Dict[str, Any]:
    """Textos das fontes (pdftotext -layout, por id de FONTES) -> calendário no formato de modelo.py.

    Sem rede. `textos` tem uma chave por id de FONTES."""
    if ano != 2026:
        raise ErroDeFonte("interpretar só conhece o calendário de 2026 (pedido: %d)" % ano)
    faltam = [i for i in FONTES if i not in textos]
    if faltam:
        raise ErroDeFonte("faltam textos das fontes: %s" % ", ".join(faltam))

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{"id": i, "url": url, "descricao": desc} for i, (url, desc) in FONTES.items()]
    geral: List[Dict[str, str]] = []

    # Feriados (Portaria 189, art. 1º).
    feriados, _ = _feriados_189(textos["portaria_189"], ano)
    geral.extend(feriados)

    # Pontos facultativos (Portaria 189, § 1º): só o de 18/02 (até as 14h) vira dia; os demais ficam
    # de fora (DUVIDA, ver docstring e `parcial`).
    parciais, _omitidos, qtd_pontos = _pontos_189(textos["portaria_189"], ano)
    if qtd_pontos != PONTOS_2026_QTD:
        raise ErroDeFonte("Portaria 189: achei %d pontos facultativos de %d, esperava %d"
                          % (qtd_pontos, ano, PONTOS_2026_QTD))
    geral.extend(parciais)

    # Recesso de 20/12/2025 a 06/01/2026 (Portaria 250, art. 1º) e suspensão de prazos (art. 4º).
    norm250 = _norm(textos["portaria_250"])
    m = re.search(r"Não haverá expediente no período de (.+?) a (.+?)\.", norm250)
    if not m:
        raise ErroDeFonte("Portaria 250: não achei o recesso (art. 1º)")
    for d in _intervalo(_extensa(m.group(1)), _extensa(m.group(2))):
        if d.year == ano:
            geral.append(dia(d, "recesso", "Recesso forense", "portaria_250"))
    m = re.search(r"Os prazos processuais ficarão suspensos no período de (.+?) a (.+?)\.", norm250)
    if not m:
        raise ErroDeFonte("Portaria 250: não achei a suspensão de prazos (art. 4º)")
    for d in _intervalo(_extensa(m.group(1)), _extensa(m.group(2))):
        if d.year == ano:
            geral.append(dia(d, "suspensao_prazo", "Suspensão de prazos processuais (Portaria GDG 250/2025, art. 4º)",
                             "portaria_250"))

    # Recesso de 20/12/2026 (calendário oficial). O trecho de 2027 não entra.
    norm_cal = _norm(textos["calendario"])
    m = re.search(r"Recesso forense \(art\. 78, § 1º, RISTF\): \(\w+\) (\d{2})/(\d{2})/(\d{4}) a \(\w+\) "
                  r"(\d{2})/(\d{2})/(\d{4})", norm_cal)
    if not m:
        raise ErroDeFonte("calendário: não achei a linha do recesso forense")
    ini = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    fim = datetime.date(int(m.group(6)), int(m.group(5)), int(m.group(4)))
    for d in _intervalo(ini, fim):
        if d.year == ano:
            geral.append(dia(d, "recesso", "Recesso forense", "calendario"))

    # Suspensão de prazos de julho (Portaria 124, art. 1º).
    m = re.search(r"prazos processuais ficarão suspensos no período de (\d{1,2}) a (\d{1,2}) de (\w+) de (\d{4})",
                  _norm(textos["portaria_124"]))
    if not m:
        raise ErroDeFonte("Portaria 124: não achei a suspensão de prazos (art. 1º)")
    ini = datetime.date(int(m.group(4)), _mes(m.group(3)), int(m.group(1)))
    fim = datetime.date(int(m.group(4)), _mes(m.group(3)), int(m.group(2)))
    for d in _intervalo(ini, fim):
        geral.append(dia(d, "suspensao_prazo", "Suspensão de prazos processuais (Portaria GDG 124/2026, art. 1º)",
                         "portaria_124"))

    # Ponto facultativo de 29/06/2026 com prazos prorrogados (Portaria 146, art. 1º e 3º).
    norm146 = _norm(textos["portaria_146"])
    m = re.search(r"marcado para o dia (\d{1,2} de [a-zç]+ de \d{4})", norm146)
    if not m or "Decretar ponto facultativo" not in norm146 or "prorrogados para o dia 30 de junho" not in norm146:
        raise ErroDeFonte("Portaria 146: texto diferente do esperado")
    geral.append(dia(_extensa(m.group(1)), "sem_expediente",
                     "Ponto facultativo: jogo da Seleção Brasileira (Portaria GDG 146/2026)", "portaria_146"))

    # Expediente reduzido em 24/06/2026 (Portaria 112, art. 1º).
    m = re.search(r"no dia (\d{1,2} de [a-zç]+ de \d{4}), que terá início às (\d{1,2})h, e término às (\d{1,2})h",
                  _norm(textos["portaria_112"]))
    if not m:
        raise ErroDeFonte("Portaria 112: texto diferente do esperado")
    geral.append(dia(_extensa(m.group(1)), "parcial",
                     "Expediente reduzido (Portaria GDG 112/2026)", "portaria_112",
                     horario="das %sh às %sh" % (m.group(2), m.group(3))))

    cal["geral"] = geral
    cal["locais"] = {normalizar_local("BRASÍLIA"): []}
    return ordenar(cal)


class MotorSTF(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = (
        "Ficam de fora: (1) pontos facultativos da Portaria GDG 189/2025, § 1º, II a VII (20/04, 04/06 "
        "Corpus Christi, 05/06, 10/08, 30/10, 07/12): não lançados porque a fonte não diz se suspendem "
        "prazo (DUVIDA em aberto; a ficha sugere sem expediente e a revisão decide); (2) atos avulsos "
        "não listados aqui (só 112, 124, 146 e 250 foram lidos; a página índice do STF tem links JS sem "
        "texto e não é lida); (3) atos publicados depois de 23/10/2026; (4) férias coletivas dos "
        "ministros (2 a 31/01 e 2 a 31/07), sem dia próprio; (5) horário reduzido de atendimento ao "
        "público (13h às 18h em jan e jul), que não é expediente; (6) recesso e suspensão de prazos de "
        "20/12/2026 a 06/01/2027 e os demais do ano seguinte, ainda não publicados (o 2027 é "
        "AindaNaoPublicado)."
    )
    esperado = {
        "min_geral": 80,   # 97 dias lidos da fixture (feriados, recesso, suspensões e avulsos)
        "min_locais": 1,   # chave única "BRASÍLIA" (tribunal único, sem locais)
        "ancoras": {
            "2026-01-06": "Recesso forense, fim (Portaria 250)",
            "2026-02-16": "Carnaval",
            "2026-02-17": "Carnaval",
            "2026-04-01": "Semana Santa",
            "2026-04-03": "Semana Santa, fim",
            "2026-07-02": "Suspensão de prazos (Portaria 124)",
            "2026-07-31": "Suspensão de prazos (Portaria 124), fim",
            "2026-12-20": "Recesso forense (calendário 2026)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano != 2026:
            # DUVIDA: o calendário de 2027 (recesso de dez/2027, suspensões) não foi publicado. A Portaria 189
            # traz só feriados de 2027; sem o resto, o calendário ficaria pela metade.
            raise AindaNaoPublicado("o STF ainda não publicou o calendário de %d (a Portaria 189 traz só os feriados)" % ano)
        textos = {}
        for id_, (url, _desc) in FONTES.items():
            textos[id_] = pdf_para_texto(rede.baixar(url))
        return interpretar(textos, ano)


MOTOR = MotorSTF()
