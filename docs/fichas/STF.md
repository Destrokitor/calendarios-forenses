# Ficha do tribunal: STF

- **Nome:** Supremo Tribunal Federal
- **Justiça / regime(s) de contagem:** Superior (CPC; processo penal pelo art. 798-A CPP). Recesso e férias coletivas próprios.
- **Categoria:** `pronto_para_motor`
- **Fonte(s) oficial(is):**
  - Página índice (HTML; lista as portarias do ano, com ementa): https://portal.stf.jus.br/textos/verTexto.asp?servico=processoCalendarioStf&pagina=calendarioStf (gestor: Secretaria-Geral da Presidência; última atualização 2026-06-26)
  - Calendário oficial 2026 (PDF com texto, 1 página, versão 12/11/2025): http://www.stf.jus.br/arquivo/cms/processoCalendarioStf/anexo/CalendarioSTFOficial2026.pdf
  - Portaria GDG 189/2025 (feriados e pontos facultativos jan/2026 a set/2027): https://www.stf.jus.br/arquivo/norma/portariadg189-2025.pdf
  - Portaria GDG 124/2026 (prazos suspensos 2 a 31/7/2026): https://www.stf.jus.br/arquivo/norma/portariadg124-2026.pdf
  - Portaria GDG 250/2025 (recesso 20/12/2025 a 6/1/2026; prazos suspensos até 31/1/2026): https://www.stf.jus.br/arquivo/norma/portariadg250-2025.pdf
  - Portarias GDG 112/2026 e 146/2026 (dias avulsos). Padrão de URL do PDF: `https://www.stf.jus.br/arquivo/norma/portariadg<NNN>-<AAAA>.pdf` (confirmado para 189, 124, 250 na nuvem; 146 e 112 só no meu computador). Os links da página índice apontam para `atosnormativos.stf.jus.br/visualizador/<id>`, que é uma página JS (HTML de 2,8 KB, sem o texto): não serve ao motor.
- **Fixture(s) guardada(s):** tests/fixtures/stf/ (calendarios_stf_pagina.html, CalendarioSTFOficial2026.pdf, portaria_gdg_189_2025.pdf, portaria_gdg_124_2026_suspensao_julho.pdf, portaria_gdg_250_2025_recesso.pdf, portaria_gdg_146_2026_copa.pdf, portaria_gdg_112_2026_24jun.pdf). Baixadas em 23/10/2026 dos URLs acima.
- **Formato:** HTML (índice), PDF com texto (`pdftotext -layout` lê limpo). Sem OCR.
- **Como o calendário é publicado:** o PDF do calendário traz lista textual "Nome (fundamento): (dia-da-semana) dd/mm"; a Portaria 189 traz feriados (art. 1º, incisos I a XVIII) e pontos facultativos (art. 1º §1º). Suspensões e horários especiais saem em portarias avulsas, listadas na página índice (ementa em texto) e depois no PDF.
- **Locais (comarcas/foros/municípios):** nenhum. Tribunal único (Brasília). `locais` = {} (ou chave única "BRASÍLIA" se o app exigir).
- **Particularidades:**
  - Feriado x ponto facultativo: o calendário PDF mistura as duas coisas em uma lista; a Portaria 189 separa. Corpus Christi (4/6) é PONTO FACULTATIVO na Portaria (art. 1º §1º III), mas o PDF lista sem rótulo. 
  - O PDF lista também 1/11, 15/11 (domingos) e a Páscoa (5/4): sem efeito em dia útil.
  - Suspensão de prazo (não é feriado): 2 a 31/7/2026 (Portaria 124, art. 1º; parágrafo único prorroga vencimentos para o 1º dia útil seguinte); 20/12/2025 a 31/1/2026 (Portaria 250, art. 4º, vale para jan/2026). As do fim de 2026 (20/12/2026 a 31/1/2027) ainda NÃO foram publicadas (hoje 23/10).
  - Recesso: 20/12/2026 a 6/1/2027 (PDF; art. 78 §1º RISTF). Férias coletivas dos ministros: 2 a 31/1 e 2 a 31/7 (PDF).
  - Dias parciais: 24/6/2026 expediente das 11h às 18h (Portaria 112, só ementa na página); 18/2 "ponto facultativo até as 14 horas" (Quarta-feira de Cinzas: o PDF/Portaria dizem "até as 14 horas"; efeito exato não detalhado).
  - Ponto facultativo extraordinário: 29/6/2026 (jogo da Seleção), com prazos prorrogados para 30/6 (Portaria 146, art. 3º). 
  - # DUVIDA: efeito dos pontos facultativos da Portaria 189 sobre o prazo (20/4, 5/6, 10/8, 30/10, 7/12). Só a Portaria 146 diz expressamente que prorroga prazos; a 189 cita arts. 219 e 224 §1º CPC só para os feriados. Notícia do STF diz que não há expediente no ponto facultativo de 10/8. Quem revisa decide (sugestão: `sem_expediente` com motivo "ponto facultativo").
  - # DUVIDA: "até as 14 horas" em 18/2 = expediente começa às 14h ou termina às 14h? (CPC art. 224 §1º tratado como `parcial`, sem horário).
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2026-02-16 e 2026-02-17, Carnaval (feriado): Portaria 189/2025, art. 1º, II; PDF do calendário, linha "Carnaval (art. 62, III, da Lei 5.010/1966): (seg) 16/02 e (ter) 17-02".
  2. 2026-04-01 a 2026-04-03, Semana Santa (feriado): Portaria 189, art. 1º, III ("1º a 03 de abril de 2026"). O PDF diz "(qua) 01/04 a (dom) 05/04".
  3. 2026-07-02 a 2026-07-31, suspensão de prazos processuais: Portaria GDG 124/2026, art. 1º (tipo `suspensao_prazo`, não feriado).
  4. 2026-12-20 a 2027-01-06, recesso forense: PDF do calendário, "Recesso forense (art. 78, § 1º, RISTF): (dom) 20/12/2026 a (qua) 06/01/2027". Para jan/2026: Portaria 250/2025, art. 1º ("Não haverá expediente no período de 20 de dezembro de 2025 a 06 de janeiro de 2026").
  5. 2026-06-04 Corpus Christi como ponto facultativo: Portaria 189, art. 1º §1º, III. E 2026-06-29: Portaria 146/2026, art. 1º e 3º (ponto facultativo, prazos prorrogados para 30/6).
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 200 156007 text/html 2.8 https://portal.stf.jus.br/textos/verTexto.asp?servico=processoCalendarioStf&pagina=calendarioStf
OK 200 124467 application/pdf 4.2 http://www.stf.jus.br/arquivo/cms/processoCalendarioStf/anexo/CalendarioSTFOficial2026.pdf
OK 200 195126 application/pdf 3.8 https://www.stf.jus.br/arquivo/norma/portariadg189-2025.pdf
OK 200 178005 application/pdf 2.9 https://www.stf.jus.br/arquivo/norma/portariadg124-2026.pdf
OK 200 143688 application/pdf 1.7 https://www.stf.jus.br/arquivo/norma/portariadg250-2025.pdf
```
- **Pode rodar na nuvem?** Sim (HTTP 200, PDFs e HTML).
- **Cobertura:** completa para feriados, pontos facultativos, recesso, férias e suspensões já publicadas. Portarias futuras (suspensão de fim de ano, dias avulsos) aparecem na página índice; o motor deve reler a página a cada rodada.
