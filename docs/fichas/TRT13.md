# Ficha do tribunal: TRT13

- **Nome:** Tribunal Regional do Trabalho da 13ª Região (Paraíba)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT art. 775); recesso 20/12 a 20/01.
- **Fonte(s) oficial(is):** o site principal (www.trt13.jus.br) NÃO abre na nuvem (robots.txt nega ao robô). A fonte alternativa que abre é o repositório de normas internas do próprio TRT13 (DSpace), host diferente:
  - Ato TRT13.SGP nº 181, de 30/10/2025 (calendário oficial 2026, com anexo): https://normasinternas.trt13.jus.br/xmlui/bitstream/handle/bdtrt7/129054/ATO%20TRT13%20SGP%20N.%c2%ba%20181-2025.pdf?sequence=2&isAllowed=y (PDF, texto extraível)
  - Versão consolidada do Ato 181 (HTML): .../bdtrt7/129054/ATO%20TRT13%20SGP%20N.%c2%ba%20181_2026%20-%20CONSOLIDADO%20-%20REVOGADO%20PARCIALMENTE.html?sequence=4&isAllowed=y
  - Ato TRT13.SGP nº 39, de 18/03/2026 (pontos facultativos 20/04, 05/06, 07/12; alterado pelos Atos 75/2026 e 76/2026), consolidado em HTML: .../bdtrt7/129941/ATO%20TRT13.SGP%20N.%c2%ba%2039%2c%20DE%2018%20DE%20MAR%c3%87O%20DE%202026%20CONSOLIDADO.html?sequence=6&isAllowed=y
  - Como achar: busca `https://normasinternas.trt13.jus.br/xmlui/discover?query=calend%C3%A1rio+2026+feriados` (abre na nuvem) lista os atos; cada `handle/bdtrt7/<n>` traz os links `bitstream`.
- **Fixture(s) guardada(s):** tests/fixtures/trt13/ato_181_2025_calendario_2026.pdf (+ .txt via pdftotext -layout), ato_181_consolidado.html, ato_39_2026_consolidado.html
- **Como o calendário é publicado:** anexo em tabela (colunas DATA | EVENTO | LOCALIDADE | DIA DA SEMANA | OCORRÊNCIA | LEGISLAÇÃO). OCORRÊNCIA distingue "Feriado Nacional", "Feriado Legal e Regimental" (recesso), "Feriado Municipal" e "Ponto Facultativo".
- **Locais (comarcas/foros/municípios):** feriados municipais NO MESMO anexo, coluna LOCALIDADE (ex.: Itaporanga, Guarabira, Santa Rita, Catolé do Rocha...). Paraíba = localidade do tribunal inteiro.
- **Particularidades:** Ato 181 transfere 11/08 para 10/08 e 28/10 para 30/10. Atos de 2026 (39, 75, 76) alteram pontos facultativos e transferências (o consolidado menciona 23/06 em vez de 10/08; DUVIDA: ordem/vigência das alterações 75/76 de 2026 é confusa no HTML, revisor deve decidir). Ponto facultativo (18/02 cinzas, 04/06 Corpus Christi, 20/04, 05/06, 07/12): Ato 181 art. 4º par. único prorroga prazos para o 1º dia útil; Ato 39 diz "suspensão de expediente" => DUVIDA: feriado x prorrogação de prazo.
- **Âncoras conferidas à mão** (no texto do Ato 181 e anexo):
  1. 2026-01-01 Confraternização Universal (Feriado Nacional) — 1ª linha do anexo
  2. 2026-01-02 a 2026-01-06 Recesso (Feriado Legal e Regimental) — 2ª linha do anexo
  3. 2026-01-09 Emancipação Política, Itaporanga (Feriado Municipal, Lei 497/1999) — 3ª linha do anexo
  4. 2026-02-16 e 2026-02-17 Carnaval (Feriado Nacional); 2026-02-18 Quarta-feira de cinzas (Ponto Facultativo)
  5. 2026-04-21 Tiradentes (Feriado Nacional); 2026-04-01 a 2026-04-03 Semana Santa
- **Pode rodar na nuvem?** SIM (fonte normasinternas.trt13.jus.br). Provas literais (workflow testar-urls):
  - run 39988388199 (rodou 3 primeiras): `OK 200 34425 text/html;charset=utf-8 1.1 https://normasinternas.trt13.jus.br/xmlui/handle/bdtrt7/130260`; `OK 200 67259 text/html;charset=utf-8 2.5 .../xmlui/discover?query=calend%C3%A1rio+2026+feriados`
  - run 39988804073: `OK 200 34681 text/html;charset=utf-8 1.2 .../handle/bdtrt7/129054`; `OK 200 91666 application/pdf 0.8 .../ATO%20TRT13%20SGP%20N.%c2%ba%20181-2025.pdf?sequence=2&isAllowed=y`; `OK 200 119026 text/html; charset=UTF-8 0.9 ...CONSOLIDADO%20-%20REVOGADO%20PARCIALMENTE.html?sequence=4&isAllowed=y`; `OK 200 125072 text/html; charset=UTF-8 0.8 ...ATO%20TRT13.SGP...CONSOLIDADO.html?sequence=6&isAllowed=y`
  - Site principal (sonda e runs 39985764294/39986982105): `ROBOTS-NEGA https://www.trt13.jus.br`, `ROBOTS-NEGA https://trt13.jus.br/acesso-a-informacao/calendario-2026`, `ROBOTS-NEGA https://www.trt13.jus.br/acesso-a-informacao/arquivos/calendario-2026__.pdf`
- **Cobertura:** completa para feriados/recesso/locais do anexo do Ato 181; alterações de 2026 (Atos 39/75/76) em HTML consolidado precisam de leitura à parte.
- **Categoria:** pronto_para_motor (com ressalva das alterações de 2026)
