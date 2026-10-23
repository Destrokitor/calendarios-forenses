# Ficha do tribunal: TRF5

- **Nome:** Tribunal Regional Federal da 5ª Região (PE, AL, CE, PB, RN, SE)
- **Justiça / regime(s) de contagem:** Federal; dias úteis; Lei 5.010/66.
- **Classificação: `parcial`.** Falta: feriados das seções/subseções (cada seção publica portaria própria, em formatos diferentes; CE e RN não localizados; PE abre no meu computador mas deu tempo esgotado na nuvem).
- **Fonte(s) oficial(is):**
  - Ato da Presidência 219/2026 (reedita e substitui o Ato 626/2025; art. 5º traz prorrogação de prazos): https://www4.trf5.jus.br/comunicacao-social/anexo/114878 (PDF, texto). Ato 626/2025 original: .../anexo/114014.
  - Página-espelho: https://www.trf5.jus.br/index.php/feriados (HTML, mesma lista do Ato).
  - Art. 7º do Ato: diretores de foro das seções e das subseções editam ato com feriados e pontos facultativos dos municípios sede de vara. Achados: PE (JFPE) Portaria 126/2026 https://jfpe.jus.br/media/templates/site/cassiopeia_jfpepaginaprincipal_secundarias_jfpe/docs_pdf/biblioteca/portarias/Portaria_126_2026.pdf + páginas https://www.jfpe.jus.br/index.php/feriados.html e ...?view=article&id=217%3Aferiadossubsecoes&catid=274 (HTML por subseção: Arcoverde, Cabo, Caruaru, Garanhuns, Goiana, Jaboatão, Ouricuri, Palmares, Petrolina, Salgueiro, Serra Talhada); PB: https://sistemas.jfpb.jus.br/media/diario_feriados_2026.pdf (Portaria DF 1/2026, tabela nacional/estadual e municipal); SE: https://www.jfse.jus.br/feriados.html (índice de portarias DF 65/2025 e 44/2026); AL: https://www.jfal.jus.br/noticias/6685/ (Portaria 199/2025). CE e RN: não achei.
- **Fixture(s) guardada(s):** tests/fixtures/trf5/ (ato_219_2026..., ato_626_2025..., feriados_2026.html, jfpe_*, jfpb_portaria_dforo_1_2026.pdf, jfse_feriados.html, jfal_noticia_portaria_199_2025.html).
- **Como o calendário é publicado:** Ato: PDF com texto, tabela mês a mês (pdftotext -layout ok). Seções: heterogêneo (HTML, PDF do diário, notícia + PDF).
- **Locais:** o Ato do TRF vale para o TRF (sede Recife; traz Data Magna PE 06/03, São João 24/06 e N.S. do Carmo 16/07 por lei municipal do Recife). Subseções: ver acima.
- **Particularidades:** pontos facultativos (art. 2º): 18/02, 04/06 Corpus Christi, 23/06 véspera de São João, 28/10. Semana Santa 01-05/04 (inclui fim de semana). Recesso 01-06/01 e 20-31/12 (não até 06/01/2027). 13/02 e 31/12: teletrabalho (art. 4º; não é suspensão). Art. 5º: prazos que caírem em feriado/ponto facultativo prorrogam; carnaval -> 19/02. DUVIDA: a notícia do TRF5 cita Carnaval 16-18/02 e São João 23-24; o Ato diz feriado 16-17, ponto facultativo 18/02 e 23/06.
- **Âncoras conferidas à mão (Ato 219/2026):**
  1. 2026-02-16 e 17: Carnaval (art. 1º); 18/02 ponto facultativo (art. 2º).
  2. 2026-03-06: Data Magna do Estado de Pernambuco (art. 1º).
  3. 2026-04-01 a 05: Semana Santa.
  4. 2026-06-24: São João (feriado, lei municipal do Recife); 23/06 ponto facultativo; 04/06 Corpus Christi ponto facultativo.
  5. 2026-12-20 a 31: recesso forense. Extra: 16/07 N.S. do Carmo (Recife).
- **Pode rodar na nuvem?** PARCIAL. testar-urls run 39990187408 (GitHub, 23/10/2026), literal:
```
OK 200 48064 text/html; charset=utf-8 2.1 https://www.trf5.jus.br/index.php/feriados
OK 200 51200 application/pdf 1.9 https://www4.trf5.jus.br/comunicacao-social/anexo/114878
OK 200 46080 application/pdf 1.2 https://www4.trf5.jus.br/comunicacao-social/anexo/114014
ROBOTS-INDISPONIVEL robots.txt de https://www.jfpe.jus.br indisponível (<urlopen error timed out>):  https://www.jfpe.jus.br/index.php/feriados.html
ROBOTS-INDISPONIVEL robots.txt de https://www.jfpe.jus.br indisponível (<urlopen error timed out>):  ...feriados.html?view=article&id=217%3Aferiadossubsecoes&catid=274
ROBOTS-INDISPONIVEL robots.txt de https://jfpe.jus.br indisponível (<urlopen error timed out>): ...Portaria_126_2026.pdf
OK 200 144766 application/pdf 2.2 https://sistemas.jfpb.jus.br/media/diario_feriados_2026.pdf
OK 200 34834 text/html; charset=utf-8 2.3 https://www.jfse.jus.br/feriados.html
OK 200 32054 text/html; charset=utf-8 2.2 https://www.jfal.jus.br/noticias/6685/
```
  Retentativa JFPE (run 39991735459): de novo ROBOTS-INDISPONIVEL (timeout) em jfpe.jus.br. 
- **Cobertura:** parcial: Ato do TRF5 (geral) completo e lido na nuvem; PB lido; SE/AL só índice/notícia (portaria em PDF não baixada); PE (maior seção) fora da nuvem; CE/RN sem fonte achada.
