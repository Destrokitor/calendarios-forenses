# Ficha do tribunal: TRT24

- **Nome:** Tribunal Regional do Trabalho da 24ª Região (Mato Grosso do Sul)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT 775), recesso forense 20/12 a 06/01 no calendário (art. 62, I Lei 5.010/66).
- **Fonte(s) oficial(is):**
  - Calendário Institucional 2026 (HTML, "Lista de Feriados" do ano inteiro, todas as cidades, com coluna Localidade e Legislação): `https://www.trt24.jus.br/calendario` (equivale a `/web/guest/calendario` e `/web/guest/agendas-e-calendarios`). Seletor de ano 2021 a 2031.
  - Atos de alteração (PDF do DEJT): Portaria TRT/GP/SGJ nº 30/2026 (Mundo Novo, remarcação), `https://www.trt24.jus.br/documents/20182/3304070/Portaria-TRT-GP-SGJ-n-030.2026-Ajusta-feriados-2026-para-atender-Lei-de-Mundo-Novo-DEJT.pdf/ed2c8e02-8d66-dca9-ad37-abbff04ff6c8`
  - Base legal local: PDFs de leis municipais listados na mesma página (Corumbá, Coxim, Dourados...).
  - Resolução Administrativa nº 92/2025 (suspensões), RA 79/2026, 81/2026 e 97/2026 citadas na lista como "Legislação".
- **Fixture(s):** `tests/fixtures/trt24/calendario.html` (página inteira, 94 linhas de 2026), `portaria_030_2026_mundo_novo.pdf`.
- **Como é publicado:** tabela HTML (texto, Liferay/JSF) com colunas `Data | Localidade | Descrição | Legislação`. Localidade = "Nacional", "Estadual", "Tribunal" (vale para o tribunal todo) ou nome do município (22 municípios no seletor: Amambai, Aquidauana, Bataguassu, Campo Grande, Cassilândia, Chapadão do Sul, Corumbá, Coxim, Dourados, Fátima do Sul, Jardim, Maracaju, Mundo Novo, Naviraí, Nova Andradina, Paranaíba, Ponta Porã, Ribas do Rio Pardo, Rio Brilhante, Sidrolândia, São Gabriel do Oeste, Três Lagoas). A página inicial já traz a lista completa de todas as cidades (não precisou do formulário). Mudar de ano exige POST do formulário JSF (token `p_auth`); só o ano corrente testado.
- **Locais:** os 22 acima, nomes sem erro de acento na fonte. Locais sem feriado devem entrar com lista vazia (conferir se há algum: todos os 22 aparecem na lista).
- **Particularidades (separar efeito):**
  - Tipo está só no TEXTO da Descrição: "Suspensão expediente até as 13h" (18/02, parcial), "Expediente das 8h às 15h" (24/06) e "Expediente das 7h às 11h" (29/06) = dias parciais; "Suspensão expediente" (20/04, 05/06, 10/08, 07/12) = sem expediente do tribunal; "Suspensão de prazos processuais" (10 e 11/09, Campo Grande, RA 97/2026) = suspensão de prazo local; "Recesso Forense" (1 a 6/01, 20 a 31/12) = recesso. 7 a 20/01 não são listados (regra 775-A / CPC 220).
  - "Remarcado": Mundo Novo aniversário 11/05 (Portaria 30/2026), Dia do Servidor 30/10 (Portaria 51/2025). Rio Brilhante 26/09 e Maracaju 12/10 vêm sem legislação.
  - Feriado nacional/estadual aparece como linha própria ("Nacional", "Estadual" 11/10 Divisão do Estado, que cai em domingo).
  - Linhas "Domingo de Páscoa" e outras em domingo/sábado: filtrar fim de semana é indiferente.
- **Âncoras conferidas à mão (tabela HTML `calendario.html`):**
  1. 2026-02-02 Corumbá, Padroeiro de Corumbá (Lei 985/1987).
  2. 2026-02-18 Tribunal, "Suspensão expediente até as 13h" (RA 92/2025): parcial; 16 e 17/02 Carnaval (Nacional).
  3. 2026-05-11 Mundo Novo, "Aniversário de Mundo Novo - Remarcado" (Portaria TRT/GP/SGJ nº 30/2026).
  4. 2026-09-10 e 2026-09-11 Campo Grande, "Suspensão de prazos processuais" (RA 97/2026).
  5. 2026-06-24 Tribunal "Expediente das 8h às 15h" (RA 79/2026) e 2026-06-29 "Expediente das 7h às 11h" (RA 81/2026).
- **Pode rodar na nuvem?** SIM. Run 39986139412 (GitHub Actions, 23/10/2026), literal:
  ```
  OK 200 151547 text/html; charset=UTF-8 1.7 https://www.trt24.jus.br/calendario
  OK 200 820540 application/pdf 0.9 https://www.trt24.jus.br/documents/20182/3304070/Portaria-TRT-GP-SGJ-n-030.2026-Ajusta-feriados-2026-para-atender-Lei-de-Mundo-Novo-DEJT.pdf/ed2c8e02-8d66-dca9-ad37-abbff04ff6c8
  ```
  (Obs.: `portal.trt24.jus.br` não resolve; usar `www.trt24.jus.br`.) O PDF da portaria tem texto sobreposto/duplicado (pdftotext confuso): usar só a tabela HTML.
- **Cobertura:** completa (geral + 22 municípios), só ano corrente automaticamente.
- **Categoria: `pronto_para_motor`.** Para o motor: ler a tabela, classificar pelo texto da Descrição, ler o horário do "Expediente das Xh às Yh".
