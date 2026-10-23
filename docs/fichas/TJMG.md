# Ficha do tribunal: TJMG

- **Nome:** Tribunal de Justiça do Estado de Minas Gerais
- **Justiça / regime(s) de contagem:** Estadual; CPC (dias úteis).
- **Categoria:** `pronto_para_motor`
- **Fonte(s) oficial(is):**
  1. https://www8.tjmg.jus.br/institucional/at/pdf/pc17982026.pdf : Portaria Conjunta 1.798/PR/2026 (13/04/2026), compilada com as alterações 1.814/2026, 1.828/2026 e 1.860/2026 (a última de 24/09/2026). PDF de 1,9 MB.
  2. https://www8.tjmg.jus.br/servicos/gj/calendario/index.jsp : "Guia Judiciário > Feriados Locais" (HTML, formulário por comarca; o art. 6º da portaria o indica como divulgação oficial). A consulta com parâmetros usa `&`, que quebra o workflow `testar-urls`; só a página-base foi provada na nuvem (a consulta por comarca fica sem prova).
  A home e a página de notícias `www.tjmg.jus.br/portal-tjmg/informes/calendario-de-feriados-em-2026-suspensoes-de-expediente.htm` são vetadas por robots.txt (ROBOTS-NEGA): fora.
- **Fixture(s) guardada(s):** `tests/fixtures/tjmg/pc1798_2026.pdf` (+ `.txt` por `pdftotext -layout`, 6313 linhas) e `calendario_index.html`.
- **Como o calendário é publicado:** PDF. Arts. 1º a 3º em texto corrido (lista em algarismos romanos: "I - 1º de janeiro: Confraternização Universal;" ... "XIV - 20 a 31 de dezembro: Feriado Forense;"), art. 2º Belo Horizonte, art. 3º remete ao ANEXO ÚNICO (tabela comarca x feriados municipais).
- **Locais (comarcas):** ~300 comarcas do interior no Anexo (coluna "Comarca" + itens "I - 3 de abril: Paixão de Cristo;"), com nomes de comarca por vezes quebrados em 2 linhas (ex.: "Visconde do Rio / Branco") e itens quebrados em 2 linhas. Belo Horizonte está no art. 2º (4/6 Corpus Christi, 15/8 Assunção; 5/6 sem expediente), não no Anexo.
- **Particularidades:**
  - O PDF contém 4 vezes "ANEXO ÚNICO" (versões sucessivas: a mais nova, Port. 1.860, no início, linha ~197; depois 1.828, 1.814 e a original). O motor deve usar SÓ o primeiro (vigente) e ignorar os históricos.
  - Cabeçalho "Alterada pelas Portarias... 1814, 1828 e 1860": o texto muda durante o ano, e pode surgir nova portaria alterando (o nome do arquivo `pc1798` permanece).
  - Parágrafo único do art. 1º: "Não haverá expediente forense nos dias 20 de abril e 7 de dezembro" (não são feriados): DUVIDA (pontes/emendas: expediente x prazo).
  - Art. 4º: prazos que vencerem nesses dias vão ao primeiro dia útil; parágrafo único: prazos processuais suspensos de 7 a 20/01/2026 (LC 59/2001, art. 313 §8º).
  - 5/6 sem expediente só nas comarcas em que Corpus Christi é feriado municipal.
- **Âncoras conferidas à mão** (PDF pc1798_2026, texto):
  1. 16, 17 e 18/02/2026, Carnaval e Quarta-feira de Cinzas (art. 1º, III).
  2. 30/10/2026, Dia do Funcionário Público (art. 1º, IX).
  3. 20 a 31/12/2026, Feriado Forense/recesso (art. 1º, XIV).
  4. 04/06/2026, Corpus Christi em Belo Horizonte (art. 2º, I).
  5. Anexo, comarca Abaeté: 13/06 "Santo Antônio das Tabocas" e 05/11 "Aniversário da Cidade".
- **Pode rodar na nuvem?** SIM para o PDF e a página-base do Guia (GitHub Actions, 23/10/2026):
```
OK 200 1934204 application/pdf 2.8 https://www8.tjmg.jus.br/institucional/at/pdf/pc17982026.pdf
OK 200 31957 text/html; charset=ISO-8859-1 1.2 https://www8.tjmg.jus.br/servicos/gj/calendario/index.jsp
ROBOTS-NEGA https://www.tjmg.jus.br/portal-tjmg/informes/calendario-de-feriados-em-2026-suspensoes-de-expediente.htm
ROBOTS-NEGA https://www.tjmg.jus.br/
```
  (runs 39986365227 e 39986370049 do testar-urls)
- **Cobertura:** completa (feriados do TJ e municipais de todas as comarcas no Anexo), com a ressalva de que suspensões avulsas (ex.: jogos da Copa, portarias novas) saem em portarias posteriores, não neste PDF.

- **Motor (Etapa 2, 23/10/2026):** `robo/motores/tjmg.py`. Lidos 51 dias gerais, 298 locais (297 comarcas do Anexo + Belo Horizonte), 1.571 dias locais. Só o primeiro ANEXO ÚNICO (Port. 1.860) é lido.
  - DUVIDA: 20/04 e 07/12 (parágrafo único do art. 1º) entraram como `sem_expediente` (o art. 4º prorroga prazos dos dias dos arts. 1º a 3º); revisar se são só pontes sem efeito sobre prazo.
  - 7 a 20/01 entram como `suspensao_prazo` (art. 4º, parágrafo único); 1 a 6/01 e 20 a 31/12 como `recesso`.
  - 5/6 nas comarcas do interior: derivado do art. 3º, § 1º (comarca com "Corpus Christi" em 4/6).
  - Endereço do ano seguinte: o nome do PDF traz o número da portaria (`pc1798` + ano); o de 2027 não foi localizado, então `PORTARIAS` só tem 2026 e 2027 levanta AindaNaoPublicado. Procurar em www8.tjmg.jus.br/institucional/at/pdf/ a "Portaria Conjunta ... consolida o calendário de feriados ... 2027".
