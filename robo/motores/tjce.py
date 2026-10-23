"""Motor do TJCE (Tribunal de Justiça do Estado do Ceará). Ficha: docs/fichas/TJCE.md.

Fonte única, oficial (Portaria nº 2924/2025, Presidência, DJE Administrativo ed. 3690, de 17/12/2025,
Anexo Único). O anexo é uma tabela MÊS/ANO | DIA(S) | JUSTIFICATIVA/NATUREZA, lida com
`pdftotext -layout`. Cada linha do texto tem a coluna do dia à esquerda (x < 32 caracteres) e a da
justificativa à direita. O mês vem numa linha solta (rótulo), não em cada linha.

Como a tabela é lida (sem adivinhar):
  - cada número de dia é ligado ao mês pelo rótulo de mês mais próximo na tabela;
  - cada justificativa é ligada aos dias pela proximidade de linha; o dia que cai no texto do ato
    ("16 e 17/02/2026", "18/02/2026") é ligado pela própria data citada;
  - o dia da semana impresso ao lado do número é conferido contra o calendário; diferença = ErroDeFonte;
  - se a contagem de dias e de justificativas não bater, ErroDeFonte. Nunca se inventa data.

Efeito de cada item:
  - feriado (nacional, estadual) -> sem_expediente;
  - ponto facultativo -> sem_expediente: o Art. 1º fixa "datas em que não haverá expediente forense".
    DUVIDA: o efeito sobre o prazo fica para a revisão (a ficha pede esse tratamento);
  - 18/02 (Quarta-feira de Cinzas): "ponto facultativo até as 14h", expediente só a partir das 14h
    -> parcial, com horario. Os núcleos de custódia abrem às 08h (não entra como local);
  - Recesso Natalino (20/12 a 06/01, Res. CNJ 244/2016) -> recesso. DUVIDA: o ato chama de
    "Ponto facultativo"; o tipo recesso segue o nome do item, para a revisão confirmar.

Fora (ver `parcial`): feriados e pontos municipais (Art. 2º: seguem a lei de cada município; o
tribunal não os publica), alterações por portaria própria (ex.: Portaria nº 1169/2026) e o ano
seguinte (a portaria traz só 01 a 06/01/2027).
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

FONTE_URL = "https://portal.tjce.jus.br/uploads/2026/04/PORT-FERIADOS-E-PONTO-FACULTATIVO-2026-1776690769.pdf"
FONTE_ID = "portaria"
FONTE_DESCRICAO = ("Portaria nº 2924/2025 (Presidência), DJE Administrativo ed. 3690, de 17/12/2025, "
                   "Anexo Único (feriados e pontos facultativos, jan/2026 a jan/2027)")

# Só o exercício de 2026 está na portaria por inteiro. Para 2027 a portaria traz só 01 a 06/01.
ANOS_COBERTOS = (2026,)

# Coluna da justificativa no texto do pdftotext -layout: começa em x >= 33; a coluna do dia termina antes de 31.
COL_JUSTIFICATIVA = 32

_MESES = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO",
          "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
_MES_NUM = {nome: i + 1 for i, nome in enumerate(_MESES)}
_DIA_SEMANA = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4}

_RE_ROTULO_MES = re.compile(r"^\s*(?:\d{2} DE )?(%s)\b" % "|".join(_MESES))
_RE_NUMERO_DIA = re.compile(r"(?<![\d/])(\d{2})(?![\d/])")
_RE_SEMANA = re.compile(r"\((segunda|terça|quarta|quinta|sexta)-")
# Linhas do recesso (o recesso é lido à parte, pelo texto inteiro): saem da leitura de dias.
_RE_RECESSO_NA_COLUNA_DIA = re.compile(r"\bDE\b|DEZEMBRO|JANEIRO|Portaria|nº|DJEA|\d{2}/\d{2}/\d{4}")
_RE_RECESSO_NA_JUSTIFICATIVA = re.compile(r"Recesso|Nacional de Justiça")
# Data citada no próprio texto do ato: "(16 e 17/02/2026 - ...", "(18/02/2026 - ...".
_RE_DATA_CITADA = re.compile(r"\(((?:\d{2} e )?\d{2})/(\d{2})/(\d{4})")
_RE_RECESSO_DEZ_JAN = re.compile(r"(\d{2}) DE DEZEMBRO DE (\d{4}) a (\d{2}) JANEIRO DE (\d{4})")
_RE_RECESSO_NATALINO = re.compile(r"(\d{2})/(\d{2})/(\d{4}) a\s+Recesso Natalino.*?(\d{2})/(\d{2})/(\d{4})")
_RE_PARCIAL = re.compile(r"expediente normal único a partir das (\d{1,2})h", re.I)
_RE_CUSTODIA = re.compile(r"custódia[^)]*?a partir das (\d{1,2})h", re.I)
_RE_LINHA_DE_CABECALHO = re.compile(
    r"Diário da Justiça|Página \d|Edição:|Fortaleza - CE|MÊS /ANO|DIA\(S\)|JUSTIFICATIVA|ANEXO ÚNICO|FERIADOS E PONTOS")


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


def _anexo(texto: str) -> List[str]:
    """Linhas do Anexo Único, sem cabeçalho/rodapé de página."""
    if not re.search(r"PORTARIA Nº 2924/2025", texto):
        raise ErroDeFonte("não achei a Portaria nº 2924/2025 no texto")
    a = texto.find("ANEXO ÚNICO DA PORTARIA")
    if a == -1:
        raise ErroDeFonte("não achei o Anexo Único da Portaria 2924/2025")
    fim = texto.find("Para visualizar", a)
    corpo = texto[a:] if fim == -1 else texto[a:fim]
    linhas = []
    for linha in corpo.replace("\f", "\n").split("\n"):
        if not linha.strip() or _RE_LINHA_DE_CABECALHO.search(linha):
            linhas.append("")  # mantém a posição das linhas (distância entre dias e justificativas)
            continue
        linhas.append(linha.rstrip())
    return linhas


def _ler_tabela(linhas: List[str], ano: int) -> Tuple[List[Tuple[int, int]], List[Tuple[int, str]],
                                                     List[Tuple[int, int]], List[List[int]], List[str]]:
    """Separa a tabela em: (linha, mês) dos rótulos; (linha, dia) dos números de dia; (linha, texto)
    das justificativas. Devolve também os blocos de justificativa (linhas contíguas)."""
    rotulos: List[Tuple[int, int]] = []
    dias: List[Tuple[int, int]] = []
    justificativas: List[Tuple[int, str]] = []
    for i, linha in enumerate(linhas):
        coluna_dia = linha[:COL_JUSTIFICATIVA]
        texto = linha[COL_JUSTIFICATIVA:].strip()
        m = _RE_ROTULO_MES.match(coluna_dia)
        if m:
            rotulos.append((i, _MES_NUM[m.group(1)]))
        if not coluna_dia.strip() and not texto:
            continue
        if _RE_RECESSO_NA_COLUNA_DIA.search(coluna_dia) or _RE_RECESSO_NA_JUSTIFICATIVA.search(texto):
            continue
        for m in _RE_NUMERO_DIA.finditer(coluna_dia):
            dias.append((i, int(m.group(1))))
        if texto:
            justificativas.append((i, texto))
    blocos: List[List[int]] = []  # cada bloco: índices de linha contíguos de justificativa
    textos_por_bloco: List[str] = []
    ultimo = None
    for i, texto in justificativas:
        if ultimo is not None and i == ultimo + 1:
            blocos[-1].append(i)
            textos_por_bloco[-1] += " " + texto
        else:
            blocos.append([i])
            textos_por_bloco.append(texto)
        ultimo = i
    return rotulos, dias, justificativas, blocos, textos_por_bloco


def _mes_do_dia(linha: int, rotulos: List[Tuple[int, int]]) -> int:
    """Mês do dia: o rótulo de mês mais próximo na tabela (empate: o primeiro)."""
    if not rotulos:
        raise ErroDeFonte("tabela sem rótulo de mês")
    return min(rotulos, key=lambda r: (abs(r[0] - linha), r[0]))[1]


def _nome_e_natureza(texto: str) -> Tuple[str, str]:
    """('Dia de São José', 'ponto facultativo') a partir do texto da justificativa."""
    texto = " ".join(texto.replace("“", "").replace("”", "").split())
    nome = texto.split(" (")[0].strip() if " (" in texto else texto.rstrip(". ").strip()
    resto = texto[len(nome):]
    return nome, resto


def _motivo(texto: str) -> str:
    nome, resto = _nome_e_natureza(texto)
    if "ponto facultativo" in resto.lower():
        return "%s (ponto facultativo)" % nome
    return nome


def _tipo_e_horario(texto: str) -> Tuple[str, str]:
    m = _RE_PARCIAL.search(texto)
    if m:
        horario = "expediente a partir das %sh" % m.group(1)
        c = _RE_CUSTODIA.search(texto)
        if c:
            horario += " (custódia a partir das %sh)" % c.group(1)
        return "parcial", horario
    return "sem_expediente", ""


def _dia_da_semana_ok(data: datetime.date, linhas: List[str], linha: int) -> None:
    """Confere o dia da semana impresso ao lado do número, se houver (mesma linha ou a seguinte)."""
    for j in (linha, linha + 1):
        if j >= len(linhas):
            break
        m = _RE_SEMANA.search(linhas[j][:COL_JUSTIFICATIVA])
        if m:
            if data.weekday() != _DIA_SEMANA[m.group(1)]:
                raise ErroDeFonte("dia da semana não confere com %s (%s)" % (data.isoformat(), m.group(1)))
            return


def _recesso(texto_inteiro: str, ano: int) -> List[datetime.date]:
    """Dias de recesso natalino dentro do ano: '20 DE DEZEMBRO DE 2025 a 06 JANEIRO DE 2026' e
    '20/12/2026 a ... 06/01/2027'. Só os do ano pedido."""
    plano = " ".join(texto_inteiro.split())
    trechos = []
    m1 = _RE_RECESSO_DEZ_JAN.search(plano)
    if m1:
        trechos.append((datetime.date(int(m1.group(2)), 12, int(m1.group(1))),
                        datetime.date(int(m1.group(4)), 1, int(m1.group(3)))))
    m2 = _RE_RECESSO_NATALINO.search(plano)
    if m2:
        trechos.append((datetime.date(int(m2.group(3)), int(m2.group(2)), int(m2.group(1))),
                        datetime.date(int(m2.group(6)), int(m2.group(5)), int(m2.group(4)))))
    if len(trechos) != 2:
        raise ErroDeFonte("não achei os dois trechos do recesso natalino no anexo")
    dias: List[datetime.date] = []
    for ini, fim in trechos:
        n = (fim - ini).days + 1
        dias.extend(ini + datetime.timedelta(days=k) for k in range(n))
    return [d for d in dias if d.year == ano]


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto do DJE (pdftotext -layout) -> calendário no formato de modelo.py. Sem rede."""
    if ano not in ANOS_COBERTOS:
        raise ErroDeFonte("a Portaria 2924/2025 não traz o exercício de %d" % ano)
    linhas = _anexo(conteudo)
    if "JANEIRO DE 2026" not in " ".join(linhas):
        raise ErroDeFonte("o anexo não é o de janeiro de 2026 a janeiro de 2027")

    cal = calendario_vazio(MotorTJCE.sigla, ano)
    cal["fontes"] = [{"id": FONTE_ID, "url": FONTE_URL, "descricao": FONTE_DESCRICAO}]

    for d in _recesso(conteudo, ano):
        cal["geral"].append(dia(d, "recesso", "Recesso Natalino (ponto facultativo; Res. CNJ 244/2016)", FONTE_ID))

    rotulos, numeros, justificativas, blocos, textos = _ler_tabela(linhas, ano)

    # 1) Dias com data citada no próprio texto do ato: a data vale (e o número sai da contagem).
    usados = set()
    for bloco, texto in zip(blocos, textos):
        m = _RE_DATA_CITADA.search(texto)
        if not m:
            continue
        numeros_citados = re.findall(r"\d{2}", m.group(1))
        mes, ano_citado = int(m.group(2)), int(m.group(3))
        if ano_citado != ano:
            raise ErroDeFonte("data citada no ato de %d, não de %d: %s" % (ano_citado, ano, texto[:80]))
        tipo, horario = _tipo_e_horario(texto)
        motivo = _motivo(texto)
        for n in numeros_citados:
            n = int(n)
            # a data citada tem de existir como número na tabela, na área deste bloco
            cand = [k for k, (lin, valor) in enumerate(numeros)
                    if valor == n and k not in usados and min(abs(lin - b) for b in bloco) <= 2]
            if not cand:
                raise ErroDeFonte("dia %02d do ato não achado na tabela" % n)
            usados.add(cand[0])
            data = datetime.date(ano, mes, n)
            _dia_da_semana_ok(data, linhas, numeros[cand[0]][0])
            cal["geral"].append(dia(data, tipo, motivo, FONTE_ID, horario))

    # 2) Demais dias: cada número vai ao bloco de justificativa mais próximo na tabela.
    sem_data = [k for k in range(len(numeros)) if k not in usados]
    donos: Dict[int, int] = {}
    for k in sem_data:
        lin = numeros[k][0]
        escolhido = min(
            (b for b in range(len(blocos)) if textos[b] and not _RE_DATA_CITADA.search(textos[b])),
            key=lambda b: (min(abs(lin - x) for x in blocos[b]), b),
        )
        donos[k] = escolhido
    for b in range(len(blocos)):
        if _RE_DATA_CITADA.search(textos[b]):
            continue
        if b not in donos.values():
            raise ErroDeFonte("justificativa sem dia na tabela: %s" % textos[b][:80])

    for k in sem_data:
        lin, n = numeros[k]
        bloco = donos[k]
        mes = _mes_do_dia(lin, rotulos)
        data = datetime.date(ano, mes, n)  # ErroDeFonte implícito se a data não existir
        _dia_da_semana_ok(data, linhas, lin)
        tipo, horario = _tipo_e_horario(textos[bloco])
        cal["geral"].append(dia(data, tipo, _motivo(textos[bloco]), FONTE_ID, horario))

    # DUVIDA: pontos facultativos viram sem_expediente (ver docstring); efeito sobre prazo fica para a revisão.
    # DUVIDA: o Recesso Natalino é tipo recesso pelo nome; o ato o chama de "Ponto facultativo".

    cal["locais"] = {}  # o tribunal não publica feriados municipais (Art. 2º): ver `parcial`
    datas = [(d["data"], d["motivo"]) for d in cal["geral"]]
    if len(datas) != len(set(datas)):
        raise ErroDeFonte("dia repetido no calendário geral")
    return _ordenar(cal)


def _ordenar(cal: Dict[str, Any]) -> Dict[str, Any]:
    cal["geral"] = sorted(cal["geral"], key=lambda d: (d["data"], d["tipo"], d["motivo"]))
    return cal


class MotorTJCE(Motor):
    sigla = "TJCE"
    precisa_ip_brasil = False  # testado na nuvem: ver docs/fichas/TJCE.md
    parcial = (
        "Lê só a Portaria nº 2924/2025 (DJE ed. 3690), que fixa o calendário de jan/2026 a jan/2027. "
        "FICAM DE FORA: (1) feriados e pontos municipais (Art. 2º: seguem a lei de cada município; "
        "o tribunal não publica a lista; Fortaleza e demais municípios não aparecem, e `locais` fica "
        "vazio); (2) alterações por portaria própria, cada uma avulsa e sem índice (ex.: Portaria nº "
        "1169/2026, ponto facultativo em 05/06/2026, não lida); (3) o recesso de 01 a 06/01/2027, que "
        "cai no ano seguinte. O expediente das custódias (núcleos e varas de custódia, a partir das 08h) "
        "não é local e fica só no texto do horário de 18/02. Em 2027 não há calendário próprio lido."
    )
    esperado = {
        # A ficha não traz contagem. Lidos no anexo: 34 dias gerais (18 recesso + 16 feriados/pontos);
        # piso um pouco abaixo do lido.
        "min_geral": 30,
        "min_locais": 0,
        "ancoras": {
            "2026-02-18": "Quarta-feira de Cinzas (parcial até 14h)",
            "2026-03-25": "Data Magna",
            "2026-04-21": "Tiradentes",
            "2026-12-08": "Dia da Justiça",
            "2026-12-20": "Recesso Natalino (início)",
        },
        "exige_recesso": True,
    }

    def anos(self, hoje: datetime.date) -> List[int]:
        # O ato cobre 2026 inteiro; o ano seguinte só existe em calendário próprio (ver coletar).
        return [hoje.year, hoje.year + 1]

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in ANOS_COBERTOS:
            raise AindaNaoPublicado(
                "o TJCE ainda não publicou calendário próprio de %d (a Portaria 2924/2025 traz só 01 a 06/01/%d)"
                % (ano, ano))
        pdf = rede.baixar(FONTE_URL)
        return interpretar(pdf_para_texto(pdf), ano)


MOTOR = MotorTJCE()
