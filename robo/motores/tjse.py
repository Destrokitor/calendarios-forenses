"""Motor do TJSE (Tribunal de Justiça de Sergipe). Ficha: docs/fichas/TJSE.md.

Fonte única: o PDF "Calendário 2026 — Comarcas de Aracaju e do interior do Estado e
respectivos distritos", publicado pelo próprio tribunal (texto com camada de texto, lido com
`pdftotext -layout`). Cada mês tem duas colunas:

  - FERIADOS - COMARCAS/DISTRITOS (esquerda): entra no calendário;
  - PREVISÃO DE PONTOS FACULTATIVOS (direita): NÃO entra (ver `PARCIAL` e os comentários).

A coluna da direita é cortada pela largura da página (`coluna_feriados`), porque o
`pdftotext -layout` sozinho mistura as duas colunas quando a posição muda de mês para mês.

Na coluna de feriados, quem tem parênteses é local ("Capela (Padroeira)", "Aracaju (Aniversário
da Capital)"): o nome antes do parêntese é o município e o texto dentro é o motivo. Quem não
tem parênteses vale para o estado inteiro (feriado geral). O recesso forense vem no rodapé.

Abrangência: o que é feriado geral vai em `geral`; o que é de um município vai em
`locais[MUNICÍPIO]`. Pelo PDF, só entram os municípios que aparecem com feriado; comarca sem
feriado municipal não aparece no PDF e, por isso, não entra na lista de locais.
"""
from __future__ import annotations

import datetime
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

# Calendário de cada ano (PDF do TJSE). Ano que não está aqui levanta AindaNaoPublicado:
# o endereço de 2026 tem o ano no nome, então o de 2027 vai ser outro.
CALENDARIOS: Dict[int, str] = {
    2026: "https://www.tjse.jus.br/portal/arquivos/documentos/publicacoes/calendarios/calendario-tjse-2026.pdf",
}
FONTE_ID = "calendario"

# Geometria da página (pontos), medida na fixture de 23/10/2026 com `pdftotext -bbox`: o texto
# da coluna FERIADOS termina em x≈314 e o da coluna PREVISÃO começa em x≈320,6. O corte em 318
# separa as duas com folga. Altura: página A4 (841,92 pt).
LARGURA_COLUNA_FERIADOS = 318
ALTURA_PAGINA = 842

# Início de item: "02/02 – Capela (Padroeira)", "17/02 - Carnaval" (travessão ou hífen).
_INICIO_ITEM = re.compile(r"^(\d{2})/(\d{2})\s*[–-]\s*(.*)$")
_RECESSO = re.compile(
    r"RECESSO\s+FORENSE\s*[–-]\s*DE\s+(\d{2})/(\d{2})/(\d{4})\s+A\s+(\d{2})/(\d{2})/(\d{4})", re.I)

PARCIAL = (
    "Ficam de fora os PONTOS FACULTATIVOS (coluna 'PREVISÃO DE PONTOS FACULTATIVOS'): são "
    "previsão, e só viram dia sem expediente por portaria normativa avulsa (ex.: PN 18/2026-GP1, "
    "PN 24/2026, PN 72/2026), divulgada em notícias do tribunal que este motor não lê (o host "
    "agencia.tjse.jus.br deu timeout em teste). Exemplos fora: 16/02, 18/02, 16/03 (só Aracaju), "
    "02/04, 20/04, 05/06, 29/06, 10/08 e 07/12. Também fora: portarias avulsas e comunicados "
    "de unidade específica, e o recesso de 01 a 06/01/2027, que cai no ano seguinte e vem no "
    "calendário de 2027. Comarca sem feriado municipal no PDF não aparece em locais."
)


def _pdftotext(pdf: bytes, args: List[str]) -> str:
    try:
        r = subprocess.run(["pdftotext", "-layout"] + args + ["-", "-"], input=pdf, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=120)
    except FileNotFoundError:
        raise ErroDeFonte("pdftotext não instalado (apt-get install poppler-utils)")
    if r.returncode != 0 or not r.stdout.strip():
        raise ErroDeFonte("pdftotext falhou: %s" % r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout.decode("utf-8", "replace")


def pdf_para_texto(pdf: bytes) -> str:
    """Texto da página inteira (com as duas colunas)."""
    return _pdftotext(pdf, [])


def coluna_feriados(pdf: bytes) -> str:
    """Texto pronto para `interpretar`: a coluna FERIADOS (recorte à esquerda) e, no fim, a linha
    do recesso lida da página inteira, porque o rodapé do recesso passa do corte."""
    esquerda = _pdftotext(pdf, ["-x", "0", "-y", "0", "-W", str(LARGURA_COLUNA_FERIADOS), "-H", str(ALTURA_PAGINA)])
    rodape = [linha for linha in pdf_para_texto(pdf).splitlines() if "RECESSO FORENSE" in linha.upper()]
    return esquerda + "\n" + "\n".join(rodape) + "\n"


def _itens(texto: str) -> List[Tuple[int, int, str]]:
    """(dia, mês, texto) de cada item da coluna de feriados. Junta a linha quebrada: um item
    só fecha quando os parênteses e as aspas estão equilibrados."""
    itens: List[Tuple[int, int, str]] = []
    pendente: Optional[List[Any]] = None  # [dia, mês, texto] ainda aberto
    for linha in texto.splitlines():
        if "RECESSO" in linha.upper():
            continue
        esq = " ".join(linha.split())
        if not esq:
            continue
        m = _INICIO_ITEM.match(esq)
        if m:
            if pendente is not None:
                itens.append(tuple(pendente))
            pendente = [int(m.group(1)), int(m.group(2)), m.group(3).strip()]
        elif pendente is not None:
            pendente[2] = (pendente[2] + " " + esq).strip()  # continuação de linha quebrada
        else:
            continue  # cabeçalho ou texto solto, sem item aberto
        if _equilibrado(pendente[2]):
            itens.append(tuple(pendente))
            pendente = None
    if pendente is not None:
        itens.append(tuple(pendente))
    return itens


def _equilibrado(texto: str) -> bool:
    return texto.count("(") == texto.count(")") and texto.count("“") == texto.count("”")


def _classificar(texto: str) -> Tuple[Optional[str], str]:
    """(município ou None, motivo). Parênteses = município; as aspas do PDF são retiradas."""
    limpo = " ".join(texto.replace("“", "").replace("”", "").replace("’", "'").split())
    if limpo.endswith(")") and "(" in limpo:
        i = limpo.index("(")
        return limpo[:i].strip(), limpo[i + 1:-1].strip()
    return None, limpo


def _recesso(texto: str, ano: int) -> List[datetime.date]:
    """Datas do recesso forense dentro do ano. O rodapé diz 'DE 20/12/2026 A 06/01/2027'."""
    m = _RECESSO.search(" ".join(texto.split()))
    if not m:
        raise ErroDeFonte("não achei a linha 'RECESSO FORENSE' no calendário de %d" % ano)
    ini = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    fim = datetime.date(int(m.group(6)), int(m.group(5)), int(m.group(4)))
    if ini.year != ano:
        raise ErroDeFonte("recesso do calendário começa em %s, não em %d" % (ini.isoformat(), ano))
    dias = [ini + datetime.timedelta(days=n) for n in range((fim - ini).days + 1)]
    # DUVIDA: 01 a 06/01/2027 caem no ano seguinte; o calendário de 2027 é que os traz.
    return [d for d in dias if d.year == ano]


def interpretar(conteudo: str, ano: int) -> Dict[str, Any]:
    """Texto de `coluna_feriados` -> calendário no formato de modelo.py.

    Puro: não faz rede nem roda pdftotext. Levanta ErroDeFonte se o texto não for o de `ano`
    ou se a coluna de pontos facultativos tiver vazado para a leitura."""
    achou = re.search(r"CALEND[ÁA]RIO\s+(\d{4})", conteudo)
    if achou and int(achou.group(1)) != ano:
        raise ErroDeFonte("o PDF é o calendário de %s, não de %d" % (achou.group(1), ano))
    if "FACULTATIV" in conteudo.upper():
        raise ErroDeFonte("coluna de pontos facultativos entrou na leitura: o corte da página mudou")

    cal = calendario_vazio("TJSE", ano)
    cal["fontes"] = [{
        "id": FONTE_ID, "url": CALENDARIOS.get(ano, ""),
        "descricao": "Calendário %d do TJSE (comarcas de Aracaju e do interior): feriados e recesso" % ano,
    }]

    for d in _recesso(conteudo, ano):
        cal["geral"].append(dia(d, "recesso", "Recesso forense", FONTE_ID))

    por_municipio: Dict[str, List[Dict[str, str]]] = {}
    for dd, mm, texto in _itens(conteudo):
        data = datetime.date(ano, mm, dd)  # ErroDeFonte se a data não existir no ano
        municipio, motivo = _classificar(texto)
        if not motivo:
            raise ErroDeFonte("feriado sem motivo em %s" % data.isoformat())
        if municipio is None:
            cal["geral"].append(dia(data, "sem_expediente", motivo, FONTE_ID))
        else:
            chave = normalizar_local(municipio)
            por_municipio.setdefault(chave, []).append(dia(data, "sem_expediente", motivo, FONTE_ID))

    # DUVIDA: pontos facultativos NÃO viram sem_expediente: a ficha diz que são previsão e só
    # suspendem o expediente por portaria avulsa. Ficam fora (ver PARCIAL).
    # Feriado municipal fica em locais mesmo quando cai no mesmo dia de um geral (ex.: Aracaju,
    # 08/12): é o que o PDF publica para o município, e o efeito no geral não muda.
    cal["locais"] = por_municipio
    return cal


class MotorTJSE(Motor):
    sigla = "TJSE"
    precisa_ip_brasil = False  # a ficha registra o teste na nuvem: ver docs/fichas/TJSE.md
    parcial = PARCIAL
    esperado = {
        # min_geral: a ficha não traz a contagem. Lido na fixture de 23/10/2026: 28 dias gerais
        # (16 feriados + 12 de recesso). Piso = o lido.
        "min_geral": 28,
        # min_locais: a ficha diz "~90 linhas municipais", mas a chave é por município. Lido:
        # 51 municípios distintos (116 linhas municipais). Piso = os 51 lidos.
        # DUVIDA: a diferença entre "~90" da ficha e 116 linhas lidas fica para a revisão.
        "min_locais": 51,
        # Conferidas à mão no PDF (ver ficha, âncoras 2, 3, 4 e 5). A âncora 1 (Aracaju,
        # 17/03) é de município, então fica fora de `geral`.
        "ancoras": {
            "2026-02-17": "Carnaval",
            "2026-07-08": "Emancipação Política de Sergipe",
            "2026-08-11": "Dia do Magistrado",
            "2026-10-30": "Dia do Funcionário Público",
            "2026-12-20": "Recesso forense",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        if ano not in CALENDARIOS:
            raise AindaNaoPublicado("o TJSE ainda não publicou o calendário de %d" % ano)
        pdf = rede.baixar(CALENDARIOS[ano])
        return interpretar(coluna_feriados(pdf), ano)


MOTOR = MotorTJSE()
