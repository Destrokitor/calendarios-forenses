"""Motor do TJMT (Tribunal de Justiça de Mato Grosso). Ficha: docs/fichas/TJMT.md.

Fontes (ver a ficha):
  1. Portaria TJMT/PRES nº 1915/2025 (PDF com camada de texto, lido com `pdftotext -layout`):
     - Anexo I: calendário geral (tabela MÊS | DIA | FERIADO) -> `geral`;
     - Anexo II: feriados por comarca (blocos numerados 1..N, layout irregular) -> `locais`.
  2. Índice vivo "Calendário Judiciário 2026" (HTML): só a ALTERAÇÃO do Anexo I que o texto do
     índice traz por extenso (hoje, Portaria 1254/2026: Dia do Servidor 28/10 -> 30/10).

Efeito jurídico: o art. 2º da portaria manda suspender expediente E prazos em feriado e em ponto
facultativo; por isso ambos viram `sem_expediente`. 18/02 (Cinzas, a partir das 13h) é `parcial`.
Nenhum dia de recesso: o Anexo I não traz o recesso do CPC art. 220 e este motor não o inventa.

Anexo II: o `pdftotext -layout` mistura colunas em poucos casos (texto do motivo que escorre para a
linha da data vizinha). A leitura é conferida por três travas: números dos blocos 1..N seguidos,
todo bloco com nome e ao menos um dia, e dia da semana do Anexo I batendo com o calendário. Os
poucos motivos trocados de linha estão em CORRECOES_MOTIVO (conferidos à mão contra a fixture).
"""
from __future__ import annotations

import datetime
import html
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

URL_PORTARIA: Dict[int, str] = {
    2026: ("https://cms.tjmt.jus.br/Download.aspx?arquivo=%2Fintranet.arq%2Fcms%2Fgrupopaginas%2F100%2F820%2F"
           "Portaria_1915-2025-PRES_-_Calend%C3%A1rio_Forense_2026.pdf"),
}
URL_INDICE: Dict[int, str] = {
    2026: "https://www.tjmt.jus.br/paginas/transparencia-e-prestacao-contas?url=%2FInstitucional%2FC%2F82478",
}
FONTE_PORTARIA = "portaria"
FONTE_INDICE = "indice"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
         "outubro", "novembro", "dezembro"]
_DIAS_SEMANA = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6}
_SEMANA_RE = r"(?:segunda|terça|quarta|quinta|sexta|sábado|domingo)"

# O PDF grafa "ÀGUA BOA" (acento grave, erro de impressão); o nome oficial da comarca é ÁGUA BOA.
NOMES_CORRIGIDOS = {"ÀGUA BOA": "ÁGUA BOA"}

# Motivos que o pdftotext (e o próprio PDF) colocam na linha da data vizinha. Chave: (comarca, "MM-DD");
# valor: (início do texto mal lido, texto certo). Só se aplica se o texto lido for o esperado.
CORRECOES_MOTIVO: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("GUIRATINGA", "06-24"): ("São João Batista (Padroeiro) Aniversário", "São João Batista (Padroeiro)"),
    ("GUIRATINGA", "08-02"): ("do Município", "Aniversário do Município"),
    ("SÃO JOSÉ DOS QUATRO MARCOS", "06-15"): ("Aniversário do Município Emancipação", "Aniversário do Município"),
    ("SÃO JOSÉ DOS QUATRO MARCOS", "12-14"): ("Política", "Emancipação Política"),
    ("VILA BELA DA SANTÍSSIMA TRINDADE", "07-20"): (
        "Dia da Dança do Congo (Lei n. 896/2010)",
        "Dia da Dança do Congo (Lei n. 896/2010): institui a segunda-feira da segunda quinzena de julho como feriado no Município"),
    ("VILA BELA DA SANTÍSSIMA TRINDADE", "07-21"): (
        "- Institui a segunda-feira",
        "Feriado até às 12h; após às 12h, ponto facultativo (Lei n. 897/2010)"),
}

PARCIAL = (
    "Entram o Anexo I (geral) e o Anexo II (79 comarcas) da Portaria 1915/2025 e a única alteração "
    "que o índice HTML descreve de forma aplicável ao Anexo I (Portaria 1254/2026: Dia do Servidor, "
    "28/10 -> 30/10). Ficam de fora, porque o índice só traz o resumo e o PDF de cada uma não é lido: "
    "Portaria 245/2026 (suspensão excepcional do expediente, data não informada no resumo), 509/2026 "
    "(suspensão do expediente e dos prazos a partir das 13h de 06/04), 752/2026 (horário especial nos "
    "jogos do Brasil na Copa), 901/2026 (suspensão do expediente em 29/06), as suspensões de 21 e 22/09 e "
    "a suspensão parcial de 23 a 25/09, as retomadas (1370/2026: prazos suspensos até 30/09; 1384/2026: "
    "prazos administrativos de volta em 01/10) e a decisão sobre pedido da OAB. Também fora: o recesso "
    "do CPC art. 220 (20/12 a 20/01), que o Anexo I não traz, e feriados municipais de comarcas que não "
    "constam do Anexo II (a lista da portaria é por comarca)."
)


def _pdftotext(pdf: bytes) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def pdf_para_texto(pdf: bytes) -> str:
    return _pdftotext(pdf)


def baixar(rede: Cliente, ano: int) -> Tuple[bytes, bytes]:
    """Único ponto de rede: (PDF da portaria, HTML do índice)."""
    return rede.baixar(URL_PORTARIA[ano]), rede.baixar(URL_INDICE[ano])


def _juntar(texto: str, mais: str) -> str:
    mais = mais.strip()
    if texto.endswith("-") and mais[:1].islower():  # "terça-" + "feira)"
        return texto + mais
    return (texto + " " + mais).strip()


# ----------------------------------------------------------------------------- Anexo I

_MES_RE = "|".join(m.upper() for m in MESES)
_LINHA_I = re.compile(r"^\s*(?:(?P<mes>%s)\s+)?(?P<dia>\d{1,2})º?\s*\((?P<sem>[^)]*)\)\s+(?P<texto>.*)$" % _MES_RE)
_SO_MES = re.compile(r"^\s*(%s)\s*$" % _MES_RE)


def _anexo(texto: str, inicio: str, fim: Optional[str]) -> List[str]:
    linhas = texto.replace("\f", "\n").splitlines()
    try:
        i = next(n for n, l in enumerate(linhas) if l.strip() == inicio)
    except StopIteration:
        raise ErroDeFonte("não achei '%s' na portaria" % inicio)
    j = len(linhas)
    if fim:
        j = next((n for n, l in enumerate(linhas) if n > i and l.strip() == fim), len(linhas))
    return linhas[i + 1:j]


def _anexo_i(linhas: List[str], ano: int) -> List[Dict[str, str]]:
    """Linhas do Anexo I -> dias. O mês aparece só em uma linha de cada bloco (separado por linha em
    branco) e não necessariamente na primeira; bloco sem mês herda o do bloco anterior."""
    blocos: List[Dict[str, Any]] = []  # {"mes": int|None, "itens": [[dia, texto, semana]]}
    atual: Optional[Dict[str, Any]] = None
    for linha in linhas:
        if not linha.strip():
            atual = None
            continue
        if "CALEND" in linha.upper() or re.match(r"^\s*M[ÊE]S\s+DIA\s+FERIADO", linha):
            continue
        m = _LINHA_I.match(linha)
        so_mes = _SO_MES.match(linha)
        if m or so_mes:
            if atual is None:
                atual = {"mes": None, "itens": []}
                blocos.append(atual)
            nome_mes = so_mes.group(1) if so_mes else m.group("mes")
            if nome_mes:
                atual["mes"] = MESES.index(nome_mes.lower()) + 1
            if m:
                atual["itens"].append([int(m.group("dia")), m.group("texto").strip(), m.group("sem")])
        elif atual is not None and atual["itens"]:
            atual["itens"][-1][1] = _juntar(atual["itens"][-1][1], " ".join(linha.split()))
        else:
            raise ErroDeFonte("linha do Anexo I não reconhecida: %r" % linha.strip())

    dias: List[Dict[str, str]] = []
    mes_anterior: Optional[int] = None
    for bloco in blocos:
        mes, itens = bloco["mes"] or mes_anterior, bloco["itens"]
        if mes is None:
            raise ErroDeFonte("bloco do Anexo I sem mês")
        mes_anterior = mes
        for d, texto, sem in itens:
            data = datetime.date(ano, mes, d)
            esperado = next((v for k, v in _DIAS_SEMANA.items() if sem.strip().lower().startswith(k)), None)
            if esperado is None or esperado != data.weekday():
                raise ErroDeFonte("Anexo I: %s não é %r (mês lido errado?)" % (data.isoformat(), sem))
            texto = re.sub(r"Portaria(\d)", r"Portaria \1", texto)
            if texto.count("(") > texto.count(")"):
                texto += ")"
            parcial = re.search(r"expediente a partir das (\d{1,2}h)", texto, re.I)
            if parcial:
                dias.append(dia(data, "parcial", texto, FONTE_PORTARIA, "expediente a partir das %s" % parcial.group(1)))
            else:
                # Art. 2º: feriado E ponto facultativo suspendem expediente e prazos.
                dias.append(dia(data, "sem_expediente", texto, FONTE_PORTARIA))
    return dias


# ----------------------------------------------------------------------------- Anexo II

_NUM = re.compile(r"^\s*(\d{1,2})\.(?=\s|$)")
_DATA_II = re.compile(
    r"^(?P<pre>[\sA-ZÀ-ÚÇ'’.\-]*?)(?<!\d)(?P<d>\d{2})[/.](?P<m>\d{2})\s*[(9]?" + _SEMANA_RE +
    r"(?:-feira)?[)0]*\s*(?P<resto>.*)$")
_ULTIMO_FERIADO = re.compile(r"[\sA-ZÀ-ÚÇ'’.\-]+")


def _maiuscula(seg: str) -> bool:
    return seg == seg.upper() and any(c.isalpha() for c in seg)


def _anexo_ii(linhas: List[str], ano: int) -> Dict[str, List[Dict[str, str]]]:
    blocos: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for linha in linhas:
        if not linha.strip():
            continue
        up = linha.upper()
        if "CALEND" in up or re.match(r"^\s*N\.\s+COMARCA", linha):
            continue
        m = _NUM.match(linha)
        resto = linha
        if m:
            cur = {"n": int(m.group(1)), "nome": [], "linhas": []}  # linhas: [mm-dd, motivo]
            blocos.append(cur)
            resto = linha[m.end():]
        if cur is None:
            raise ErroDeFonte("Anexo II: linha antes do primeiro bloco: %r" % linha.strip())
        if not resto.strip():
            continue
        md = _DATA_II.match(resto)
        if md:
            pre = " ".join(md.group("pre").split())
            if pre:
                cur["nome"].append(pre)
            data = datetime.date(ano, int(md.group("m")), int(md.group("d")))  # ErroDeFonte-like se inválida
            cur["linhas"].append([data, " ".join(md.group("resto").split())])
            continue
        # linha sem data: pedaços em maiúscula = nome da comarca; o resto = continuação do motivo
        for seg in re.split(r"\s{2,}", resto.strip()):
            if _maiuscula(seg):
                cur["nome"].append(seg)
            elif cur["linhas"]:
                cur["linhas"][-1][1] = _juntar(cur["linhas"][-1][1], seg)
            else:
                raise ErroDeFonte("Anexo II: motivo sem data no bloco %d: %r" % (cur["n"], seg))

    if [b["n"] for b in blocos] != list(range(1, len(blocos) + 1)):
        raise ErroDeFonte("Anexo II: numeração dos blocos não é 1..N seguida: %s" % [b["n"] for b in blocos])
    locais: Dict[str, List[Dict[str, str]]] = {}
    for b in blocos:
        nome = normalizar_local(" ".join(b["nome"]).replace("’", "'"))
        nome = NOMES_CORRIGIDOS.get(nome, nome)
        if not nome or not b["linhas"]:
            raise ErroDeFonte("Anexo II: bloco %d sem nome ou sem dias" % b["n"])
        if nome in locais:
            raise ErroDeFonte("Anexo II: comarca repetida: %s" % nome)
        lista = []
        for data, motivo in b["linhas"]:
            chave = (nome, data.strftime("%m-%d"))
            if chave in CORRECOES_MOTIVO and motivo.startswith(CORRECOES_MOTIVO[chave][0]):
                motivo = CORRECOES_MOTIVO[chave][1]
            motivo = motivo.rstrip(" .") if not motivo.endswith("...") else motivo
            if not motivo:
                raise ErroDeFonte("Anexo II: %s %s sem motivo" % (nome, data.isoformat()))
            # DUVIDA: feriado de comarca e "Ponto facultativo" local viram sem_expediente (art. 2º e §1º:
            # suspendem expediente e prazos na comarca). Vila Bela, 21/07: feriado até 12h e ponto
            # facultativo depois; tratado como dia inteiro, pelo mesmo art. 2º.
            lista.append(dia(data, "sem_expediente", motivo, FONTE_PORTARIA))
        locais[nome] = lista
    return locais


# ----------------------------------------------------------------------------- índice (alterações)

_TRANSFERE = re.compile(
    r"transferir o ponto facultativo do dia (\d{1,2}) de (\w+) de (\d{4})(.{0,120}?)\bpara o dia (\d{1,2}) de (\w+) de (\d{4})",
    re.I)
_PORTARIA = re.compile(r"PORTARIA TJMT/PRES N\.?\s*(\d+)\s*/?\s*(\d{4})?", re.I)


def _texto_html(conteudo: Any) -> str:
    bruto = conteudo.decode("utf-8", "replace") if isinstance(conteudo, bytes) else conteudo
    bruto = re.sub(r"(?is)<(script|style).*?</\1>", " ", bruto)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", bruto)).replace("\xa0", " ").split())


def _data_extenso(d: str, mes: str, a: str) -> datetime.date:
    try:
        return datetime.date(int(a), MESES.index(mes.lower()) + 1, int(d))
    except ValueError:
        raise ErroDeFonte("data por extenso inválida no índice: %s de %s de %s" % (d, mes, a))


def aplicar_alteracoes(cal: Dict[str, Any], indice: Any, ano: int) -> None:
    """Aplica ao `geral` as transferências de ponto facultativo descritas no índice (HTML)."""
    texto = _texto_html(indice)
    for m in _TRANSFERE.finditer(texto):
        origem = _data_extenso(m.group(1), m.group(2), m.group(3))
        destino = _data_extenso(m.group(5), m.group(6), m.group(7))
        if origem.year != ano or destino.year != ano:
            continue
        previas = list(_PORTARIA.finditer(texto[:m.start()]))
        numero = ("%s/%s" % (previas[-1].group(1), previas[-1].group(2) or ano)) if previas else "do índice"
        alvo = [d for d in cal["geral"] if d["data"] == origem.isoformat() and "ponto facultativo" in d["motivo"].lower()]
        if len(alvo) != 1:
            raise ErroDeFonte("a alteração %s (%s -> %s) não casa com o Anexo I" % (numero, origem, destino))
        antigo = alvo[0]
        cal["geral"].remove(antigo)
        cal["geral"].append(dia(
            destino, antigo["tipo"],
            "%s [transferido de %s pela Portaria TJMT/PRES %s]" % (antigo["motivo"], origem.strftime("%d/%m"), numero),
            FONTE_INDICE))


# ----------------------------------------------------------------------------- montagem

def interpretar(conteudo: Tuple[str, Any], ano: int) -> Dict[str, Any]:
    """(texto do PDF via pdftotext -layout, HTML do índice) -> calendário. Puro: sem rede."""
    texto, indice = conteudo
    if not re.search(r"CALEND[ÁA]RIO\s+FORENSE\s+%d" % ano, texto):
        raise ErroDeFonte("a portaria lida não é o calendário forense de %d" % ano)
    cal = calendario_vazio("TJMT", ano)
    cal["fontes"] = [
        {"id": FONTE_PORTARIA, "url": URL_PORTARIA.get(ano, ""),
         "descricao": "Portaria TJMT/PRES nº 1915/2025: Anexo I (calendário geral) e Anexo II (feriados por comarca)"},
        {"id": FONTE_INDICE, "url": URL_INDICE.get(ano, ""),
         "descricao": "Índice 'Calendário Judiciário %d' do TJMT, com as alterações da portaria" % ano},
    ]
    cal["geral"] = _anexo_i(_anexo(texto, "ANEXO I", "ANEXO II"), ano)
    cal["locais"] = _anexo_ii(_anexo(texto, "ANEXO II", None), ano)
    aplicar_alteracoes(cal, indice, ano)
    return cal


class MotorTJMT(Motor):
    sigla = "TJMT"
    precisa_ip_brasil = False  # ficha: fonte aberta na nuvem (testar-urls nº 39986641769)
    parcial = PARCIAL
    esperado = {
        # A ficha não traz contagem. Lido na fixture: 24 dias gerais no Anexo I (a transferência de
        # 28/10 para 30/10 não muda o total) e 79 comarcas no Anexo II (a ficha dizia ~46).
        "min_geral": 24,
        "min_locais": 79,
        "ancoras": {
            "2026-02-18": "Cinzas (a partir das 13h)",
            "2026-04-20": "Tiradentes, ponto facultativo",
            "2026-04-21": "Tiradentes, feriado nacional",
            "2026-12-07": "Dia da Justiça",
            "2026-12-08": "Dia da Justiça",
            "2026-10-30": "Dia do Servidor (Portaria 1254/2026)",
        },
        "exige_recesso": False,  # o Anexo I não traz recesso
    }

    def anos(self, hoje: datetime.date) -> List[int]:
        return [hoje.year, hoje.year + 1]

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in URL_PORTARIA:
            # O endereço do PDF tem o ano no nome e a portaria do ano seguinte sai em dezembro.
            raise AindaNaoPublicado("o TJMT ainda não tem calendário forense de %d conhecido (ver ficha)" % ano)
        pdf, indice = baixar(rede, ano)
        return interpretar((pdf_para_texto(pdf), indice), ano)


MOTOR = MotorTJMT()
