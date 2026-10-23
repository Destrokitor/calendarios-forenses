# Ficha do tribunal: TST

- **Nome:** Tribunal Superior do Trabalho
- **Justiça / regime(s) de contagem:** Trabalho, superior (CLT art. 775 e 775-A; CPC subsidiário). Calendário conjunto TST/CSJT.
- **Categoria:** `incompativel`
- **Fonte(s) oficial(is) encontradas e o que a nuvem fez:**
  - Página https://www.tst.jus.br/calendarios-do-tst (links dos calendários) e PDF "Calendário 2026" (versão atual de 22/10/2026, com Atos Conjunto TST.CSJT.GP 61/2025 e 5/2026, GDGSET.GP 829/2025, SEGJUD.GP 18/2026, 285/2026, 481/2026 e 575/2026): https://www.tst.jus.br/documents/d/guest/calendario_22-10-2026-pdf . O nome do arquivo muda a cada alteração (v5, v7, calendario_22-10-2026...), então o motor teria de achar o link na página, que a nuvem não lê.
  - Feriados do TST em formato iCalendar (Google Agenda pública, 118 eventos, tem Carnaval, Semana Santa, pontos facultativos etc.): https://calendar.google.com/calendar/ical/tst.jus.br_d1avm8dm0te0ig02j876d7ebas%40group.calendar.google.com/public/basic.ics . O robô respeita robots.txt e o do Google nega (ROBOTS-NEGA).
  - Ato Conjunto TST.CSJT.GP 5/2026 (PDF no JusLaboris): abre na nuvem, mas é PDF ESCANEADO (o texto embutido sai com erros de OCR: "Io", "O1O"), exige OCR, e é de 29/1/2026, anterior a 4 atos posteriores. Serve só como evidência, não como fonte do motor.
- **Fixture(s) guardada(s):** tests/fixtures/tst/ (calendario_oficial_2026_v22-10-2026.pdf, calendarios_do_tst_pagina.html, feriados_tst.ics). Baixadas no meu computador (a nuvem não consegue).
- **Formato:** PDF vetorial com texto para feriados/pontos facultativos (lista "dd de mês, feriado (fundamento)"); RECESSO e FÉRIAS COLETIVAS só aparecem como COR nas células do calendário (roxo = recesso, bege = férias coletivas dos ministros), sem texto de data. ICS: texto limpo, mas sem recesso/férias.
- **Locais:** nenhum (Brasília). 
- **Particularidades:**
  - Pelo desenho do PDF (conferi a imagem): recesso forense 1 a 6/1 e 20 a 31/12; férias coletivas dos ministros 7 a 31/1 e 2 a 31/7. Não há texto que confirme; coincide com a regra legal (Lei 5.010/66 art. 62, I; LC 35/79 art. 66).
  - Corpus Christi (4/6): PDF diz "ponto facultativo (Corpus Christi)"; o ICS diz "Feriado de Corpus Christi" (4 e 5/6). # DUVIDA: qual vale.
  - PDF diz "1º a 5 de abril, feriado" (Semana Santa); 20/4, 5/6, 10/8, 7/12 e 30/10 são pontos facultativos; 18/2 "até 14h".
  - O calendário foi alterado por 6 atos desde outubro/2025: o motor teria de acompanhar as versões.
- **Âncoras conferidas à mão** (no PDF v22-10-2026, só para o dia caso um dia se ache fonte legível pela nuvem):
  1. 2026-02-16 e 17, Carnaval, feriado (art. 62, III, Lei 5.010/1966): lista "Feriados e Pontos Facultativos".
  2. 2026-04-01 a 05, Semana Santa, feriado (art. 62, II, Lei 5.010/1966): idem.
  3. 2026-04-20, ponto facultativo; 2026-04-21, Tiradentes feriado: idem.
  4. 2026-10-30, ponto facultativo "em razão da transferência do ponto facultativo do dia 28 de outubro": idem.
  5. 2026-12-20 a 31, recesso forense (roxo na grade de dezembro) e 2026-07-02 a 31 férias coletivas (bege na grade de julho): só pela cor.
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 202 0 text/html; charset=UTF-8 0.2 https://www.tst.jus.br/calendarios-do-tst
OK 202 0 text/html; charset=UTF-8 0.0 https://www.tst.jus.br/documents/d/guest/calendario_22-10-2026-pdf
ROBOTS-NEGA https://calendar.google.com/calendar/ical/tst.jus.br_d1avm8dm0te0ig02j876d7ebas%40group.calendar.google.com/public/basic.ics
```
```
gh run 39986812345 (testar-urls, conclusão: success)
OK 200 1911998 application/pdf 3.3 https://juslaboris.tst.jus.br/bitstream/handle/20.500.12178/259927/2026_atc0005_tst_csjt.pdf?sequence=1&isAllowed=y
OK 202 0 text/html; charset=UTF-8 0.2 https://www.tst.jus.br/documents/d/guest/calendario-oficial-a4-2026-v7-pdf
OK 202 0 text/html; charset=UTF-8 0.0 https://www.tst.jus.br/
OK 202 0 text/html; charset=UTF-8 0.2 https://www.csjt.jus.br/
OK 202 0 text/html; charset=UTF-8 0.0 https://www.tst.jus.br/robots.txt
```
  (Resposta HTTP 202 com 0 byte em tst.jus.br e csjt.jus.br: página de desafio anti-robô, sem conteúdo. NÃO foi tentado contornar.)
- **Pode rodar na nuvem?** Não. Fontes boas: 202 vazio / ROBOTS-NEGA. Fonte que abre (juslaboris): escaneada e defasada.
- **Cobertura:** nenhuma pela nuvem. Se o TST liberar a nuvem, a leitura seria parcial (feriados em texto; recesso/férias só pela cor ou por regra legal fixa).
