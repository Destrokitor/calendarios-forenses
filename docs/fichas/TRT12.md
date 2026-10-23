# Ficha do tribunal: TRT12

- **Nome:** Tribunal Regional do Trabalho da 12ª Região (Santa Catarina)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis; recesso 20/12 a 20/01 (RI art. 153).
- **Fonte(s) oficial(is):** www.trt12.jus.br dá tempo esgotado e portal.trt12.jus.br é negado (robots.txt). Fonte que abre: repositório DSpace do TRT12 com a Portaria SEAP nº 191/2024 (republicação de 19/05/2025, publicada no DEJT, alterada pela Portaria SEAP 57/2025): https://dspace.trt12.jus.br/server/api/core/bitstreams/b401ad4a-b944-43f7-86e5-b0245fbde6b9/content (PDF).
- **Fixture(s) guardada(s):** tests/fixtures/trt12/portaria_calendario_feriados_2026.pdf (+ .txt via pdftotext -layout)
- **Como o calendário é publicado:** portaria com Anexo I (nacionais, estaduais, regimentais) e Anexo II (municipais), tabelas MÊS | DIA | MOTIVO.
- **Locais:** Anexo II lista ~60 municípios/datas ("Fundação da Cidade de Joinville" etc.), sem coluna de comarca: o nome do município está dentro do MOTIVO (extrair por regex "Cidade de X", "Município de X", "Padroeira/o ... de X").
- **Particularidades:** art. 2º transfere 11/08->10/08, 28/10->30/10, 08/12->07/12. Mês com linha de data quebrada em duas (ex. XANXERÊ 27/02, 06/03 e 09/03 aparecem embaralhados na extração). Corpus Christi 04/06 é feriado em todos os municípios-sede. DUVIDA: a portaria foi alterada depois (SEAP 25/2026 acrescenta 20/04 e 05/06 como feriado regimental/ponto facultativo, segundo a página de portarias de 2026 do portal, que é bloqueada ao robô) => esta fonte sozinha fica DEFASADA.
- **Âncoras conferidas à mão:**
  1. 2026-01-01 a 2026-01-06 recesso, Art. 153 RI (Anexo I, regimentais)
  2. 2026-02-16 a 2026-02-18 Carnaval/Cinzas, Art. 154 RI
  3. 2026-04-01 a 2026-04-05 Semana Santa
  4. 2026-08-10 (transferido de 11/08) e 2026-08-16 Data Magna de SC (estadual, transferido do dia 11)
  5. 2026-03-19 Fundação da Cidade de Joinville (Anexo II, municipal)
- **Pode rodar na nuvem?** SIM para esta portaria. Provas literais (run 39986792087): `OK 200 266558 application/pdf;charset=UTF-8 2.0 https://dspace.trt12.jus.br/server/api/core/bitstreams/b401ad4a-b944-43f7-86e5-b0245fbde6b9/content`. Negados: `ROBOTS-NEGA https://portal.trt12.jus.br/sites/default/files/2026-02/calendario-2026.pdf`, `ROBOTS-NEGA https://portal.trt12.jus.br/calendario-de-2026`, `ERRO URLError <urlopen error timed out> https://www.trt12.jus.br` (run 39985764294), `ERRO 404 https://dspace.trt12.jus.br/entities/publication/de12695f-...` (run 39986982105).
- **Cobertura:** parcial (falta a alteração SEAP 25/2026 e demais de 2026, só no portal bloqueado; possível achar no DSpace, não localizado).
- **Categoria:** parcial
