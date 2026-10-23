# Ficha do tribunal: TJCE

- **Nome:** Tribunal de Justiça do Estado do Ceará
- **Justiça / regime(s) de contagem:** estadual comum; CPC (arts. 219 e 224) e CPP art. 798-A.
- **Fonte(s) oficial(is):** Portaria nº 2924/2025 (Presidência; DJE Administrativo, ed. 3690, 17/12/2025), "Fixa os feriados e os pontos facultativos, entre janeiro de 2026 e janeiro de 2027", Anexo Único (tabela). Cópia no portal: https://portal.tjce.jus.br/uploads/2026/04/PORT-FERIADOS-E-PONTO-FACULTATIVO-2026-1776690769.pdf . Alterações: Portaria nº 1169/2026 (ponto facultativo em 05/06/2026), cada uma por portaria própria. Existe também o "Calendário Eletrônico" https://www.tjce.jus.br/calendario/ (a portaria diz que ele não substitui o cadastro de prazos nos sistemas).
- **Fixture(s) guardada(s):** tests/fixtures/tjce/portaria_2924_2025_feriados_2026.pdf (3 páginas, PDF com texto; o anexo é tabela "MÊS/ANO | DIA(S) | JUSTIFICATIVA/NATUREZA" com células quebradas e meses em linhas verticais).
- **Como o calendário é publicado:** PDF com texto (diário oficial), tabela difícil: o mês vem solto numa linha, os dias com "(segunda-feira)" quebrados em duas linhas.
- **Locais (comarcas/foros/municípios):** NENHUMA lista. Art. 2º: feriados/pontos municipais "seguirão legislação própria de cada município" (Portaria 301/2020-Presidência). Ou seja, o tribunal não publica os municipais: Fortaleza (ex.: 15/08) e demais municípios precisariam de fonte externa (lei de cada município).
- **Particularidades:** pontos facultativos misturados com feriados no anexo (carnaval 16 e 17/02, ponto facultativo; 18/02 "ponto facultativo até as 14h", expediente normal único a partir das 14h, exceto custódia a partir das 08h: DIA PARCIAL; 19/03 São José ponto facultativo; Quinta e Sexta-feira Santa 02-03/04 ponto facultativo; Corpus Christi 04/06 ponto facultativo). Recesso natalino 20/12/2025 a 06/01/2026 (remete à portaria 24/2025) e 20/12/2026 a 06/01/2027 (CNJ 244/2016, "ponto facultativo"). Art. 1º §2º: datas que caem em sábado/domingo não constam. Natal (25/12/2026) cai no recesso. Efeito dos "pontos facultativos" sobre o prazo: a portaria diz "datas em que não haverá expediente forense": tratar como sem expediente (DUVIDA a confirmar).
- **Âncoras conferidas à mão** (Anexo Único):
  1. 2026-03-25, Data Magna, feriado estadual (EC estadual 73/2011).
  2. 2026-02-18, Quarta-feira de Cinzas, ponto facultativo até 14h (dia parcial).
  3. 2026-04-21, Tiradentes, feriado nacional.
  4. 2026-12-08, Dia da Justiça, feriado (Lei estadual 12.342/1994 e DL 1408/1951).
  5. 2026-12-20 a 2027-01-06, Recesso natalino, ponto facultativo (CNJ 244/2016).
- **Pode rodar na nuvem?** SIM. Saída literal (execuções `testar-urls` nº 39986386976 e nº 39986641769, 23/10/2026):
  `OK 200 53322 application/pdf 2.0 https://portal.tjce.jus.br/uploads/2026/04/PORT-FERIADOS-E-PONTO-FACULTATIVO-2026-1776690769.pdf`
  `OK 200 2577171 text/html; charset=UTF-8 5.5 https://www.tjce.jus.br/calendario/`
  `OK 200 211960 text/html; charset=UTF-8 2.5 https://www.tjce.jus.br/noticias/tjce-divulga-calendario-de-feriados-e-pontos-facultativos-para-2026/`
- **Cobertura:** parcial para o que importa ao advogado. Categoria: **parcial**. Geral legível e com DIA PARCIAL; sem NENHUM feriado municipal/local (Fortaleza e demais). Alterações vêm em portarias soltas (a de junho foi achada por busca; não há índice).
