# Ficha do tribunal: TRT18

- **Nome:** Tribunal Regional do Trabalho da 18ª Região (Goiás)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT 775), suspensão 20/12 a 20/01 (o próprio calendário cita "art. 220 do CPC").
- **Fonte(s) oficial(is):**
  - Calendário anual 2026 (PDF com texto, publicado em 08/01/2026): `https://www.trt18.jus.br/portal/arquivos/2026/01/Calendario-2026_Insta.pdf` (página que o lista: `https://www.trt18.jus.br/portal/informe-se/calendario-anual/`, atualizada em 02/02/2026).
  - Suspensões de expediente: Portaria nº 2329/2025 (citada pelo calendário e pela notícia `https://www.trt18.jus.br/portal/planeje-se-para-2026-com-o-calendario-do-trt-go-publicacao-tambem-traz-dicas-de-linguagem-simples/`). O texto da portaria NÃO foi localizado.
  - A página "calendário anual" só tem a "Lista de feriados locais" de 2023 e 2024 (PDFs); NÃO existe lista de feriados locais de 2026 separada (o PDF do calendário a substitui).
- **Fixture(s):** `tests/fixtures/trt18/calendario_2026.pdf`, `calendario_anual.html`, `noticia_calendario_2026.html`.
- **Como é publicado:** PDF de arte (12 meses, grade Dom a Sáb, 2,5 MB) COM camada de texto. Cada dia traz o texto do rótulo (ex. "Carnaval", "Suspensão de expediente", "Semana Santa", "Padroeiro São Sebastião (Goiatuba, Rio Verde e Palmeiras de Goiás)", "Aniversário de Goiatuba"). A legenda (feriado estadual/nacional/recesso, feriado municipal, suspensão de expediente, prazos suspensos 20/12 a 20/1) é por COR; o texto sozinho não distingue sempre o tipo. Ler exige `pdftotext -bbox` e atribuir cada rótulo à coluna/linha da grade (fragil; rótulos se espalham em várias linhas, e dias de outro mês aparecem nas pontas das semanas).
- **Locais:** municípios goianos com Vara/Posto Avançado, citados no rótulo entre parênteses ou em "Aniversário de X". Sem lista fechada de locais.
- **Particularidades:**
  - Suspensões (Portaria 2329/2025, segundo a notícia): 18/02, 20/04, 05/06, 10/08 e 07/12 (dias úteis entre feriado e fim de semana); prazos que caírem nelas prorrogam para o dia útil seguinte (CPC 216 e 219). Carnaval: 16, 17 e 18/02 (esta última, suspensão).
  - "Suspensão de prazos" em 07 a 20/01 (e 20/12 em diante). Em 20/01 coincide com feriado municipal. Distinguir de feriado.
  - Feriado local atípico: "Feriado Goianésia (falecimento do ex-governador ...)" em 15/07.
  - Rodapé da grade: 24/05 (Domingo) Nossa Senhora Auxiliadora (Goiânia e Iporá) cai em domingo, sem efeito.
- **Âncoras conferidas à mão (PDF `calendario_2026.pdf`, texto na grade):**
  1. 2026-02-16 e 17: "Carnaval"; 2026-02-18: "Suspensão de expediente".
  2. 2026-01-20 (terça): "Suspensão de prazos / Padroeiro São Sebastião (Goiatuba, Rio Verde e Palmeiras de Goiás)"; 21/01 Aniversário de Goiatuba; 22/01 Aniversário de Quirinópolis.
  3. 2026-06-04 "Corpus Christi" e 2026-06-05 "Suspensão de Expediente".
  4. 2026-08-10 (segunda) "Suspensão de Expediente" e 2026-08-11 "Dia do Magistrado e do Advogado".
  5. 2026-07-15 (quarta) "Feriado Goianésia (falecimento do ex-governador Otávio Lage de Siqueira)".
  (20/04 e 07/12 constam da notícia/portaria 2329/2025; não conferi o rótulo na grade.)
- **Pode rodar na nuvem?** SIM (PDF e páginas). Run 39986139412 (GitHub Actions, 23/10/2026), literal:
  ```
  OK 200 2537318 application/pdf 2.8 https://www.trt18.jus.br/portal/arquivos/2026/01/Calendario-2026_Insta.pdf
  OK 200 183133 text/html; charset=UTF-8 1.2 https://www.trt18.jus.br/portal/informe-se/calendario-anual/
  ```
- **Cobertura:** parcial, por causa do formato (tipo do dia depende de cor/legenda) e de a Portaria 2329/2025 não ter sido achada (nem o ato dos feriados locais). Dá para ler dias e rótulos, mas classificar feriado x suspensão exige regras por texto do rótulo.
- **Categoria: `parcial`** (fonte abre na nuvem; PDF gráfico com rótulos em texto; sem ato normativo textual dos locais; atribuir tipo por palavras do rótulo).
