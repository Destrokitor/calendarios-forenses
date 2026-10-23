# Ficha do tribunal: TJMT

- **Nome:** Tribunal de Justiça do Estado de Mato Grosso
- **Justiça / regime(s) de contagem:** estadual comum; CPC. Art. 2º: em feriado nacional, estadual, municipal e ponto facultativo ficam suspensos o expediente e os prazos; §1º: feriado municipal só vale na respectiva comarca.
- **Fonte(s) oficial(is):**
  - Portaria TJMT/PRES nº 1915, de 05/12/2025 (DJe 09/12/2025; a cópia diz "este texto não substitui o publicado no DJe"), 8 páginas, Anexo I (calendário geral) e Anexo II (feriados por comarca): https://cms.tjmt.jus.br/Download.aspx?arquivo=%2Fintranet.arq%2Fcms%2Fgrupopaginas%2F100%2F820%2FPortaria_1915-2025-PRES_-_Calend%C3%A1rio_Forense_2026.pdf
  - Índice vivo, com todas as alterações e suspensões do ano: https://www.tjmt.jus.br/paginas/transparencia-e-prestacao-contas?url=%2FInstitucional%2FC%2F82478 ("Calendário Judiciário 2026", atualizada até 01/10/2026). Lista: Portaria 1254/2026 (altera o Anexo I: Dia do Servidor, 28/10 → 30/10), 245/2026, 509/2026 (suspensão a partir das 13h de 06/04, falta de água), 752/2026 (horário especial em jogos da Copa), 901/2026 (suspende 29/06), suspensões de 21 a 25/09/2026 e retomadas (1370 e 1384/2026), cada uma com PDF.
  - NÃO usar: o espelho wiki.tjmt.jus.br (robots.txt nega e o site está "em manutenção"), nem a AASP ("não divulgado": errada).
- **Fixture(s) guardada(s):** tests/fixtures/tjmt/portaria_1915_2025_pres_calendario_forense_2026.pdf, calendario_judiciario_2026_pagina.html (índice com os links das alterações)
- **Como o calendário é publicado:** PDF com texto. Anexo I = tabela "MÊS | DIA | FERIADO" com texto livre e a natureza entre parênteses ("(feriado nacional)", "(ponto facultativo)"). Anexo II = bloco por comarca numerado (46 blocos achados na extração), com linhas "DD/MM (dia da semana) | motivo" (ex.: "ÁGUA BOA | 09/07(quinta-feira) Aniversário do Município; 12/10 N. S. Aparecida (Padroeira)"). O layout é irregular (nomes de comarca em duas linhas, "(" e ")" desencontrados, um erro de impressão em Aripuanã "31/10 (sexta-feira  31/12 (quarta-feira))").
- **Locais (comarcas/foros/municípios):** lista única em PDF no Anexo II, cerca de 46+ comarcas conferidas na extração (conferir a contagem total na Etapa 2). Os nomes são os oficiais em maiúsculas com acento. Feriado em fim de semana também consta (ex.: 24/05 domingo).
- **Particularidades:** Anexo I mistura "feriado nacional" e "ponto facultativo"; o art. 2º manda suspender prazos em ambos. 18/02 "Cinzas (expediente a partir das 13h)" = DIA PARCIAL (Portaria 338/2023). Dia do Advogado 10 e 11/08 e Dia da Justiça 07 e 08/12 como ponto facultativo/feriado. Anexo I NÃO tem o recesso de 20/12 a 20/01 (CPC art. 220); 24/12 e 31/12 constam como ponto facultativo. 15/11/2026 cai em domingo. A Portaria 1254/2026 altera o Anexo I (28/10 → 30/10): o motor tem de aplicar as portarias do índice, senão erra o Dia do Servidor.
- **Âncoras conferidas à mão** (Anexos I e II):
  1. 2026-02-18, Cinzas, expediente a partir das 13h (Anexo I; dia parcial).
  2. 2026-04-20, Tiradentes, ponto facultativo (Anexo I); 2026-04-21 feriado nacional.
  3. 2026-12-07 e 12-08, Dia da Justiça (Anexo I, DL 8.292/1945).
  4. Água Boa: 09/07 Aniversário do Município e 12/10 N. S. Aparecida (Anexo II, bloco 1).
  5. Cáceres: 25/08 São Luiz de Cáceres (Padroeiro) e 06/10 Aniversário do Município (Anexo II, bloco 13).
- **Pode rodar na nuvem?** SIM. Saída literal (execução `testar-urls` nº 39986641769, 23/10/2026):
  `OK 200 401360 application/pdf 6.4 https://cms.tjmt.jus.br/Download.aspx?arquivo=%2Fintranet.arq%2Fcms%2Fgrupopaginas%2F100%2F820%2FPortaria_1915-2025-PRES_-_Calend%C3%A1rio_Forense_2026.pdf`
  `OK 200 228772 text/html;charset=UTF-8 7.3 https://www.tjmt.jus.br/paginas/transparencia-e-prestacao-contas?url=%2FInstitucional%2FC%2F82478`
  (Na execução nº 39986386976 o espelho wiki.tjmt.jus.br deu `ROBOTS-NEGA`: não usar.)
- **Cobertura:** completa para o calendário base e os feriados municipais. Categoria: **pronto_para_motor**. Ressalva: ler também o índice (HTML) para pegar as alterações e suspensões extras (Portaria 1254/2026 muda o Dia do Servidor; as outras são suspensões pontuais em PDFs soltos: ler os links só se o motor quiser cobri-las).
