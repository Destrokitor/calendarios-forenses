# Ficha do tribunal: TRF2

- **Nome:** Tribunal Regional Federal da 2ª Região (RJ e ES)
- **Justiça / regime(s) de contagem:** Federal; dias úteis; Lei 5.010/66 art. 62.
- **Classificação: `pronto_para_motor`** (com ressalvas abaixo).
- **Fonte(s) oficial(is):**
  1. Tabela HTML "Calendário de feriados no Estado do Rio de Janeiro" (feriados locais E suspensões avulsas, com link do ato): https://www.trf2.jus.br/trf2/atendimento/prazos-suspensos-feriados?field_data_ano_limite2_value=2026&field_nacional_ou_estadual_value=2 (filtro por ano e abrangência; colunas: data, feriado/suspensão, abrangência = município/subseção, ato).
  2. Portaria PRES/TRF2 844/2025 (SJRJ, 2026): https://www.trf2.jus.br/sites/default/publico/motivo-ato/2025-12/SEI_1420331_Portaria_PRES_844.pdf (PDF com texto; art. 1º geral, art. 2º feriados municipais por subseção, 17 subseções).
  3. Portaria PRES/TRF2 845/2025 (SJES) alterada pela Portaria 32/2026: .../2025-12/PORTARIA%20PRES-TRF2%20N%C2%BA%20845_0.pdf e .../2026-04/portaria-trf2-atualizada-feriados-2026_portaria-32_2026.pdf; índice em https://www.trf2.jus.br/jfes/aviso/2026/consulte-as-portarias-de-suspensao-de-expediente-na-jfes-em-2026
  4. Avulsas: Port. 338/2026 (ponto facultativo 29/06 nas 3 portarias), Port. 78/2026 (13/02), 17/2026, 13/2026, 125/2026, 476/2026 (links na tabela 1).
- **Fixture(s) guardada(s):** tests/fixtures/trf2/ (prazos_suspensos_feriados_rj_2026.html, portaria_pres_844_..., 845_..., 32_..., 338_..., 78_..., jfes_aviso_portarias_2026.html).
- **Como o calendário é publicado:** HTML (tabela) + PDFs com texto (pdftotext -layout funciona). Sem OCR.
- **Locais:** RJ: 17 subseções (Angra dos Reis, Barra do Piraí, Campos, Itaboraí, Itaperuna, Macaé, Magé, Niterói, Petrópolis, Resende, Rio de Janeiro, São Gonçalo, São João de Meriti, São Pedro d'Aldeia, Teresópolis, Três Rios, Volta Redonda). ES: seção inteira (Port. 845/32; não conferi se há feriados municipais no ES, a 845 tem 6,8 mil caracteres de texto).
- **Particularidades / DUVIDA:**
  - As portarias 844/845 põem PONTOS FACULTATIVOS (18/02, 04/06, 28/10 no RJ; 20/04, 05/06, 10/08, 07/12 no ES) na lista "Não haverá expediente". Art. 5º: efeito sobre prazos "estabelecido pela legislação". Decisão de tipo (sem_expediente x parcial/suspensão) para o revisor. 18/02 é "Cinzas - ponto facultativo" sem horário na 844.
  - 13/02/2026: a tabela mostra "Suspensão do expediente - Rio de Janeiro" (Port. 17), mas a Port. 78 põe as DEMAIS subseções em regime remoto (não é suspensão). Cuidado com escopo.
  - Recesso: RJ 1-6/jan e 20/12-06/01 ("feriado" art. 62 I, plantão). A tabela HTML não lista os nacionais; vêm dos PDFs.
  - Tabela da página cobre RJ; ES tem página própria (JFES) só com os PDFs.
- **Âncoras conferidas à mão:**
  1. 2026-02-16 e 17: Carnaval, sem expediente (Port. 844 art. 1º II).
  2. 2026-04-23: São Jorge, estadual RJ (844 art. 1º VI).
  3. 2026-06-24: São João, municipal em Itaboraí, Macaé, Niterói, São João de Meriti (844 art. 2º IV/VI/VIII/XIII; confirmado na tabela HTML).
  4. 2026-04-13: Nossa Sra. da Penha, padroeira do ES (Port. 32, art. 1º V da 845).
  5. 2026-06-29: ponto facultativo (Port. 338/2026); Petrópolis também tem Dia do Colono e São Pedro d'Aldeia São Pedro nessa data (844).
- **Pode rodar na nuvem?** SIM. testar-urls run 39990142303 (GitHub, 23/10/2026), literal:
```
OK 200 78611 text/html; charset=UTF-8 2.2 https://www.trf2.jus.br/trf2/atendimento/prazos-suspensos-feriados?field_data_ano_limite2_value=2026&field_nacional_ou_estadual_value=2
OK 200 62426 application/pdf 0.8 https://www.trf2.jus.br/sites/default/publico/motivo-ato/2025-12/SEI_1420331_Portaria_PRES_844.pdf
OK 200 53209 application/pdf 0.7 https://www.trf2.jus.br/sites/default/publico/2026-04/portaria-trf2-atualizada-feriados-2026_portaria-32_2026.pdf
OK 200 39214 text/html; charset=UTF-8 1.0 https://www.trf2.jus.br/jfes/aviso/2026/consulte-as-portarias-de-suspensao-de-expediente-na-jfes-em-2026
OK 200 189134 application/pdf 3.5 https://www.trf2.jus.br/sites/default/publico/2025-12/PORTARIA%20PRES-TRF2%20N%C2%BA%20845_0.pdf
```
- **Cobertura:** completa para RJ (geral + 17 subseções + suspensões da tabela); ES só geral (verificar municipais na 845).
