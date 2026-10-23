"""Motor do TJRR (Tribunal de Justiça do Estado de Roraima).

Fonte única, oficial (ficha: docs/fichas/TJRR.md):

  Portaria TJRR/PR n. 1558, de 19/12/2025, publicada no DJe ano XXVI, edição 8006, de
  22/12/2025, pp. 3 a 7. O Anexo Único é uma tabela DATA | DESCRIÇÃO | COMARCA, em duas
  partes: a) feriados da capital e b) feriados dos municípios do interior.

Abrangência: a linha "Todas as Comarcas" vai para `geral`; a linha com comarca nomeada vai
para `locais[COMARCA]`. Um intervalo numa célula ("16 a 18/2/2026") vira um Dia por data.

Efeito de cada item (Art. 3º da portaria: "ficam suspensos o expediente e os prazos" nas datas
de feriados OU PONTOS FACULTATIVOS):
  - "Recesso forense" -> recesso
  - feriado e ponto facultativo -> sem_expediente (o ponto também suspende prazo, por isso
    não vira expediente parcial nem suspensao_prazo)

Não entra: feriado ou ponto decretado depois por outro Poder (Art. 2º: é só comunicado à
Secretaria de Gestão de Pessoas, sem constar do anexo). Ver `parcial`.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_URL = "https://diario.tjrr.jus.br/dpj/dpj-20251222.pdf"
FONTE_ID = "portaria"
FONTE_DESCRICAO = ("Portaria TJRR/PR n. 1558, de 19/12/2025 (Anexo Único), DJe ano XXVI, edição 8006, "
                   "de 22/12/2025, pp. 3 a 7")

# Edição do DJe que traz o calendário de cada ano. A ficha só conhece o de 2026; para os demais
# anos o motor levanta AindaNaoPublicado (ver coletar).
EDICOES: Dict[int, str] = {2026: FONTE_URL}

# Colunas do texto do pdftotext -layout, medidas nas páginas da portaria: a data começa na
# coluna 4, a descrição na 22 (ou na 13, no "a" de intervalo) e a comarca na 92 a 100.
COL_DESCRICAO = 15
COL_COMARCA = 85

# Comarca como aparece no anexo -> chave do locais. Só estes nomes são aceitos: outro nome
# levanta erro, para não sumir um local em silêncio.
LOCAIS: List[Tuple[str, str]] = [
    (r"Boa Vista", "Boa Vista"),
    (r"Mucajaí", "Mucajaí"),
    (r"Bonfim", "Bonfim"),
    (r"Caracaraí", "Caracaraí"),
    # DUVIDA: no 15/05 o texto do DJe quebra a linha e aparece "Alto de Alegre"; tratado como
    # a comarca de Alto Alegre, que é o nome da ficha. Conferir no ato se for erro de quebra.
    (r"Alto (?:de )?Alegre", "Alto Alegre"),
    (r"São Luiz do Anauá", "São Luiz do Anauá"),
    (r"Pacaraima", "Pacaraima"),
    (r"Rorainópolis", "Rorainópolis"),
    (r"Posto Avançado de Caroebe", "Posto Avançado de Caroebe e de Iracema"),
]

_RE_DATA = re.compile(r"(\d{1,2})[º°]?/(\d{1,2})/(\d{4})")
_RE_DIA = re.compile(r"(\d{1,2})[º°]?")
_RE_CABECALHO = re.compile(
    r"Número de Autenticidade|Diário da Justiça|DATA\s+DESCRIÇÃO|FERIADOS (?:DA CAPITAL|DOS MUNICÍPIOS)"
    r"|ANEXO ÚNICO|Documento assinado|A autenticidade do documento"
)


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


def _limpa(texto: str) -> str:
    return " ".join(texto.split())


def _pedacos(linha: str) -> List[Tuple[int, str]]:
    """Quebra a linha em trechos separados por espaço duplo, com a coluna onde cada um começa."""
    return [(m.start(), m.group()) for m in re.finditer(r"\S+(?: \S+)*", linha)]


def _anexo(texto: str, ano: int) -> List[str]:
    """Linhas do Anexo Único da Portaria 1558 (só ela: o DJe pode ter outras portarias)."""
    m = re.search(r"PORTARIA TJRR/PR N\. 1558\b", texto)
    if not m:
        raise ErroDeFonte("não achei a Portaria TJRR/PR n. 1558 no texto")
    inicio = m.start()
    a = texto.find("ANEXO ÚNICO", inicio)
    if a == -1:
        raise ErroDeFonte("não achei o Anexo Único da Portaria 1558")
    fim = texto.find("Documento assinado", a)
    if fim == -1:
        fim = len(texto)
    if not re.search(r"exerc[íi]cio de %d\b" % ano, texto[inicio:a]):
        raise ErroDeFonte("a Portaria 1558 não é a do exercício de %d" % ano)
    linhas = []
    for linha in texto[a:fim].split("\n"):
        linha = linha.replace("\f", "")
        if not linha.strip() or _RE_CABECALHO.search(linha) or linha.strip() == "PRESIDÊNCIA":
            continue
        linhas.append(linha)
    return linhas


def _registros(linhas: List[str]) -> List[Dict[str, Any]]:
    """Agrupa as linhas do anexo em registros (data(s), descrição, comarca).

    Uma linha que começa com data abre registro. "1º   a   Recesso forense" abre intervalo, cuja
    data final vem na linha seguinte ("6/1/2026"). Linha sem data é continuação do registro
    anterior: o que está na coluna da comarca completa a comarca; o resto completa a descrição.
    """
    registros: List[Dict[str, Any]] = []
    atual: Optional[Dict[str, Any]] = None
    pendente: Optional[Dict[str, Any]] = None  # intervalo que espera a data final

    for linha in linhas:
        pedacos = _pedacos(linha)
        if not pedacos:
            continue
        col, primeiro = pedacos[0]
        resto = pedacos[1:]

        m_data = _RE_DATA.fullmatch(primeiro) if col < COL_DESCRICAO else None
        m_dia = _RE_DIA.fullmatch(primeiro) if col < COL_DESCRICAO else None
        if m_data:
            fim = datetime.date(int(m_data.group(3)), int(m_data.group(2)), int(m_data.group(1)))
            if pendente is not None:
                pendente["fim"] = fim
                pendente["ini"] = datetime.date(fim.year, fim.month, pendente.pop("dia_ini"))
                if pendente["ini"] > fim:
                    raise ErroDeFonte("intervalo ao contrário perto de %s" % fim.isoformat())
                pendente = None
            else:
                atual = {"ini": fim, "fim": fim, "descricao": [], "comarca": []}
                registros.append(atual)
        elif m_dia and resto and resto[0][1] == "a":
            atual = {"dia_ini": int(m_dia.group(1)), "ini": None, "fim": None, "descricao": [], "comarca": []}
            registros.append(atual)
            pendente = atual
            resto = resto[1:]
        elif atual is None:
            raise ErroDeFonte("texto do anexo antes da primeira data: %r" % linha.strip())
        else:
            resto = pedacos  # linha de continuação

        if atual is None:
            raise ErroDeFonte("linha sem registro: %r" % linha.strip())
        for c, texto in resto:
            (atual["comarca"] if c >= COL_COMARCA else atual["descricao"]).append(texto)

    if pendente is not None:
        raise ErroDeFonte("intervalo sem data final: %r" % pendente["descricao"])
    for reg in registros:
        reg["descricao"] = _limpa(" ".join(reg["descricao"]))
        reg["comarca"] = _limpa(" ".join(reg["comarca"]))
        if not reg["descricao"] or not reg["comarca"]:
            raise ErroDeFonte("registro incompleto: %s" % reg)
    return registros


def _tipo(descricao: str) -> str:
    # Art. 3º: feriado e ponto facultativo suspendem expediente e prazo -> sem_expediente.
    # Recesso forense é outro tipo: é o período de recesso do art. 116 §2º do RITJRR/CPC.
    if descricao.lower().startswith("recesso forense"):
        return "recesso"
    return "sem_expediente"


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do DJe (pdftotext -layout) -> calendário no formato de modelo.py. Sem rede."""
    cal = calendario_vazio(MotorTJRR.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]
    locais = {normalizar_local(nome): [] for _, nome in LOCAIS}

    for reg in _registros(_anexo(conteudo, ano)):
        tipo = _tipo(reg["descricao"])
        if "Todas as Comarcas" in reg["comarca"]:
            nomes: List[str] = []
        else:
            nomes = [normalizar_local(nome) for padrao, nome in LOCAIS if re.search(padrao, reg["comarca"])]
            if not nomes:
                raise ErroDeFonte("comarca não reconhecida no anexo: %r" % reg["comarca"])
        n = (reg["fim"] - reg["ini"]).days + 1
        for k in range(n):
            data = reg["ini"] + datetime.timedelta(days=k)
            if data.year != ano:
                raise ErroDeFonte("data fora do exercício %d: %s" % (ano, data.isoformat()))
            if nomes:
                for nome in nomes:
                    locais[nome].append(dia(data, tipo, reg["descricao"], FONTE_ID))
            else:
                cal["geral"].append(dia(data, tipo, reg["descricao"], FONTE_ID))

    cal["locais"] = locais
    return ordenar(cal)


class MotorTJRR(Motor):
    sigla = "TJRR"
    precisa_ip_brasil = False  # testado do GitHub: o PDF do DJe abre (ficha)
    parcial = (
        "Lê só a Portaria TJRR/PR n. 1558/2025 (DJe 8006). Ficam de fora os feriados e pontos "
        "decretados depois por outros Poderes, que o Art. 2º manda só comunicar à Secretaria de "
        "Gestão de Pessoas (não constam do anexo), e qualquer portaria ou retificação publicada em "
        "outra edição do DJe de 2026 (não verificado). Em 2027 ainda não há edição conhecida."
    )
    esperado = {
        "min_geral": 30,  # a ficha não traz contagem; piso abaixo dos dias gerais lidos no anexo
        "min_locais": 9,  # comarcas listadas na ficha
        # Conferidas à mão no anexo da Portaria 1558 (ficha, itens 1 a 3). Só dias gerais: o
        # validador confere `geral`.
        "ancoras": {
            "2026-01-01": "Recesso forense 01 a 06/01 (início)",
            "2026-01-06": "Recesso forense 01 a 06/01 (fim)",
            "2026-02-16": "Carnaval 16 a 18/02 (início)",
            "2026-02-18": "Quarta-feira de cinzas (fim)",
            "2026-12-20": "Recesso forense 20 a 31/12 (início)",
            "2026-12-31": "Recesso forense 20 a 31/12 (fim)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in EDICOES:
            # DUVIDA: a ficha não diz como achar a portaria do ano seguinte (o DJe com ela sai em
            # dezembro, com data que muda). Enquanto não houver a regra, o robô só registra o fato.
            raise AindaNaoPublicado(
                "a ficha do TJRR não diz como localizar o calendário de %d; a edição conhecida "
                "(DJe 8006, de 22/12/2025) traz só o exercício de 2026" % ano)
        return interpretar(pdf_para_texto(rede.baixar(EDICOES[ano])), ano)


MOTOR = MotorTJRR()
