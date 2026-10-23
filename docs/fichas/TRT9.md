# Ficha do tribunal: TRT9

- **Nome:** Tribunal Regional do Trabalho da 9ª Região (Paraná)
- **Justiça / regime(s) de contagem:** Trabalhista. Dias úteis (CLT art. 775); art. 775-A. O TRT9 lança 01-06/01 como "Recesso Judiciário" (Lei 5.010/66) e 07-20/01 como "Suspensão de prazo - Art. 220 CPC" (Reg. Interno art. 191 §1º), mais 20-31/12 recesso.
- **Categoria:** **pronto_para_motor**
- **Fonte(s) oficial(is):**
  - Principal: https://www.trt9.jus.br/institucional/calendario.xhtml ("Calendário do Judiciário e dos feriados locais"), HTML (JSF/PrimeFaces) com uma TABELA servida no próprio HTML, sem JavaScript, já com o ano corrente (2026). Colunas: `Data Feriado | Descrição | Abrangência | Origem | Legislação`. Abrangência: Nacional / Estadual / Municipal / Órgão Julgador.
  - Atos: https://www.trt9.jus.br/institucional/atoPortaria.xhtml (lista) e cada ato em `atoPortaria.xhtml?id=N` (ex.: Portaria Presidência-Corregedoria 7/2026, id=9039745).
  - O formulário tem filtros "Ano" e "Data" (POST JSF); sem filtro entrega o ano corrente. Em 2027 o ano default muda sozinho; para ler outro ano seria preciso o POST (não testado).
- **Fixture(s) guardada(s):** `tests/fixtures/trt9/calendario-2026.html` (23/10/2026), `portaria-presid-correg-7-2026.html`.
- **Formato:** HTML, tabela `<tr><td>` (143 linhas de dados em 2026: Nacional 46, Municipal 78, Estadual 15, Órgão Julgador 4). Datas em dd/mm/aaaa. Pode haver duas linhas no mesmo dia (ex.: 01/01 Recesso + Confraternização; 25/12 Recesso + Natal).
- **Como saem feriados locais e suspensões:** na MESMA tabela, pela coluna Abrangência:
  - `Municipal`: coluna Origem = "CIDADE-PR" (maiúsculas com UF, p. ex. "PARANAVAI-PR", "JACAREZINHO-PR"), Legislação = decreto/lei municipal. 78 linhas.
  - `Órgão Julgador`: Origem = nome da unidade ("POSTO AVANÇADO DA JUSTIÇA DO TRABALHO DE PALOTINA", "VARA DO TRABALHO DE ASSIS CHATEAUBRIAND"); 4 linhas.
  - Suspensões de prazo avulsas entram como "Estadual": "Suspensão de Prazos - jogo da copa 2026" (29/06, Port. Presid/Correg 7/2026), "Suspensão de prazos processuais no dia 28/08/2026" (Port. 8/2026), 01/09 (Port. 9/2026), 11/09 (Port. 10/2026). A lista cresce durante o ano (esta fixture é de 23/10/2026).
  - "Suspensão de expediente e prazos processuais" (20/04 e 05/06, Port. Presid-Correg 2/2026): explicitamente expediente E prazo.
  - Feriados movidos aparecem como "Transferência do feriado de ..." (14/08, 30/10, 18/12).
- **Locais (comarcas/foros/municípios):** municípios (chave: nome em maiúsculas + "-PR") e unidades (Origem). Não é lista fechada de todas as varas; só quem tem feriado próprio aparece.
- **Particularidades / DUVIDA:**
  - 18/02 "Quarta-Feira de Cinzas" (Nacional, Art. 292 "b" do Reg. Interno): a tabela não diz se é expediente parcial. DUVIDA: não lançar como `sem_expediente` sem revisor. 
  - Semana Santa 01-03/04 marcada "Estadual" (Art. 292 "a" RI); 04/04 sáb e 05/04 dom não constam.
  - Corpus Christi 04/06 marcada "Nacional" (Lei Federal 9.093/1995), única linha do dia: o TRT9 trata como feriado em todo o tribunal (diferente do TRT3, que trata como local). Não há linhas municipais de Corpus Christi.
  - 07-20/01: "Suspensão de prazo - Art. 220 CPC" Nacional (suspensão prevista no RI): é suspensão de prazo, não recesso: tipo `suspensao_prazo`. 21-23/01: suspensão por Portaria 6/2025 (pedido OAB-PR/AATPR).
  - 29/06 (Copa): Portaria Presid-Correg 7/2026 suspende prazos em curso nesse dia e diz que "o dia 29 de junho de 2026 não será computado" (art. 219 CPC); expediente interno encerrou às 12h (Portaria 5/2026, citada). Tipo: `suspensao_prazo` (e expediente parcial); não é feriado.
- **Âncoras conferidas à mão** (tabela e portaria, 23/10/2026):
  1. **2026-01-07 a 01-20** "Suspensão de prazo - Art. 220 CPC", Nacional, "Art. 191, §1º Reg. Interno" (14 linhas) e **2026-01-01 a 01-06** "Recesso Judiciário", Lei 5.010/1966.
  2. **2026-01-21, 22, 23** "Dispõe sobre a suspensão dos prazos processuais de 21 a 23/01/2026", Estadual, "Portaria Presid-Correg 6/2025"; local no meio: **2026-01-22** "Dia do Padroeiro do Município de Palotina", Órgão Julgador, "POSTO AVANÇADO DA JUSTIÇA DO TRABALHO DE PALOTINA", Lei 1.487/1999.
  3. **2026-04-20** e **2026-06-05** "Suspensão de expediente e prazos processuais", Estadual, "Portaria Presid-Correg 2/2026"; **2026-04-21** Tiradentes, **2026-06-04** Corpus Christi.
  4. **2026-06-29** "Suspensão de Prazos - jogo da copa 2026", Port Presid/Correge 7/2026; texto da portaria: "Suspender os prazos processuais em curso no dia 29 de junho de 2026 (segunda-feira). § 1º Os prazos que se iniciarem ou terminarem ... no primeiro dia útil subsequente." (`portaria-presid-correg-7-2026.html`).
  5. **2026-08-14** "Transferência do feriado de 11/8 (Instituição dos Cursos Jurídicos)", **2026-10-30** "Transferência do feriado do Dia do Servidor Público (28/10)", **2026-12-18** "Transferência do feriado de 8/12 (Dia da Justiça)", todos "Portaria Presid-Correg 1/2025"; local: **2026-01-19** "Padroeiro do Município de Paranavaí", Municipal, PARANAVAI-PR, Decreto 27.594/2025.
- **Pode rodar na nuvem?** SIM. Runs https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986611463 , .../39986961133 e .../39987256478 (todos `success`), saída literal:
  ```
  OK 200 444295 text/html;charset=UTF-8 1.6 https://www.trt9.jus.br/institucional/calendario.xhtml
  OK 200 637113 text/html;charset=UTF-8 2.1 https://www.trt9.jus.br/institucional/atoPortaria.xhtml
  OK 200 376960 text/html;charset=UTF-8 1.6 https://www.trt9.jus.br/portal/noticias.xhtml?id=9039777
  OK 200 640763 text/html;charset=UTF-8 3.3 https://www.trt9.jus.br/institucional/atoPortaria.xhtml?id=9039745
  ```
- **Cobertura:** completa (nacionais, estaduais, municipais, unidades, suspensões de prazo e recesso numa só tabela, com a portaria de cada suspensão).
