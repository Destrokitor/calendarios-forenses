"""Motor do TRT12 (Tribunal Regional do Trabalho da 12ª Região, Santa Catarina).

Fonte única que abre na nuvem (ficha: docs/fichas/TRT12.md): Portaria SEAP nº 191/2024, republicada
em 19/05/2025 e alterada pela Portaria SEAP nº 57/2025. O próprio ato diz que "divulga os feriados a
serem observados no exercício de 2026". É um PDF com texto, lido com `pdftotext -layout`.

Estrutura do ato:
  - Anexo I, Feriados Nacionais (MÊS | DIA | MOTIVO) -> `geral`, sem_expediente.
  - Anexo I, Feriados Estaduais -> `geral`, sem_expediente (a data pode ter sido transferida).
  - Anexo I, Feriados Regimentais: tabela com "Art.153" (recesso) e "Art.154" (feriados do Tribunal)
    -> `geral`. Intervalos ("1º a 6", "16 a 18", "20 a 31") viram um Dia por data.
  - Anexo II, Feriados Municipais -> `locais[MUNICÍPIO]`, sem_expediente. Não há coluna de comarca:
    o nome do município está dentro do MOTIVO.

Efeito de cada item:
  - Art. 153 (recesso de 20/12 a 06/01) -> recesso.
  - Art. 154, feriados nacionais, estaduais e municipais -> sem_expediente.
  - Art. 2º transfere 11/08 -> 10/08, 28/10 -> 30/10 e 08/12 -> 07/12. Entra a data transferida.
  O ato não traz expediente parcial nem suspensão de prazo (tipos parcial e suspensao_prazo ficam vazios).

Cobertura: ver `parcial`. Nada disto vem do portal do TRT12 (bloqueado ao robô).
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

SIGLA = "TRT12"
URL = "https://dspace.trt12.jus.br/server/api/core/bitstreams/b401ad4a-b944-43f7-86e5-b0245fbde6b9/content"
FONTE_ID = "portaria"
FONTE_DESCRICAO = ("Portaria SEAP nº 191/2024 (republicação de 19/05/2025, alterada pela Portaria SEAP "
                   "nº 57/2025), feriados do exercício de 2026, PDF do DSpace do TRT12")

MESES = {"JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
         "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12}

_RE_MES = re.compile(r"^(JANEIRO|FEVEREIRO|MARÇO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)(?:\s+(.*))?$")
# dia ("1º", "27"), intervalo com "a" ("1º a 6") ou par com "e" ("1º e 2"), e o motivo depois de 2+ espaços
_RE_DIA = re.compile(r"^(\d{1,2})[º°]?(?:\s+(a|e)\s+(\d{1,2}))?(?:\s+(.*))?$")
_RE_RUIDO = re.compile(r"PODER JUDICIÁRIO|JUSTIÇA DO TRABALHO|TRIBUNAL REGIONAL|PROAD|^Anexo 1 -|^\d/\d{4} -"
                       r"|FERIADOS DEFINIDOS|^MÊS\b|Documento válido|Tribunal Regional do Trabalho da 12ª Região")
_RE_MARC_NAC = re.compile(r"ANEXO I\s+-\s+Feriados Nacionais")
_RE_MARC_MUN = re.compile(r"ANEXO II\s+-\s+Feriados Municipais")
_INICIO_MOTIVO = re.compile(r"^[A-ZÀ-Ú]")
_INICIO_MOTIVO_MUN = ("Fundação", "Padroeir", "Feriado", "Dia ", "Aniversário", "Corpus")
_RE_MUNICIPIO = re.compile(r"(?i)\b(?:cidades?|munic[ií]pios?)\s+(?:de|do|da|das|dos)\s+(.+)$")
_RE_FERIADO_EM = re.compile(r"^Feriado Municipal em\s+(.+)$")

RECESSO = "Recesso forense (Art. 153 do RI do TRT12)"
# Feriados regimentais do Art. 154, por dia. Os que foram transferidos pelo Art. 2º trazem a data de origem.
ART154 = {
    (2, 16): "Carnaval e Quarta-feira de Cinzas (Art. 154 do RI)",
    (2, 17): "Carnaval e Quarta-feira de Cinzas (Art. 154 do RI)",
    (2, 18): "Carnaval e Quarta-feira de Cinzas (Art. 154 do RI)",
    (4, 1): "Semana Santa (Art. 154 do RI)",
    (4, 2): "Semana Santa (Art. 154 do RI)",
    (4, 3): "Semana Santa (Art. 154 do RI)",
    (4, 4): "Semana Santa (Art. 154 do RI)",
    (4, 5): "Semana Santa (Art. 154 do RI)",
    (8, 10): "Feriado regimental transferido de 11/08 para 10/08 (Art. 154 do RI e Art. 2º da portaria)",
    (10, 30): "Feriado regimental transferido de 28/10 para 30/10 (Art. 154 do RI e Art. 2º da portaria)",
    (11, 1): "Feriado regimental (Art. 154 do RI)",
    (11, 2): "Feriado regimental (Art. 154 do RI)",
    (12, 7): "Feriado regimental transferido de 08/12 para 07/12 (Art. 154 do RI e Art. 2º da portaria)",
}

# DUVIDA: a Portaria SEAP 191 não traz data para Caçador (na extração, "Fundação da Cidade de Caçador"
# aparece sem dia) e tem um "09" de março sem motivo próprio (a linha é a quebra do motivo de 06/03,
# Xanxerê). Os dois ficam fora: nenhuma data é inventada. Ver `parcial`.
# DUVIDA: Art. 153 manda observar a suspensão de prazo do art. 220 do CPC de 20/12 a 20/01 inclusive.
# Os dias 07/01 a 20/01 não estão listados no ato como dias, então NÃO entram como suspensao_prazo.
# Quem revisa decide se entram (e em que tipo).
# DUVIDA: Corpus Christi (04/06) é feriado "em todos os Municípios-Sede de Unidades Judiciárias"; o ato
# não diz quais são as sedes. Não entra em `geral` (aplicaria a todo o tribunal) nem em `locais`.

PARCIAL = (
    "Dados de ato anterior ao ano: Portaria SEAP 191/2024, republicada em 19/05/2025 e alterada pela "
    "Portaria SEAP 57/2025. Ela divulga os feriados do exercício de 2026, e o robô lê só esta republicação "
    "(o portal do TRT12, que traz o calendário atualizado, é bloqueado ao robô). FICAM DE FORA as "
    "alterações de 2026 posteriores a 19/05/2025, em especial a Portaria SEAP 25/2026, que acrescenta "
    "20/04/2026 e 05/06/2026 como feriado regimental/ponto facultativo (segundo a ficha, não lida). "
    "Também ficam de fora: Corpus Christi (04/06) nas sedes de unidade judiciária, porque o ato não "
    "lista as sedes; a data de Fundação de Caçador e o dia 09/03 (sem motivo legível na extração); a "
    "suspensão de prazo de 07/01 a 20/01 do art. 153 (não listada como dia no ato); e municípios que não "
    "estão no Anexo II."
)


class MotorTRT12(Motor):
    sigla = SIGLA
    precisa_ip_brasil = False
    parcial = PARCIAL
    esperado = {
        # A ficha não traz contagem. Piso = o que li na fixture (ver test_trt12).
        "min_geral": 40,
        "min_locais": 30,
        "ancoras": {        # só dias GERAIS: a validação confere em `geral`
            "2026-01-01": "Confraternização Universal (nacional) e recesso",
            "2026-01-06": "Recesso forense (Art. 153)",
            "2026-02-16": "Carnaval (Art. 154)",
            "2026-02-18": "Quarta-feira de Cinzas (Art. 154)",
            "2026-04-01": "Semana Santa (Art. 154)",
            "2026-04-05": "Domingo de Páscoa, fim da Semana Santa (Art. 154)",
            "2026-08-10": "Feriado regimental transferido de 11/08 (Art. 154 e Art. 2º)",
            "2026-08-16": "Data Magna de SC, transferida do dia 11 (Lei 18.531/2022)",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        pdf = rede.baixar(URL)
        return interpretar(pdf_para_texto(pdf), ano)


def _pdftotext(pdf: bytes) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0:
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def pdf_para_texto(pdf: bytes) -> str:
    """Único ponto que roda pdftotext. `interpretar` só recebe o texto."""
    return _pdftotext(pdf)


def _motivo_valido(motivo: str) -> bool:
    return bool(motivo) and bool(_INICIO_MOTIVO.match(motivo))


def _continua(motivo_anterior: str, linha: str) -> bool:
    """Linha sem data que completa o motivo da linha anterior (quebra de texto do PDF)."""
    if motivo_anterior.count("(") > motivo_anterior.count(")"):
        return True
    if motivo_anterior.endswith("-"):
        return True
    return linha[:1].islower() or linha[:1].isdigit() or linha[:1] in "*“\"("


def _ler_ato(texto: str) -> List[Dict[str, Any]]:
    """Percorre o texto do pdftotext e devolve os registros de data: secao, mes, dias e motivo."""
    registros: List[Dict[str, Any]] = []
    secao: Optional[str] = None
    mes: Optional[int] = None
    atual: Optional[Dict[str, Any]] = None
    for bruta in texto.splitlines():
        linha = bruta.replace("​", " ").strip()
        if not linha:
            continue
        if _RE_MARC_NAC.search(linha):
            secao, mes, atual = "nac", None, None
            continue
        if _RE_MARC_MUN.search(linha):
            secao, mes, atual = "mun", None, None
            continue
        if linha == "Feriados Estaduais":
            secao, mes, atual = "est", None, None
            continue
        if linha == "Feriados Regimentais":
            secao, mes, atual = "reg", None, None
            continue
        if _RE_RUIDO.search(linha):          # cabeçalho e rodapé de página
            atual = None
            continue
        if secao is None:
            continue
        # Quebra do motivo: texto recuado além da coluna DIA (>= 42 espaços; a DIA fica em 37 a 39).
        # Ex.: "16 de maio de 2025)" de Xanxerê, que começa com número mas não é data.
        recuo = len(bruta) - len(bruta.lstrip(" "))
        if atual is not None and recuo >= 42 and _continua(atual["motivo"], linha):
            atual["motivo"] = atual["motivo"] + " " + linha
            continue
        m = _RE_MES.match(linha)
        if m:
            mes = MESES[m.group(1)]
            resto = m.group(2) or ""
            atual = None
        else:
            resto = linha
        if not resto:
            continue
        d = _RE_DIA.match(resto)
        if d:
            if mes is None:
                raise ErroDeFonte("linha de data antes de qualquer mês: %r" % linha)
            n1 = int(d.group(1))
            if d.group(2) == "a":
                dias = list(range(n1, int(d.group(3)) + 1))
            elif d.group(2) == "e":
                dias = [n1, int(d.group(3))]
            else:
                dias = [n1]
            motivo = " ".join((d.group(4) or "").split())
            if not motivo:
                raise ErroDeFonte("linha de data sem motivo: %r" % linha)
            if not _motivo_valido(motivo):
                # "09   16 de maio de 2025)": a data não tem motivo; o texto é a quebra da linha anterior.
                if atual is None:
                    raise ErroDeFonte("texto solto sem linha anterior: %r" % linha)
                atual["motivo"] = atual["motivo"] + " " + motivo
                atual = None
                continue
            atual = {"secao": secao, "mes": mes, "dias": dias, "motivo": motivo}
            registros.append(atual)
            continue
        if atual is not None and _continua(atual["motivo"], linha):
            atual["motivo"] = atual["motivo"] + " " + linha
            continue
        atual = None
        if secao == "mun" and linha.startswith(_INICIO_MOTIVO_MUN):
            # motivo municipal sem data na extração (ex.: Caçador): guarda só o nome, sem dia
            atual = {"secao": secao, "mes": mes, "dias": [], "motivo": linha}
            registros.append(atual)
    return registros


def _municipios(motivo: str) -> List[str]:
    if motivo.startswith("Corpus Christi"):
        return []  # feriado nas sedes; o ato não lista as sedes (ver DUVIDA no topo)
    sem_parenteses = motivo.split("(")[0].strip(" -")
    m = _RE_MUNICIPIO.search(sem_parenteses) or _RE_FERIADO_EM.match(sem_parenteses)
    if not m:
        raise ErroDeFonte("motivo municipal sem nome de município: %r" % motivo)
    return [n for n in re.split(r",\s*|\s+e\s+", m.group(1).strip()) if n]


def _motivo_geral(secao: str, mes: int, dia_n: int, motivo: str) -> tuple:
    """Devolve (tipo, motivo) para uma linha de Anexo I."""
    if secao in ("nac", "est"):
        return "sem_expediente", motivo
    if "Art.153" in motivo:
        return "recesso", RECESSO
    if "Art.154" in motivo:
        if (mes, dia_n) not in ART154:
            raise ErroDeFonte("feriado regimental sem texto conhecido: %d/%d" % (dia_n, mes))
        return "sem_expediente", ART154[(mes, dia_n)]
    raise ErroDeFonte("linha regimental fora de Art.153/Art.154: %r" % motivo)


def interpretar(texto: str, ano: int) -> Dict[str, Any]:
    """Lê o texto do pdftotext -layout da portaria e devolve o calendário do ano pedido. Não usa rede."""
    if "PORTARIA SEAP" not in texto or "FERIADOS DEFINIDOS PARA O EXERCÍCIO DE" not in texto:
        raise ErroDeFonte("o texto não é a Portaria SEAP de feriados do TRT12: o formato mudou")
    if "EXERCÍCIO DE %d" % ano not in texto:
        raise AindaNaoPublicado("a fonte do TRT12 não traz o exercício de %d" % ano)

    cal = calendario_vazio(SIGLA, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": URL, "descricao": FONTE_DESCRICAO}]
    registros = _ler_ato(texto)
    if not registros:
        raise ErroDeFonte("nenhuma linha de data encontrada no ato: o formato mudou")

    for r in registros:
        for dia_n in r["dias"]:
            try:
                data = datetime.date(ano, r["mes"], dia_n)
            except ValueError:
                raise ErroDeFonte("data inválida no ato: %d/%d" % (dia_n, r["mes"]))
            if r["secao"] == "mun":
                for nome in _municipios(r["motivo"]):
                    cal["locais"].setdefault(normalizar_local(nome), []).append(
                        dia(data, "sem_expediente", r["motivo"], FONTE_ID))
            else:
                tipo, motivo = _motivo_geral(r["secao"], r["mes"], dia_n, r["motivo"])
                cal["geral"].append(dia(data, tipo, motivo, FONTE_ID))
        if r["secao"] == "mun" and not r["dias"]:
            for nome in _municipios(r["motivo"]):
                cal["locais"].setdefault(normalizar_local(nome), [])

    if not cal["geral"]:
        raise ErroDeFonte("nenhum dia geral lido do ato: o formato mudou")
    return ordenar(cal)


MOTOR = MotorTRT12()
