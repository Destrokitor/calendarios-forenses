# Ficha do tribunal: TRT3

- **Nome:** Tribunal Regional do Trabalho da 3ª Região (Minas Gerais)
- **Justiça / regime(s) de contagem:** Trabalhista. Dias úteis (CLT art. 775); art. 775-A. O calendário institucional lança "Recesso" 01-06/01 e 20-31/12 (Lei 5.010/66 art. 62 I); NÃO lança suspensão 07-20/01.
- **Categoria:** **pronto_para_motor** (com a ressalva das suspensões avulsas, abaixo)
- **Fonte(s) oficial(is):**
  1. Feriados LOCAIS 2026 (HTML, tabela por mês; já com alterações posteriores): https://portal.trt3.jus.br/internet/institucional/calendario/feriados-locais-1/feriados-locais-2026 . Ato: Portaria TRT3/SEGP 991, de 3/11/2025 (art. 1º: "Não haverá expediente ... nas datas dos respectivos feriados locais informados no Anexo Único"). O Anexo Único oficial é PDF (ver abaixo, ilegível); a tabela HTML da página é o texto lido.
  2. Feriados NACIONAIS/estaduais/recesso 2026 (HTML, resumo + tabela por mês): https://portal.trt3.jus.br/internet/institucional/calendario/calendario-2026 (reproduz a Resolução Administrativa 109, de 12/08/2025). O ato original é PDF com texto no repositório `sistemas.trt3.jus.br/bd-trt3`, mas esse host tem `robots.txt` com `Disallow: /` (o nosso robô respeita): usar a página HTML.
  3. Calendário de parede 2026 (PDF com texto, extraível): https://portal.trt3.jus.br/internet/institucional/calendario/downloads/calendario-de-parede-web.pdf (confirmação).
  4. Suspensões avulsas (ex.: jogos da Copa): só notícia + "texto da portaria" (https://portal.trt3.jus.br/internet/conheca-o-trt/comunicacao/noticias-institucionais/trt-define-expediente-para-dias-com-jogos-do-brasil). Não há lista estruturada de suspensões de prazo.
- **Fixture(s) guardada(s):** `tests/fixtures/trt3/feriados-locais-2026.html`, `calendario-2026.html`, `calendario-parede-2026.pdf`, `ra-109-2025-calendario-2026.pdf` (+ `.txt` extraído com pdftotext), `portaria-segp-991-2025.pdf`, `noticia-jogos-brasil-copa.html`.
- **Formato:** HTML com tabelas (locais: 11 tabelas `Data | Localidade | Motivo`, uma por mês, sem fevereiro; calendário-2026: bloco "Feriados da Justiça do Trabalho de Minas Gerais" com tabela `Dias do mês | Dia da semana | Motivo`). PDF da Portaria 991 e o Anexo Único: texto não extraível (Anexo: 14 páginas, fontes Type 3 sem unicode, pdftotext devolve lixo; sem OCR não dá). NÃO usar o Anexo PDF; usar o HTML.
- **Como saem feriados locais e suspensões:**
  - Locais: tabela HTML da página "Feriados Locais 2026": 274 linhas de dados, 66 localidades distintas (Belo Horizonte, Contagem, Uberlândia, ...). A coluna Data é só o DIA do mês; o mês vem do cabeçalho "<Mês> / 2026" da tabela. Motivo traz a lei municipal. Registra também "Suspensão do expediente (RA 109/2025)" em 05/06 por município que tem Corpus Christi (154 linhas só em junho).
  - Localidades que não aparecem na tabela não têm feriado local. RA 109 III: "Os Órgãos desta Justiça observarão ... os feriados locais ... informados pelo gestor da unidade à Secretaria-Geral da Presidência": a lista pode mudar ao longo do ano (a página já cita a "Portaria TRT/SEMA/001/2026" alterando Almenara).
  - Suspensões de prazo avulsas: não estão na agenda; saem em portaria/notícia. Ex.: Copa do Mundo (portaria da Presidência: fecha 1h antes do jogo quando começa entre 14h e 19h; prazos com início/fim em dia de jogo com início até 17h são prorrogados). Sem número da portaria na notícia; não há lista no site. O motor NÃO cobre isso (parcial nesse ponto).
- **Locais (comarcas/foros/municípios):** 66 localidades (nome do município, em caixa mista, p. ex. "Belo Horizonte"). Normalizar com `normalizar_local`.
- **Particularidades / DUVIDA:**
  - 18/02 Quarta de Cinzas: RA 109 diz "Suspensão de expediente em todos os órgãos". DUVIDA: dia inteiro? O texto não fala em horário.
  - 20/04: "Suspensão de expediente ... em decorrência do feriado de Tiradentes no dia subsequente". 05/06: "Suspensão do expediente em decorrência de Corpus Christi" só onde há feriado municipal em 04/06 e comunicação prévia à Secretaria-Geral (condicionada). O 05/06 NÃO vale para o tribunal inteiro: Belo Horizonte, Contagem, Uberlândia etc. constam na tabela de locais; os demais só se comunicaram. NÃO lançar 05/06 como geral.
  - Corpus Christi 04/06: "feriado com regulamentação municipal" (calendário-2026); a RA 109 NÃO o lista como feriado geral. Tratar como LOCAL (só nas localidades da tabela). DUVIDA para o revisor: o TRT3 não declara 04/06 como feriado em todo o estado.
  - 14/08 (Dia dos Cursos Jurídicos, movido de 11 para 14) e 30/10 (Dia do Servidor, movido de 28 para 30): "alterado por interesse da Administração".
  - Feriados que caem em fim de semana (01/11, 15/11) constam: sem efeito prático.
  - Dia da Justiça 08/12 geral. Recesso 01-06/01 e 20-31/12.
- **Âncoras conferidas à mão** (23/10/2026):
  1. **2026-02-16 e 02-17** Carnaval; **02-18** "Cinzas / Suspensão de expediente em todos os órgãos" (RA 109/2025; HTML calendario-2026 e `ra-109-...txt`).
  2. **2026-04-20** "Suspensão de expediente ... em decorrência do feriado de Tiradentes no dia subsequente" e **2026-04-21** Tiradentes (RA 109 item I).
  3. **2026-08-14** "Dia da Criação dos Cursos Jurídicos, Dia do Magistrado e Dia do Advogado ... Feriado alterado do dia 11 para o dia 14 de agosto" (RA 109, Art. 62 IV Lei 5.010/66) e **2026-10-30** Dia do Servidor Público ("alterado do dia 28 para o dia 30 de outubro").
  4. Local: **2026-01-15 Unaí** "Aniversário da Cidade – Dia do Município (Lei n. 2760/2011)"; **2026-03-27 Contagem** "Jubileu de Nossa Senhora da Dores (Lei n. 3484/2001) – Feriado Móvel"; **2026-06-04 Belo Horizonte** "Corpus Christi (Lei n. 1327/1967)" e **2026-06-05 Belo Horizonte** "Suspensão do expediente (RA 109/2025)" (`feriados-locais-2026.html`).
  5. **Recesso 2026-01-01 a 01-06 e 12-20 a 12-31** ("Recesso: de 1º a 6 de janeiro e de 20 a 31 de dezembro", RA 109 item I) e **2026-12-08** Dia da Justiça.
- **Pode rodar na nuvem?** PARCIAL. Run https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986611463 e https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986961133 (ambos `success`), saída literal:
  ```
  OK 200 233071 text/html;charset=utf-8 1.6 https://portal.trt3.jus.br/internet/institucional/calendario/feriados-locais-1/feriados-locais-2026
  ROBOTS-NEGA https://sistemas.trt3.jus.br/bd-trt3/bitstream/handle/11103/92641/RA%20TRT3_SETPOE%20109_2025%20ORIG.pdf
  OK 200 178802 application/pdf 0.9 https://portal.trt3.jus.br/internet/institucional/calendario/feriados-locais-1/anexo-unico-portaria-trt3-segp-991-2025-de-3-de-novembro-de-2025-1.pdf
  OK 200 179264 text/html;charset=utf-8 1.5 https://portal.trt3.jus.br/internet/institucional/calendario/calendario-2026
  OK 200 792983 application/pdf 1.0 https://portal.trt3.jus.br/internet/institucional/calendario/downloads/calendario-de-parede-web.pdf
  OK 200 232558 text/html;charset=utf-8 1.4 https://portal.trt3.jus.br/internet/conheca-o-trt/comunicacao/noticias-institucionais/trt-define-expediente-para-dias-com-jogos-do-brasil
  ```
  (O Anexo Único PDF abre, mas é ilegível; o repositório da RA 109 é barrado por robots.txt.)
- **Cobertura:** completa para feriados nacionais/estaduais, recesso e feriados locais publicados; parcial só para suspensões avulsas de prazo (Copa etc.), que não saem em lista estruturada.
