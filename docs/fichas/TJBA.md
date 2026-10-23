# Ficha do tribunal: TJBA

- **Nome:** Tribunal de Justiça do Estado da Bahia
- **Justiça / regime(s) de contagem:** estadual comum; CPC. O decreto manda prorrogar prazo que vencer em dia sem expediente para o primeiro dia útil (art. 8º).
- **Fonte(s) oficial(is):**
  - Calendário geral: Decreto Judiciário nº 1050, de 04/12/2025 (DJe nº 3.944, 05/12/2025, p. 6-8). Texto corrido, art. 5º em lista de incisos com datas. Cópia em PDF no portal: https://www.tjba.jus.br/portal/wp-content/uploads/2025/12/Decreto-1050-25_-expediente-forense-2026.pdf (é a página inteira do DJe: o decreto começa na p. 6 depois de um edital de concurso; 2 outros decretos vêm em seguida). Notícia oficial: https://www.tjba.jus.br/portal/decreto-judiciario-estabelece-o-expediente-forense-e-administrativo-do-tjba-para-2026/
  - Feriados MUNICIPAIS: Decreto Judiciário nº 09, de 07/01/2026 ("disponibiliza a relação dos feriados municipais nas Comarcas"), com anexo por comarca; alterado por decretos como o nº 48/2026 e o nº 144/2026 (que só mexe em Sapeaçu: 27 de abril). Índice: https://www.tjba.jus.br/portal/feriados-municipais/ (lista os decretos; os de 2026 estão no sistema www7.tjba.jus.br).
- **Fixture(s) guardada(s):** tests/fixtures/tjba/decreto_1050_2025_expediente_forense_2026.pdf, decreto_1050_2025_noticia.html, feriados_municipais_pagina.html (índice dos decretos), dje_adm_3985_decreto_144_2026.pdf (exemplo de decreto que altera o anexo municipal). NÃO consegui guardar o Decreto 09/2026 (anexo com as comarcas): o www7 devolve 503.
- **Como o calendário é publicado:** geral = PDF do DJe com texto (lista de incisos: "II - 12, 13, 16, 17 e 18 de fevereiro: Carnaval e Quarta-feira de Cinzas"). Locais = anexo de decreto em PDF no www7 (não lido) + decretos de alteração soltos (um por mudança) no portal.
- **Locais (comarcas/foros/municípios):** pela imprensa (não conferi no anexo), o anexo cobre 193 comarcas. Cada alteração vem em decreto próprio ("Altera o anexo do Decreto nº 09"), com tabela "COMARCA | FERIADOS MUNICIPAIS" (ex.: "SAPEAÇU | 27 de abril."). Art. 10 do Decreto 1050: outros feriados/pontos municipais só valem com determinação expressa do Presidente.
- **Particularidades:**
  - Art. 5º lista "feriados ou pontos facultativos" juntos (sem distinguir); o efeito é o mesmo no texto: "não haverá expediente forense e administrativo". Art. 6º: horas repostas (compensação) em 12/02, 13/02, 02/04, 20/04, 05/06, 22/06, 23/06, 03/07, 10/08, 07/12.
  - Recesso: 20/12/2025 a 06/01/2026 (art. 2º, prazos suspensos); 07 a 20/01/2026: prazos suspensos, expediente normal (art. 4º), com exceções penais (art. 798-A CPP).
  - Dias parciais: nenhum no decreto.
  - 30/10: Dia do Servidor transferido do 28.
- **Âncoras conferidas à mão** (Decreto Judiciário 1050/2025, art. 5º, DJe p. 8):
  1. 2026-02-12, 13, 16, 17 e 18, Carnaval e Quarta-feira de Cinzas (inciso II).
  2. 2026-04-02 e 03, Endoenças e Sexta-feira Santa (inciso III).
  3. 2026-06-22, 23 e 24, São João (inciso VII).
  4. 2026-07-02 e 03, Independência da Bahia (inciso VIII).
  5. 2026-12-07 e 08, Dia da Justiça (inciso XV). Recesso: 2025-12-20 a 2026-01-06 (art. 2º). Local: Sapeaçu 27/04 (Decreto 144/2026, anexo).
- **Pode rodar na nuvem?** PARCIAL. Saída literal (execuções `testar-urls` nº 39986386976 e nº 39986641769, 23/10/2026):
  `OK 200 172259 text/html; charset=UTF-8 4.5 https://www.tjba.jus.br/portal/decreto-judiciario-estabelece-o-expediente-forense-e-administrativo-do-tjba-para-2026/`
  `OK 200 95856 application/pdf 2.4 https://www.tjba.jus.br/portal/wp-content/uploads/2025/12/Decreto-1050-25_-expediente-forense-2026.pdf`
  `OK 200 177650 text/html; charset=UTF-8 2.1 https://www.tjba.jus.br/portal/feriados-municipais/`
  `OK 200 56667 application/pdf 0.6 https://www.tjba.jus.br/portal/wp-content/uploads/2026/02/DJE-ADM-3985.pmd_.pdf`
  `ERRO 503 https://www7.tjba.jus.br/secao/arquivo/9/41226/DJ%2009.2026%20-%20Texto%20compilado.pdf`  (o anexo municipal; no meu computador também deu 503 em 3 tentativas. O link "lerPublicacao.wsp?...&tmp.id=..." tem `&` e não pode ser testado pelo workflow.)
- **Cobertura:** parcial. Categoria: **parcial**. Geral completo e legível. Falta o anexo municipal do Decreto 09/2026 (www7 em 503 na nuvem e no meu computador; testar de novo mais tarde, ou achar cópia no portal wp-content) e os decretos de alteração (um por comarca/mudança, página índice HTML com links).
