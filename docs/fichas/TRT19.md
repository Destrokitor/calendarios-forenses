# Ficha do tribunal: TRT19

- **Nome:** Tribunal Regional do Trabalho da 19ª Região (Alagoas)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis; recesso 20/12 a 20/01.
- **Fonte(s) oficial(is):** www.trt19.jus.br recusa o robô (robots.txt). Fonte que abre: Boletim Interno (asp1.trt19.jus.br) com o Ato nº 170/GP/TRT 19ª, de 29/09/2025 (também "Disponibilizado no DEJT e no BI nº 10, em 08/10/2025"): https://asp1.trt19.jus.br/docspdf/rhdocs/BOLETIM_20251008092236621.PDF (PDF, 2 páginas, texto extraível).
- **Fixture(s) guardada(s):** tests/fixtures/trt19/ato_170_2025_feriados_2026.pdf (+ .txt via pdftotext -layout)
- **Como o calendário é publicado:** tabela MÊS | DIAS | FERIADOS com faixas ("02 a 06 (sexta a terça-feira)").
- **Locais:** NÃO há lista. Só inclui feriados de Maceió/estaduais (São João 24/06, São Pedro 29/06, Padroeira de Maceió 27/08, Emancipação AL 16/09). Art. 3º: "Varas do Trabalho sediadas no interior ... deverão observar os feriados locais" (sem relação).
- **Particularidades:** Pontos facultativos 20/04, 05/06, 10/08, 07/12 listados como linhas "Ponto Facultativo". Ato 30/10 (transferência do Dia do Servidor). DUVIDA: ponto facultativo x suspensão de prazo (art. 2º remete a CPC 219 e 224 §1º). Atos posteriores de 2026 (ex. 20/04 etc.) não verificados.
- **Âncoras conferidas à mão:**
  1. 2026-01-01 Confraternização universal; 2026-01-02 a 2026-01-06 Recesso Forense
  2. 2026-02-16 e 17 Carnaval, 2026-02-18 Cinzas
  3. 2026-06-24 São João (Lei Estadual 5508/1993)
  4. 2026-08-27 Padroeira de Maceió
  5. 2026-12-20 a 2026-12-31 Recesso Forense
- **Pode rodar na nuvem?** SIM. Prova literal (run 39986792087): `OK 200 148343 application/pdf 2.2 https://asp1.trt19.jus.br/docspdf/rhdocs/BOLETIM_20251008092236621.PDF`. Também `OK 200 563831 application/pdf 2.3 .../BOLETIM_20260306140251317.PDF` e `OK 200 390683 application/pdf 2.6 .../BOLETIM_20260618142102312.PDF` (run 39988767567; são outros atos, sem calendário). Site principal: `ROBOTS-NEGA https://www.trt19.jus.br`.
- **Cobertura:** parcial (sem feriados municipais do interior).
- **Categoria:** parcial

- **Próximo ano (como localizar):** não localizado. O ato é publicado no DEJT/Boletim Interno (asp1.trt19.jus.br/docspdf/rhdocs/BOLETIM_<data-hora>.PDF); o endereço muda a cada edição e não há página índice conhecida. Procurar o "Ato GP ... feriados e pontos facultativos do exercício de <ano>" no Boletim Interno do fim do ano anterior.
- **Motor:** `robo/motores/trt19.py`; testes em `tests/test_trt19.py`. Motor lê só o Ato de 2026; 2027 levanta AindaNaoPublicado.
- **Travou em:** nada.
