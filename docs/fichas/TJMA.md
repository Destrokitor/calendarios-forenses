# Ficha do tribunal: TJMA

- **Nome:** Tribunal de Justiça do Estado do Maranhão
- **Justiça / regime(s) de contagem:** estadual comum; CPC.
- **Fonte(s) oficial(is):**
  - Resolução-GP nº 131, de 04/11/2025 (Órgão Especial, 36ª sessão administrativa de 29/10/2025; DJe 06/11/2025): "Relaciona os dias em que não haverá expediente ... no ano de 2026". URL: https://novogerenciador.tjma.jus.br/storage/arquivos/resolucoes_2025/resolucao_gp_n_131_de_4_de_novembro_de_2025_05_11_2025_17_12_45.pdf (2 páginas, PDF com texto, incisos numerados I a XVII com data e motivo).
  - Notícia oficial (lista de datas): https://www.tjma.jus.br/midia/portal/noticia/519639/tjma-divulga-os-feriados-forenses-de-2026
  - HÁ ALTERAÇÃO: Resolução-GP nº 26, de 07/04/2026, que gerou uma "versão consolidada" (ficheiro `..._consolidada_08_04_2026_17_28_55.pdf` na mesma pasta, apareceu em busca). Esse link dá 404 (no meu computador e no WebFetch). O que a Res. 26/2026 mudou NÃO foi conferido: DUVIDA/lacuna importante para o motor.
- **Fixture(s) guardada(s):** tests/fixtures/tjma/resolucao_gp_131_2025.pdf, noticia_feriados_2026.html
- **Como o calendário é publicado:** PDF com texto, prosa em incisos ("II – 16 de fevereiro (segunda-feira) - Carnaval - Feriado Forense (...)"). Fácil de ler com regex.
- **Locais (comarcas/foros/municípios):**
  - Art. 1º parágrafo único: só o Termo Judiciário de São Luís (Comarca da Ilha de São Luís) tem 2 feriados municipais nomeados: 29/06 São Pedro e 08/09 Fundação da Cidade.
  - Art. 2º: "também não haverá expediente nas comarcas do interior nos feriados definidos em lei municipal", SEM lista. Não há anexo com os municípios. Logo, feriados do interior = fonte externa (lei de cada município).
- **Particularidades:** Art. 3º pontos facultativos: 18/02 (Cinzas), 01/04 (quarta da Semana Santa), 05/06 (sexta após Corpus Christi); art. 4º: pontos facultativos do Executivo não vinculam o Judiciário. "Feriado Forense" (Lei Complementar 14/1991, art. 5º-A §1º): carnaval, 02-03/04, 11/08, 08/12. Não há recesso de fim de ano no ato (20/12 a 20/01 do CPC não consta). Efeito do ponto facultativo: o art. 1º lista só os dias sem expediente; o art. 3º diz "pontos facultativos" sem dizer o efeito sobre o prazo: DUVIDA.
- **Âncoras conferidas à mão** (Resolução-GP 131/2025, art. 1º):
  1. 2026-01-01, Dia da Confraternização Universal (inciso I).
  2. 2026-07-28, Adesão do Maranhão à Independência do Brasil (inciso IX), data estadual.
  3. 2026-06-29, São Pedro, feriado municipal só no Termo Judiciário de São Luís (parágrafo único).
  4. 2026-09-08, Fundação da Cidade de São Luís, feriado municipal só em São Luís (parágrafo único).
  5. 2026-06-05, ponto facultativo (art. 3º, III). Também: 2026-08-11 Dia do Advogado, feriado forense (inciso X).
- **Pode rodar na nuvem?** SIM. Saída literal (execução `testar-urls` nº 39986386976, 23/10/2026):
  `OK 200 10656 application/pdf 3.0 https://novogerenciador.tjma.jus.br/storage/arquivos/resolucoes_2025/resolucao_gp_n_131_de_4_de_novembro_de_2025_05_11_2025_17_12_45.pdf`
- **Cobertura:** parcial. Categoria: **parcial**. Geral legível; interior sem lista municipal; alteração de 07/04/2026 não lida (precisa achar a Res.-GP 26/2026 ou a consolidada).
