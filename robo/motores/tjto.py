"""Motor do TJTO (Tribunal de Justiça do Estado do Tocantins). Ficha: docs/fichas/TJTO.md.

Fonte única, oficial (lida do PDF do Diário da Justiça pela API pública do Diário):

  Portaria nº 3741, de 10/11/2025 (Presidência), que institui o calendário de feriados e pontos
  facultativos do exercício de 2026, publicada no Diário da Justiça nº 5995, de 10/11/2025,
  pp. 39 e 40.

O portal www.tjto.jus.br está fora do ar por incidente (22/10/2026): o motor só usa o Diário.

Abrangência (Art. 1º a 4º da portaria):
  - Art. 1º, tabela DATAS | FERIADOS E/OU PONTOS FACULTATIVOS: cada item vai para `geral` como
    sem_expediente, um Dia por data. Intervalos em texto ("16 e 17 de fevereiro", "1º, 2 e 3 de
    abril") viram um Dia por data.
  - Art. 2º: transferências 28/10 -> 30/10 e 08/12 -> 18/12. A tabela já traz as datas novas; as
    originais não viram dia.
  - Art. 3º: pontos facultativos (20/04, 05/06 e 10/08). Não entram como dia: a portaria não diz se
    suspendem prazo. Ver `parcial` e a DUVIDA abaixo.
  - Art. 4º: feriados municipais da Capital (19/03 e 20/05), que vão para `locais["PALMAS"]`.
  - Art. 5º: as comarcas do interior não têm lista na portaria: ficam de fora.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_ID = "portaria"
FONTE_URL = "https://diario.tjto.jus.br/api/diario/03512a628c56487e9b4d0ebba3c0e9c4"
FONTE_DESCRICAO = ("Portaria nº 3741, de 10/11/2025 (Presidência), calendário de feriados e pontos "
                   "facultativos de 2026, Diário da Justiça nº 5995, de 10/11/2025, pp. 39 e 40")

# Edição do Diário que traz o calendário de cada ano. A ficha só conhece o de 2026.
EDICOES: Dict[int, str] = {2026: FONTE_URL}

# O Art. 4º fala em "Capital", que é Palmas (a única comarca nominal na portaria).
CAPITAL = "Palmas"

MESES = {nome: i for i, nome in enumerate(
    ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
     "outubro", "novembro", "dezembro"], 1)}

_RE_CABECALHO_TABELA = re.compile(r"^DATAS\s+FERIADOS")
_RE_PAGINA_DJ = re.compile(r"DIÁRIO DA JUSTIÇA")
_RE_DATA_TEXTUAL = re.compile(r"^(.+?) de ([^\s]+)$")


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto com layout (colunas preservadas), via pdftotext."""
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _normal(texto: str) -> str:
    return " ".join(texto.split())


def _bloco(portaria: str, n: int) -> str:
    """Texto bruto do Art. n da portaria, até o Art. n+1."""
    ini = re.search(r"Art\. %d[º°]" % n, portaria)
    if not ini:
        raise ErroDeFonte("não achei o Art. %d da Portaria 3741" % n)
    fim = re.search(r"Art\. %d[º°]" % (n + 1), portaria[ini.end():])
    if not fim:
        raise ErroDeFonte("não achei o fim do Art. %d da Portaria 3741" % n)
    return portaria[ini.start(): ini.end() + fim.start()]


def _tabela(bloco_art1: str) -> List[Tuple[str, str]]:
    """(datas, descrição) de cada linha da tabela do Art. 1º. Pula cabeçalhos de página do DJ."""
    linhas = bloco_art1.split("\n")
    inicio = None
    for i, linha in enumerate(linhas):
        if _RE_CABECALHO_TABELA.match(linha.strip()):
            inicio = i + 1
            break
    if inicio is None:
        raise ErroDeFonte("não achei o cabeçalho DATAS | FERIADOS no Art. 1º")
    linhas_tabela: List[Tuple[str, str]] = []
    for linha in linhas[inicio:]:
        s = linha.strip()
        if not s or _RE_PAGINA_DJ.search(s):
            continue
        partes = re.split(r"\s{2,}", s, maxsplit=1)
        if len(partes) != 2:
            raise ErroDeFonte("linha da tabela do Art. 1º sem duas colunas: %r" % s)
        linhas_tabela.append((_normal(partes[0]), _normal(partes[1])))
    if not linhas_tabela:
        raise ErroDeFonte("tabela do Art. 1º vazia")
    return linhas_tabela


def _datas(texto: str, ano: int) -> List[datetime.date]:
    """'16 e 17 de fevereiro' -> [16/02, 17/02] do ano. '1º, 2 e 3 de abril' -> 01, 02 e 03/04."""
    m = _RE_DATA_TEXTUAL.match(_normal(texto))
    if not m:
        raise ErroDeFonte("data não reconhecida na tabela: %r" % texto)
    mes = MESES.get(m.group(2).lower())
    if mes is None:
        raise ErroDeFonte("mês não reconhecido na tabela: %r" % m.group(2))
    datas = []
    for numero in re.findall(r"\d{1,2}", m.group(1)):
        try:
            datas.append(datetime.date(ano, mes, int(numero)))
        except ValueError:
            raise ErroDeFonte("data inválida na tabela: %s de %s" % (numero, m.group(2)))
    if not datas:
        raise ErroDeFonte("nenhum dia reconhecido em %r" % texto)
    return datas


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do DJ (pdftotext -layout) -> calendário no formato de modelo.py. Sem rede."""
    m = re.search(r"Portaria N[º°o]\s*3741\b", conteudo)
    if not m:
        raise ErroDeFonte("não achei a Portaria nº 3741 no texto")
    portaria = conteudo[m.start():]

    art1 = _bloco(portaria, 1)
    if not re.search(r"exerc[íi]cio de %d\b" % ano, _normal(art1)):
        raise ErroDeFonte("a Portaria 3741 não é a do exercício de %d" % ano)

    cal = calendario_vazio(MotorTJTO.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]

    # DUVIDA: a portaria não diz se os pontos facultativos suspendem prazo. Sem essa decisão,
    # não viram sem_expediente nem suspensao_prazo (isso inventaria suspensão): ficam de fora.
    pontos_tabela = set()
    for datas_txt, descricao in _tabela(art1):
        datas = _datas(datas_txt, ano)
        if descricao.lower().startswith("ponto facultativo"):
            pontos_tabela.update((d.month, d.day) for d in datas)
            continue
        for data in datas:
            cal["geral"].append(dia(data, "sem_expediente", descricao, FONTE_ID))

    # O Art. 3º tem de listar exatamente os pontos da tabela: se não bater, a leitura está errada.
    art3 = _normal(_bloco(portaria, 3))
    pontos_art3 = {(MESES[mes], int(numero)) for numero, mes in re.findall(r"(\d{1,2}) de ([^\s,]+)", art3)
                   if mes in MESES}
    if pontos_tabela != pontos_art3:
        raise ErroDeFonte("pontos facultativos da tabela (%s) diferem do Art. 3º (%s)"
                          % (sorted(pontos_tabela), sorted(pontos_art3)))

    # Art. 4º: feriados municipais da Capital (Palmas).
    art4 = _normal(_bloco(portaria, 4))
    if "Capital" not in art4:
        raise ErroDeFonte("Art. 4º sem referência à Capital")
    locais: Dict[str, List[Dict[str, str]]] = {normalizar_local(CAPITAL): []}
    for numero, mes, motivo in re.findall(r"(\d{1,2}) de ([^\s()]+) \(([^)]*)\)", art4):
        if mes not in MESES:
            raise ErroDeFonte("mês não reconhecido no Art. 4º: %r" % mes)
        data = datetime.date(ano, MESES[mes], int(numero))
        locais[normalizar_local(CAPITAL)].append(dia(data, "sem_expediente", motivo, FONTE_ID))

    cal["locais"] = locais
    return ordenar(cal)


class MotorTJTO(Motor):
    sigla = "TJTO"
    # Não testado a partir de IP brasileiro. A API do Diário abriu na nuvem em outra edição (DJ
    # 6200, ficha); a edição do calendário de 2026 (DJ 5995) ainda não foi testada na nuvem.
    precisa_ip_brasil = False
    parcial = (
        "Lê só a Portaria nº 3741/2025 (DJ 5995, pp. 39 e 40), que traz o calendário de 2026. "
        "Ficam de fora: (1) as comarcas do interior: a portaria não tem lista (Art. 5º: feriados "
        "municipais próprios, a cargo do Diretor do Foro), e só Palmas aparece (Art. 4º); (2) os "
        "pontos facultativos de 20/04, 05/06 e 10/08 (Art. 3º), que não entram como dia porque a "
        "portaria não diz se suspendem prazo; (3) portarias de comarca, decretos e alterações "
        "posteriores, como o Decreto Judiciário 772 (prazos suspensos em 20 a 23/10/2026, incidente "
        "cibernético); (4) recesso forense: a portaria não traz, e nenhum recesso entra no calendário. "
        "Em 2027 ainda não há edição conhecida."
    )
    esperado = {
        "min_geral": 19,  # dias gerais lidos na tabela do Art. 1º (ficha não traz contagem)
        "min_locais": 1,  # só Palmas é nominal (Art. 4º)
        # Conferidas à mão no Art. 1º e 2º da portaria (ficha, itens 1 a 4).
        "ancoras": {
            "2026-02-16": "Carnaval (início)",
            "2026-02-17": "Carnaval (fim)",
            "2026-04-01": "Semana Santa (início)",
            "2026-04-03": "Semana Santa (fim)",
            "2026-10-30": "Dia do Servidor Público (transferido de 28/10)",
            "2026-12-18": "Dia da Justiça (transferido de 08/12)",
        },
        "exige_recesso": False,  # a portaria não traz recesso
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in EDICOES:
            # DUVIDA: a ficha não diz como achar o Diário com o calendário de 2027. O de 2026 saiu no
            # DJ de 10/11/2025; a busca pela lista publicados?ano=<ano-1>&mes=11 não foi testada.
            raise AindaNaoPublicado(
                "a ficha do TJTO não diz como localizar o calendário de %d; a edição conhecida "
                "(DJ 5995, de 10/11/2025) traz só o exercício de 2026" % ano)
        return interpretar(pdf_para_texto(rede.baixar(EDICOES[ano])), ano)


MOTOR = MotorTJTO()
