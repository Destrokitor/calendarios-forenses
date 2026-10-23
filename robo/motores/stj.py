"""Motor do STJ (Superior Tribunal de Justiça). Ver docs/fichas/STJ.md.

Fonte (ver ficha):

  Tabela HTML "Feriados, Pontos Facultativos e Recesso" da página "Horários de Funcionamento"
  do STJ (https://www.stj.jus.br/sites/portalp/Contato-e-ajuda/Fale-conosco/Horarios-de-funcionamento).
  Uma linha por feriado, ponto facultativo ou recesso: Feriados | Datas | Fundamento Legal.
  As datas não trazem ano; o ano vem da frase "para o ano de AAAA" do próprio texto da página.

  Comprovação (não lida pelo motor): comunicado de 16/04/2026 que confirma 20 e 21/04.
  A portaria (Portaria STJ/GP 1010/2025) não foi lida: a página é a fonte dos dias.

Efeito dos dias (decisão da ficha):
  - feriado, Semana Santa e Dia da Justiça: sem_expediente;
  - ponto facultativo: sem_expediente (o STJ trata assim, ver comunicado de 16/04/2026);
  - Quarta-feira de Cinzas (até 14h): parcial;
  - recesso forense: recesso (art. 2º da Emenda Regimental 16/2014), com o trecho de janeiro
    do mesmo recesso no início do ano.

O STJ é uma jurisdição só: tudo vai em `geral`. `locais` tem uma chave única, "BRASÍLIA", com
lista vazia, para o app ter o que listar.

Não entra aqui (ver `parcial`): suspensão de prazo do CPC art. 220 e férias, que a página não
publica; e dias avulsos que só saem em comunicado de notícia.
"""
from __future__ import annotations

import datetime
import html
import re
from typing import Any, Dict, List, Tuple

from ..modelo import calendario_vazio, dia, normalizar_local, ordenar
from ..rede import Cliente, ErroDeFonte
from .base import AindaNaoPublicado, Motor

URL_PAGINA = ("https://www.stj.jus.br/sites/portalp/Contato-e-ajuda/Fale-conosco/"
              "Horarios-de-funcionamento")
URL_COMUNICADO = ("https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2026/"
                  "16042026-Tribunal-nao-tera-expediente-nos-dias-20-e-21-de-abril.aspx")
LOCAL_UNICO = "BRASÍLIA"

_LINHA = re.compile(r"<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>", re.S)
_TABELA = re.compile(r"<table[^>]*>\s*<thead>.*?Feriados.*?</thead>\s*<tbody>(.*?)</tbody>\s*</table>", re.S)
_ANO_TEXTO = re.compile(r"para o ano de (\d{4})")

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Linhas em que o NOME da tabela não bate com a data (a ficha aponta). Para elas o motivo sai do
# fundamento legal, e não do nome: "Independência do Brasil" em 7/12 é o rótulo errado.
ROTULO_NAO_CONFIAVEL = {(12, 7)}
# DUVIDA: "Dia do Servidor Público, 28 de outubro" está como feriado na tabela; notícia secundária
# (Migalhas) fala em ponto facultativo em 30/10. Fica 28/10 (o que a fonte oficial traz); 30/10 NÃO entra.
# DUVIDA: "Corpus Christi, 4 e 5 de junho" está como ponto facultativo: vira sem_expediente, como a ficha manda.


def _texto(celula: str) -> str:
    """Tira as tags e as entidades HTML, e junta os espaços."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", celula)).split())


def _datas(expressao: str, ano: int) -> Tuple[List[datetime.date], str]:
    """Expande a coluna Datas em datas do `ano` (e o horário, se a linha trouxer "(até 14h)").

    Formas vistas na tabela:
      "1º de janeiro"                      -> um dia
      "16 e 17 de fevereiro"               -> dois dias
      "1º a 3 de abril"                    -> intervalo no mesmo mês
      "20 de dezembro a 6 de janeiro"      -> intervalo que cruza o ano (só o trecho do `ano` entra)
      "18 de fevereiro (até 14h)"          -> um dia com horário limite
    """
    horario = ""
    m_hora = re.search(r"\(até\s*(\d{1,2})h\)", expressao)
    if m_hora:
        horario = "até as %sh" % m_hora.group(1)
        expressao = re.sub(r"\s*\(até\s*\d{1,2}h\)", "", expressao)
    expressao = expressao.replace("º", "").strip()

    m_cruza = re.match(r"(\d{1,2}) de (\w+) a (\d{1,2}) de (\w+)$", expressao)
    if m_cruza:
        d1, mes1, d2, mes2 = int(m_cruza.group(1)), MESES[m_cruza.group(2)], int(m_cruza.group(3)), MESES[m_cruza.group(4)]
        ini = datetime.date(ano, mes1, d1)
        fim = datetime.date(ano + 1 if mes2 < mes1 else ano, mes2, d2)
        # o trecho do ano (ex.: 20/12 a 31/12 de 2026) e o trecho de janeiro do mesmo recesso (1 a 6/1 de 2026)
        datas = []
        atual = ini
        while atual <= fim:
            if atual.year == ano:
                datas.append(atual)
            atual += datetime.timedelta(days=1)
        if mes2 < mes1:
            datas_jan = [datetime.date(ano, mes2, n) for n in range(1, d2 + 1)]
            datas = sorted(set(datas) | set(datas_jan))
        return datas, horario

    m_mes = re.search(r"(\w+)$", expressao)
    if not m_mes or m_mes.group(1) not in MESES:
        raise ErroDeFonte("data sem mês reconhecível na tabela do STJ: %r" % expressao)
    mes = MESES[m_mes.group(1)]
    dias_txt = expressao[: m_mes.start()].replace(" de", "").strip()
    m_intervalo = re.match(r"(\d{1,2}) a (\d{1,2})$", dias_txt)
    if m_intervalo:
        numeros = list(range(int(m_intervalo.group(1)), int(m_intervalo.group(2)) + 1))
    else:
        numeros = [int(n) for n in re.findall(r"\d{1,2}", dias_txt)]
    if not numeros:
        raise ErroDeFonte("dia sem número na tabela do STJ: %r" % expressao)
    return [datetime.date(ano, mes, n) for n in numeros], horario


def _tipo_e_motivo(rotulo: str, fundamento: str, data: datetime.date) -> Tuple[str, str]:
    """(tipo, motivo) de uma linha da tabela. Nunca inventa suspensão de prazo."""
    if "recesso" in rotulo.lower():
        return "recesso", "Recesso forense"
    if fundamento.lower().startswith("ponto facultativo"):
        # DUVIDA: ponto facultativo vira sem_expediente (decisão da ficha; comunicado de 16/04/2026).
        if (data.month, data.day) in ROTULO_NAO_CONFIAVEL:
            return "sem_expediente", "Ponto facultativo"
        if rotulo.lower() == "ponto facultativo":
            return "sem_expediente", "Ponto facultativo"
        return "sem_expediente", "%s (ponto facultativo)" % rotulo
    return "sem_expediente", rotulo


def baixar(rede: Cliente) -> bytes:
    """Rede: a página de horários. Única chamada de rede do motor."""
    return rede.baixar(URL_PAGINA)


def interpretar(conteudo: bytes, ano: int) -> Dict[str, Any]:
    """Do HTML da página para o calendário. Puro: sem rede, para os testes usarem a fixture."""
    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = conteudo.decode("iso-8859-1")

    # Cada janeiro a frase de abertura muda de ano: se não cita o ano pedido, a página é de outro ano.
    frase = _ANO_TEXTO.search(_texto(texto))
    if not frase:
        raise ErroDeFonte("frase 'para o ano de AAAA' não encontrada na página do STJ")
    if int(frase.group(1)) != ano:
        raise AindaNaoPublicado("a página do STJ ainda é de %s, não de %d" % (frase.group(1), ano))

    tabela = _TABELA.search(texto)
    if not tabela:
        raise ErroDeFonte("tabela de feriados não encontrada na página do STJ")

    cal = calendario_vazio("STJ", ano)
    cal["fontes"] = [
        {"id": "tabela", "url": URL_PAGINA,
         "descricao": "Tabela 'Feriados, Pontos Facultativos e Recesso' da página Horários de Funcionamento do STJ (Portaria STJ/GP 1010/2025)"},
        {"id": "comunicado", "url": URL_COMUNICADO,
         "descricao": "Comunicado do STJ de 16/04/2026 (não expediente em 20 e 21/04/2026); comprovação"},
    ]
    cal["locais"] = {normalizar_local(LOCAL_UNICO): []}

    linhas = _LINHA.findall(tabela.group(1))
    if not linhas:
        raise ErroDeFonte("tabela do STJ sem linhas de dia")

    for celula_rotulo, celula_datas, celula_fund in linhas:
        rotulo = _texto(celula_rotulo)
        datas_txt = _texto(celula_datas)
        fundamento = _texto(celula_fund)
        if not rotulo or not datas_txt:
            raise ErroDeFonte("linha incompleta na tabela do STJ: %r" % ((rotulo, datas_txt),))
        datas, horario = _datas(datas_txt, ano)
        for data in datas:
            if horario:
                # Quarta-feira de Cinzas "até 14h": o expediente encerra cedo, então é parcial
                cal["geral"].append(dia(data, "parcial", "%s (ponto facultativo)" % rotulo, "tabela", horario))
                continue
            tipo, motivo = _tipo_e_motivo(rotulo, fundamento, data)
            cal["geral"].append(dia(data, tipo, motivo, "tabela"))

    return ordenar(cal)


class MotorSTJ(Motor):
    sigla = "STJ"
    precisa_ip_brasil = False  # testado do GitHub: página e PDF do ato abrem (200), ver docs/fichas/STJ.md
    parcial = (
        "Fora: (1) suspensão de prazo do CPC art. 220 (20/12 a 20/1) e férias de julho: a página "
        "não publica; o calendário traz só feriados, pontos facultativos e recesso, e o app não "
        "pode usar este arquivo para suspender prazo. (2) Dias avulsos só divulgados em comunicado "
        "de notícia: só entram os que já estão na tabela (20 e 21/04 de 2026). (3) A Portaria STJ/GP "
        "1010/2025 não foi lida (o PDF do BDJur não foi conferido). (4) Não há locais: o STJ é uma "
        "jurisdição só. (5) O trecho de 1 a 6/01 do recesso de dezembro está em `geral` por causa da "
        "regra do recesso (ficha, âncora 5), não por linha própria da tabela."
    )
    esperado = {
        # 40 dias lidos da fixture de 2026 (inclui 1 a 6/01 do recesso e 20 a 31/12); piso abaixo disso.
        "min_geral": 35,
        "min_locais": 1,
        # Conferidas à mão na ficha (tabela da página e comunicado de 16/04/2026).
        "ancoras": {
            "2026-01-06": "Recesso forense (trecho de janeiro)",
            "2026-02-16": "Carnaval",
            "2026-02-17": "Carnaval",
            "2026-04-01": "Semana Santa",
            "2026-04-03": "Semana Santa",
            "2026-04-20": "Ponto facultativo",
            "2026-04-21": "Tiradentes",
            "2026-08-11": "Criação dos Cursos Jurídicos",
            "2026-12-08": "Dia da Justiça",
            "2026-12-20": "Recesso forense",
        },
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        return interpretar(baixar(rede), ano)


MOTOR = MotorSTJ()
