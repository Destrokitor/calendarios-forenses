# Ficha do tribunal: TJAL

- **Nome:** Tribunal de Justiça do Estado de Alagoas
- **Justiça / regime(s) de contagem:** estadual comum; CPC.
- **Fonte(s) oficial(is):**
  - Ato Normativo nº 03/2026 ("Regulamenta os feriados do ano de 2026", publicado no DJe de 28/01/2026, ed. 3944, p. 6-7). É só um ato de SUSPENSÕES com compensação de horas (20/04, 05/06, 10/08, 28/08 só nos municípios com o feriado, 07/12). O art. 6º diz que "os demais feriados" seguem os Decretos do Estado e dos Municípios e a Lei Estadual 6.564/2005 (Código de Organização Judiciária, arts. 36-38).
  - Ato Normativo nº 22/2025 (ed. 3901 do DJe, 12/11/2025): suspende 02/01/2026.
  - Base citada pelo próprio ato (NÃO é fonte do tribunal): Decreto Estadual nº 106.093/2025 (feriados nacionais e estaduais do Executivo) e Decreto Municipal de Maceió nº 10.234/2025.
  - ATENÇÃO: a AASP aponta "Ato nº 170, de 29/09/2025" como sendo do TJAL, mas o PDF é do TRT19 (Justiça do Trabalho). Não usar.
  - Onde estão os atos (API JSON do portal, sem captcha): https://documentos.tjal.jus.br/api/documentos/detalhes/34801 (Ato 03/2026) e .../34091 (Ato 22/2025). A página da notícia (https://tjal.jus.br/noticia/tribunal-de-justica-de-alagoas-regulamenta-feriados-de-2026/visualizar) é um site em JavaScript: o HTML baixado vem vazio (1,7 KB). O DJe (www2.tjal.jus.br/cdje) devolve página de captcha ao pedir o PDF: inutilizável.
- **Fixture(s) guardada(s):** tests/fixtures/tjal/ato_normativo_03_2026_detalhes.json, ato_normativo_22_2025_detalhes.json (campo `texto` em HTML; há também `anexo` PDF).
- **Como o calendário é publicado:** não há calendário completo do tribunal. Texto corrido (artigos) em JSON/HTML com as suspensões; o resto vem de lei e de decreto de outro poder.
- **Locais (comarcas/foros/municípios):** NENHUMA lista. Feriado municipal = "decretos dos respectivos Municípios" (art. 6º). Só aparece N. Sra. dos Prazeres (27/08, suspensão em 28/08 "apenas nos municípios que preveem o respectivo feriado") sem dizer quais municípios.
- **Particularidades:** suspensão por "compensação": o prazo é suspenso no dia (20/04, 05/06, 10/08, 07/12) mas o servidor repõe horas; tratar como `suspensao_prazo` ("Suspender as atividades, atos e prazos processuais"). 02/01/2026 = fim do recesso forense. Recesso de fim de ano e feriados forenses (Carnaval, Semana Santa, 11/08, 08/12 etc.) estão na Lei 6.564/2005 (arts. 36-38), não no ato: DUVIDA, só lendo a lei. Notícias falam de plantão "22 a 30/06" no recesso junino: não conferido em ato (DUVIDA).
- **Âncoras conferidas à mão** (Ato Normativo 03/2026, `texto`, via JSON):
  1. 2026-04-20, suspensão por Tiradentes (art. 1º; 21/04 seria o feriado).
  2. 2026-06-05, suspensão por Corpus Christi (art. 2º; 04/06 é o feriado).
  3. 2026-08-10, suspensão pelo Dia do Jurista (art. 3º).
  4. 2026-08-28, suspensão por N. Sra. dos Prazeres, só nos municípios que preveem o feriado (art. 4º).
  5. 2026-12-07, suspensão pelo Dia da Justiça (art. 5º).
  (Do Ato 22/2025, art. 1º: 2026-01-02, suspensão por Dia Mundial da Paz e fim do recesso.)
- **Pode rodar na nuvem?** SIM para o JSON e a notícia, mas a notícia só devolve casca de JavaScript. Saída literal (execução `testar-urls` nº 39986386976, 23/10/2026):
  `OK 200 11511 application/json 1.6 https://documentos.tjal.jus.br/api/documentos/detalhes/34801`
  `OK 200 1730 text/html; charset=UTF-8 1.4 https://tjal.jus.br/noticia/tribunal-de-justica-de-alagoas-regulamenta-feriados-de-2026/visualizar`
  (A URL de busca da API, `.../api/documentos/pesquisa-portal?numero=&ano=...`, tem "&" e não pode ser testada pelo workflow atual: o `&` vira comando no shell. Funciona no meu computador.)
- **Cobertura:** parcial. Categoria: **parcial**. Só as 6 suspensões do tribunal estão em fonte oficial legível; falta o calendário nacional/estadual/forense (está em Decreto do Executivo e na Lei 6.564/2005) e todos os feriados municipais. Um motor teria de usar regra fixa para os feriados nacionais e o Decreto estadual como segunda fonte.
