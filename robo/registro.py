"""Lista de todos os tribunais cobertos pelo projeto (64) e quem ainda não tem motor.

Ficam de fora, por decisão do dono do projeto, a Justiça Eleitoral (TSE e os 27 TREs).
A lista é construída aqui, e não à mão em outro lugar, para que `dados/cobertura.json`
sempre mostre os 64, inclusive os que ainda estão sem motor.
"""
from __future__ import annotations

from typing import Dict, List

_UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def todos_os_tribunais() -> List[Dict[str, str]]:
    """Cada item: sigla, nome, justica. A sigla é a chave em `dados/` e na cobertura."""
    lista: List[Dict[str, str]] = []

    for sigla, nome in [
        ("STF", "Supremo Tribunal Federal"),
        ("STJ", "Superior Tribunal de Justiça"),
        ("TST", "Tribunal Superior do Trabalho"),
        ("STM", "Superior Tribunal Militar"),
    ]:
        lista.append({"sigla": sigla, "nome": nome, "justica": "superior"})

    for uf in _UFS:
        sigla = "TJDFT" if uf == "DF" else "TJ" + uf
        nome = "Tribunal de Justiça do Distrito Federal e dos Territórios" if uf == "DF" else "Tribunal de Justiça (" + uf + ")"
        lista.append({"sigla": sigla, "nome": nome, "justica": "estadual"})

    for uf in ("SP", "MG", "RS"):
        lista.append({"sigla": "TJM" + uf, "nome": "Tribunal de Justiça Militar (" + uf + ")", "justica": "militar_estadual"})

    for n in range(1, 7):
        lista.append({"sigla": "TRF%d" % n, "nome": "Tribunal Regional Federal da %dª Região" % n, "justica": "federal"})

    for n in range(1, 25):
        lista.append({"sigla": "TRT%d" % n, "nome": "Tribunal Regional do Trabalho da %dª Região" % n, "justica": "trabalho"})

    return lista


# Tribunais cujo site recusa a consulta automática (HTTP 403 mesmo com o robô identificado).
# Enquanto estiverem aqui o app avisa o usuário, em vez de fingir que sabe o calendário.
# Para sair da lista: um motor tem de conseguir ler o calendário DE VERDADE a partir do
# GitHub (ver docs/PROCESSO_MOTORES.md). Atualizada com evidência, nunca por palpite.
AVISO_INCOMPATIVEL = (
    "Este tribunal não permite a consulta automática do calendário. "
    "Use o cálculo simplificado ou confira o prazo por conta própria."
)

INCOMPATIVEIS = {
    # sem nenhuma fonte oficial que abra a partir do GitHub (HTTP 403 / tela anti-robô / robots.txt
    # que proíbe / conexão derrubada / tempo esgotado), testado em 2026-10-23 e 24
    "TJES": "site e diário recusam o robô (403/robots.txt)",
    "TJPB": "site e diário recusam o robô (403/robots.txt)",
    "TJPI": "site recusa o robô; diário e transparência em tempo esgotado",
    "TJRN": "site e diário recusam o robô (403/robots.txt)",
    "TJAP": "site recusa o robô (403/robots.txt)",
    "TJAM": "tempo esgotado em todas as fontes testadas",
    "TJMS": "tempo esgotado em todas as fontes testadas",
    "TJRJ": "erro de certificado SSL nas fontes oficiais (não desligamos a verificação)",
    "TJRS": "tempo esgotado e 403 em todas as fontes testadas",
    "TJRO": "o servidor de atos derruba a conexão do robô",
    "TJPA": "o ato do calendário é PDF escaneado (só imagem); sem OCR não há leitura confiável",
    "TJMSP": "site e robots.txt dão 403",
    "TST": "site e calendário respondem com tela anti-robô, sem conteúdo",
    "STM": "o PDF do calendário não abre (devolve HTML de 247 bytes); categoria do dia só por cor",
    "TRT1": "site e diário recusam o robô (403/robots.txt)",
    "TRT4": "site e diário recusam o robô (403/robots.txt)",
    "TRT5": "site e diário recusam o robô (403/robots.txt)",
    "TRT6": "tempo esgotado, até no robots.txt",
    "TRT7": "endereços do calendário dão 404/403",
    "TRT8": "site e diário recusam o robô (403/robots.txt)",
    "TRT10": "site e diário recusam o robô (403/robots.txt)",
    "TRT14": "os PDFs do calendário dão 403",
    "TRT16": "PDFs e listas do calendário dão 403",
    "TRT17": "site e diário recusam o robô (403/robots.txt)",
    "TRT20": "site e diário recusam o robô (403/robots.txt)",
    "TRT21": "site e diário recusam o robô (403/robots.txt)",
    "TRT22": "site e diário recusam o robô (403/robots.txt)",
    "TRT23": "site responde 400; nenhuma fonte alternativa achada",
}
