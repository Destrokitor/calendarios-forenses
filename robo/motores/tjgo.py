"""Motor do TJGO (Tribunal de Justiça do Estado de Goiás). Ficha: docs/fichas/TJGO.md.

Fonte: PDF "FERIADOS 2026" do próprio tribunal (versão de 08/06/2026), tabela
DATA | DIA DA SEMANA | DESCRIÇÃO | FERIADO (alcance), em 2 páginas.

Leitura: `pdftotext -raw` (e não `-layout`). Na ordem de texto `-raw` cada linha da tabela sai
junta, começando pela data, e as linhas seguintes são a continuação da mesma linha da tabela.
Com `-layout` a célula da data sai no meio da altura das células de descrição e de alcance, e
os registros se misturam.

Abrangência: o alcance "Feriado no Tribunal e em todas as comarcas", "Feriado Nacional",
"Feriado Estadual" e "Feriado (Art. 123 ...)" vai para `geral`. O "Feriado Municipal (restrito ao
Tribunal e às comarcas de ...)" vai para `locais` das comarcas listadas. Um alcance que não
estiver nessa lista levanta ErroDeFonte (não é ignorado em silêncio).

Efeito de cada item:
  - feriado com alcance geral -> sem_expediente;
  - "até 12h" (só 18/02/2026, Quarta de Cinzas) -> parcial, com o horário lido da fonte;
  - "Recesso Forense" (20/12/2026 a 06/01/2027) -> recesso; só entram os dias de 2026. Os dias
    de 01 a 06/01/2027 caem no ano seguinte e vêm no calendário de 2027;
  - PONTO FACULTATIVO (20/03, 20/04, 05/06 em 2026): NÃO entra no calendário. DUVIDA: o PDF não
    diz se o ponto suspende prazo (ficha, DUVIDA). Como o robô não pode inventar suspensão de
    prazo, o dia fica fora: o prazo continua correndo. Quem revisa decide se entra.

DUVIDA (ficha): o nome do arquivo tem a data da versão (08062026) e muda ao longo do ano. A
ficha não diz como achar a versão nova, e o motor usa só o endereço de 08/06/2026. Por isso o
ano de 2027 levanta AindaNaoPublicado até alguém registrar a regra na ficha.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

# Endereço do PDF de cada ano. O de 2027 ainda não é conhecido (ver DUVIDA no cabeçalho).
FONTES: Dict[int, str] = {
    2026: "https://docs.tjgo.jus.br/institucional/feriados/DOC_feriados_2026_08062026.pdf",
}
FONTE_ID = "feriados"
FONTE_DESCRICAO = ("Tabela 'FERIADOS 2026' do TJGO, versão de 08/06/2026 (PDF do próprio tribunal, "
                   "2 páginas): feriados, ponto facultativo e recesso forense")

# Comarcas com feriado municipal no PDF (única linha local da tabela). A chave do `locais` é
# montada a partir desta lista; nome fora dela levanta erro.
LOCAIS_CONHECIDOS: List[str] = ["Goiânia", "Iporá", "Leopoldo de Bulhões", "Senador Canedo"]

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Linha que abre um item: "1º de janeiro Quinta-feira Ano Novo Feriado Nacional".
_RE_DATA = re.compile(r"^(\d{1,2})[º°]? de ([a-zçãé]+)\b\s*(.*)$", re.IGNORECASE)
# Recesso: "20/12/26 a Recesso Forense - ..."; o fim vem depois, numa linha só com a data.
_RE_RECESSO_INICIO = re.compile(r"^(\d{2})/(\d{2})/(\d{2}) a\b")
_RE_RECESSO_FIM = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_RE_HORARIO = re.compile(r"^até \d{1,2}h$")
_RE_DIA_SEMANA = re.compile(r"^(domingo|sábado|(segunda|terça|quarta|quinta|sexta)-feira)\b\s*", re.IGNORECASE)
# Onde começa o alcance (a última coluna). Antes disso é descrição.
_RE_INICIO_ALCANCE = re.compile(r"Feriado\b|Em todo o Poder Judiciário|Ponto facultativo em todo")
_RE_PONTO = re.compile(r"ponto facultativo", re.IGNORECASE)
_RE_MUNICIPAL = re.compile(r"^Feriado Municipal \(restrito ao Tribunal e às comarcas de ([^)]+)\)$")
_RE_GERAL = re.compile(
    r"^(Feriado Nacional"
    r"|Feriado no Tribunal e em todas as comarcas\*"
    r"|Feriado Estadual \(Lei nº 20\.756/20\)"
    r"|Feriado \(Art\. 123 do Regimento Interno do TJGO\))$"
)
# Cabeçalhos e rodapés repetidos pelas duas páginas.
_CABECALHOS = {"PODER JUDICIÁRIO", "Tribunal de Justiça do Estado de Goiás", "DATA", "DIA DA",
               "SEMANA", "DESCRIÇÃO FERIADO"}
_RODAPE = "Av. Assis Chateubriand"
_INICIO_NOTAS = "¹"  # primeira nota de rodapé: a tabela acabou


def pdf_para_texto(pdf: bytes) -> str:
    """PDF em bytes -> texto na ordem de leitura (`pdftotext -raw`)."""
    try:
        r = subprocess.run(["pdftotext", "-raw", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def _acrescenta(linha: Dict[str, Any], texto: str) -> None:
    """Põe um pedaço de texto da linha da tabela na descrição ou no alcance."""
    if linha["dia_semana_pendente"] and texto:
        m = _RE_DIA_SEMANA.match(texto)
        linha["dia_semana_pendente"] = False
        if m:
            texto = texto[m.end():]
    texto = texto.strip()
    if not texto:
        return
    if linha["modo"] == "descricao":
        m = _RE_INICIO_ALCANCE.search(texto)
        if m:
            antes = texto[:m.start()].strip()
            if antes:
                linha["descricao"].append(antes)
            linha["alcance"].append(texto[m.start():])
            linha["modo"] = "alcance"
        else:
            linha["descricao"].append(texto)
    else:
        linha["alcance"].append(texto)


def _linhas(texto: str, ano: int) -> List[Dict[str, Any]]:
    """Agrupa o texto em itens da tabela: data(s), horário, descrição, alcance."""
    itens: List[Dict[str, Any]] = []
    atual: Optional[Dict[str, Any]] = None
    for bruta in texto.splitlines():
        l = " ".join(bruta.split())
        if not l or l in _CABECALHOS or _RODAPE in l:
            continue
        if l.startswith(_INICIO_NOTAS):
            break
        m = _RE_DATA.match(l)
        if m:
            mes = MESES.get(m.group(2).lower())
            if mes is None:
                raise ErroDeFonte("mês desconhecido na tabela: %r" % m.group(2))
            try:
                data = datetime.date(ano, mes, int(m.group(1)))
            except ValueError:
                raise ErroDeFonte("data inexistente na tabela: %s/%s/%d" % (m.group(1), mes, ano))
            atual = {"recesso": False, "ini": data, "fim": None, "horario": "", "descricao": [],
                     "alcance": [], "modo": "descricao", "dia_semana_pendente": True}
            itens.append(atual)
            _acrescenta(atual, m.group(3))
            continue
        m = _RE_RECESSO_INICIO.match(l)
        if m:
            ini = datetime.date(2000 + int(m.group(3)), int(m.group(2)), int(m.group(1)))
            atual = {"recesso": True, "ini": ini, "fim": None, "horario": "", "descricao": [],
                     "alcance": [], "modo": "descricao", "dia_semana_pendente": False}
            itens.append(atual)
            continue
        if atual is None:
            continue  # cabeçalho ou texto antes da tabela
        m = _RE_RECESSO_FIM.match(l)
        if m and atual["recesso"] and atual["fim"] is None:
            atual["fim"] = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            continue
        if _RE_HORARIO.match(l) and not atual["recesso"]:
            atual["horario"] = l
            continue
        if not atual["recesso"]:
            _acrescenta(atual, l)
    return itens


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto de `pdf_para_texto` -> calendário no formato de modelo.py. Puro: sem rede."""
    if "FERIADOS %d" % ano not in conteudo:
        raise ErroDeFonte("o PDF não é a tabela FERIADOS %d" % ano)

    cal = calendario_vazio(MotorTJGO.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTES.get(ano, ""), "descricao": FONTE_DESCRICAO}]
    locais: Dict[str, List[Dict[str, str]]] = {normalizar_local(n): [] for n in LOCAIS_CONHECIDOS}

    for item in _linhas(conteudo, ano):
        if item["recesso"]:
            if item["fim"] is None:
                raise ErroDeFonte("recesso sem data final no PDF")
            if item["ini"].year != ano:
                raise ErroDeFonte("recesso começa em %s, não em %d" % (item["ini"].isoformat(), ano))
            n = (item["fim"] - item["ini"]).days + 1
            for k in range(n):
                data = item["ini"] + datetime.timedelta(days=k)
                if data.year == ano:  # 01 a 06/01/2027 vem no calendário de 2027
                    cal["geral"].append(dia(data, "recesso", "Recesso forense", FONTE_ID))
            continue

        descricao = " ".join(item["descricao"])
        alcance = " ".join(item["alcance"])
        data = item["ini"]
        if not descricao:
            raise ErroDeFonte("item sem descrição em %s" % data.isoformat())
        if _RE_PONTO.search(descricao) or _RE_PONTO.search(alcance):
            # DUVIDA: ponto facultativo não entra (ver cabeçalho do módulo). Não é suspensão de
            # prazo sem decisão do tribunal.
            continue
        if item["horario"]:
            tipo, horario = "parcial", item["horario"]
        else:
            tipo, horario = "sem_expediente", ""

        if "Feriado Municipal" in alcance:
            m = _RE_MUNICIPAL.match(alcance)
            if not m:
                raise ErroDeFonte("alcance municipal não reconhecido em %s: %r" % (data.isoformat(), alcance))
            nomes = [n.strip() for parte in m.group(1).split(", ") for n in re.split(r" e ", parte)]
            for nome in nomes:
                if nome not in LOCAIS_CONHECIDOS:
                    raise ErroDeFonte("comarca nova no PDF da municipal: %r" % nome)
                locais[normalizar_local(nome)].append(dia(data, tipo, descricao, FONTE_ID, horario))
        elif _RE_GERAL.match(alcance):
            cal["geral"].append(dia(data, tipo, descricao, FONTE_ID, horario))
        else:
            raise ErroDeFonte("alcance não reconhecido em %s: %r" % (data.isoformat(), alcance))

    cal["locais"] = locais
    return ordenar(cal)


class MotorTJGO(Motor):
    sigla = "TJGO"
    precisa_ip_brasil = False  # testado na nuvem: o PDF abre (ficha)
    parcial = (
        "Lê só a tabela 'FERIADOS 2026' do TJGO (versão de 08/06/2026). Ficam de fora: os pontos "
        "facultativos (20/03, 20/04 e 05/06/2026), que não entram por falta de decisão sobre prazo; "
        "os feriados municipais de outras comarcas, que não constam da tabela; os decretos e "
        "pontos facultativos baixados depois, que o PDF avisa que podem ocorrer; e a versão "
        "posterior do arquivo, se houver. Os dias de 01 a 06/01/2027 vêm no calendário de 2027. "
        "Locais: só as comarcas do feriado municipal (Goiânia, Iporá, Leopoldo de Bulhões e Senador "
        "Canedo); o Tribunal, que fica em Goiânia, não é comarca e não entra em `locais`."
    )
    esperado = {
        # min_geral: lido na tabela de 2026: 20 feriados (incluindo 18/02 parcial) + 12 dias de
        # recesso (20 a 31/12). Piso = o lido.
        "min_geral": 32,
        # min_locais: as 4 comarcas do feriado municipal de 24/05.
        "min_locais": 4,
        # Conferidas à mão na tabela (ficha, âncoras 1 a 5).
        "ancoras": {
            "2026-02-16": "Carnaval",
            "2026-02-18": "Carnaval (até 12h, parcial)",
            "2026-04-01": "Semana Santa (início)",
            "2026-12-08": "Dia da Justiça (Art. 123 do RITJGO)",
            "2026-12-20": "Recesso forense (início)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in FONTES:
            # DUVIDA: a ficha não diz como achar a tabela de 2027 (o nome do arquivo tem a data da
            # versão). Enquanto não houver a regra, o robô só registra o fato.
            raise AindaNaoPublicado("a ficha do TJGO não diz como localizar a tabela de feriados de %d" % ano)
        return interpretar(pdf_para_texto(rede.baixar(FONTES[ano])), ano)


MOTOR = MotorTJGO()
