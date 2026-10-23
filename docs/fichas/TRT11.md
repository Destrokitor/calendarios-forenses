# Ficha do tribunal: TRT11

- **Nome:** Tribunal Regional do Trabalho da 11ª Região (Amazonas e Roraima)
- **Justiça / regime(s) de contagem:** Trabalhista. Dias úteis (CLT art. 775); art. 775-A. O TRT11 suspende "prazos, audiências e sessões" em 07-20/01 (art. 220 CPC).
- **Categoria:** **parcial**
- **Fonte(s) oficial(is) que ABREM na nuvem:**
  1. Suspensões: https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-susp (Joomla/iCagenda; lista de 58 eventos paginada 1/3, com os de 2026 na página 1: categoria "Suspensão de Prazos" ou "Suspensão de Expediente", título e data). Cada evento tem página própria (`.../calendario-susp/NNN-slug`) com categoria e datas.
  2. Feriados do mês corrente: https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-geral (e `/list`): calendário Joomla do MÊS em que a página é aberta (hoje outubro/2026) + "eventos futuros"; categoria "Feriado". Não dá para ler janeiro-setembro de 2026 sem parâmetros `&`/JS (e o robô não sobe o histórico). Cobre só o futuro.
  3. Página "Suspensão e Prorrogação de Prazos" (https://portal.trt11.jus.br/index.php/sociedades/suspensao-de-prazos), tabela "FERIADOS E DIAS SEM EXPEDIENTE ... A PARTIR DE 2015" (data | abrangência | base legal | observações) por Vara/Fórum: ABRE, mas DESATUALIZADA (último item de 2025, nenhum de 2026).
- **Fonte oficial que NÃO abre (ROBOTS-NEGA na nuvem):** o calendário anual de feriados 2026, PDF de 1 página com texto extraível (grade por mês + lista de feriados estaduais/municipais de Manaus, Boa Vista e 12 municípios do AM, "Ponto Facultativo (RA nº. 322/2025)"): https://portal.trt11.jus.br/images/arquivos/GestaoEstrategica/2025/2-_Calendario_Feriados_2026_V2.pdf . Não é ato normativo, é o calendário da Secretaria de Governança. O ato é a "RA nº 322/2025" (não localizado em fonte que abra).
- **Fixture(s) guardada(s):** `tests/fixtures/trt11/calendario-suspensao-lista.html`, `evento-690.html` (07-20/01), `suspensao-prorrogacao-prazos-pagina-desatualizada.html`, `calendario-feriados-2026.pdf` (cópia local do PDF; NÃO pode ser lida pelo robô na nuvem).
- **Formato:** HTML (listas/eventos iCagenda; sem tabela de feriados anuais) e PDF com texto (o de feriados, inacessível ao robô).
- **Como saem feriados locais e suspensões:** suspensões por evento (ver acima). Feriados locais (Manaus, Boa Vista, Parintins, Coari, ...) só no PDF anual (inacessível) ou como eventos "Feriado" do mês corrente. O que o TRT11 lista (PDF): 4/jun Corpus Christi, 5/set Elevação do Amazonas a Província, 24/out Aniversário de Manaus, 20/nov Manaus e Boa Vista, 15/dez Instalação do TRT11, etc. Sem pontos facultativos explicados na parte lida.
- **Particularidades / DUVIDA:**
  - Eventos 2026 em `calendario-susp`: "Suspensão dos prazos, audiências e sessões" 07/01 a 20/01/2026 (Suspensão de Prazos, evento 690); "Suspensão do expediente RA nº 322/2025" em 20/04, 05/06 e 10/08/2026 (Suspensão de Expediente, evento 700). DUVIDA: "suspensão do expediente" corre ou suspende prazo? O texto não diz; tratar como `sem_expediente` só com revisor. O PDF chama esses dias de "Ponto Facultativo (RA 322/2025)".
  - Copa 29/06: o TRT11 suspendeu o expediente a partir das 11h "sem prejuízo da contagem de prazos" (Portaria 238/2026/SGP, republicada), mas isso NÃO consta na lista de suspensões 2026 (só 4 eventos). Dia `parcial` fora da fonte lida.
  - Feriados nacionais/estaduais (Carnaval, Semana Santa, ...) não aparecem na lista de suspensões: só no PDF (inacessível) ou no calendário mensal.
  - A lista "calendario-susp" mistura Vara/Fórum de Boa Vista e interior do AM (eventos de 2025 em Manacapuru, Parintins, Tabatinga na página desatualizada).
- **Âncoras conferidas à mão** (lista e evento, 23/10/2026; PDF para feriados):
  1. **2026-01-07 a 2026-01-20** "Suspensão dos prazos, audiências e sessões", categoria Suspensão de Prazos (evento 690: "De Quarta, 7 de Janeiro de 2026 00:00 até Terça, 20 de Janeiro de 2026 23:59").
  2. **2026-04-20** "Suspensão do expediente RA nº 322/2025" (evento 700, categoria Suspensão de Expediente; "Todas as Datas": 10/08, 05/06, 20/04/2026).
  3. **2026-06-05** e **2026-08-10** idem (mesmo evento 700).
  4. **2026-10-12** "Feriado: Nossa Senhora Aparecida"; **2026-10-24** "Feriado: Aniversário de Manaus" (local; sábado); **2026-10-28** "Feriado: Dia do Servidor Público" (calendario-geral, mês de outubro).
  5. (só PDF, inacessível na nuvem) **2026-06-04** Corpus Christi, **2026-12-15** Instalação do TRT11, "15/dez - Instalação do TRT 11ª Região (RI)".
- **Pode rodar na nuvem?** PARCIAL. Runs https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986611463 e .../39986961133 (`success`), saída literal:
  ```
  ROBOTS-NEGA https://portal.trt11.jus.br/images/arquivos/GestaoEstrategica/2025/2-_Calendario_Feriados_2026_V2.pdf
  OK 200 124407 text/html; charset=utf-8 1.4 https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-susp
  OK 200 106391 text/html; charset=utf-8 1.2 https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-susp/690-suspensao-dos-prazos-audiencias-e-sessoes-3
  OK 200 134055 text/html; charset=utf-8 2.7 https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-geral
  OK 200 134110 text/html; charset=utf-8 1.5 https://portal.trt11.jus.br/index.php/sociedades/calendarios/calendario-geral/list
  OK 200 502 text/plain; charset=UTF-8 0.3 https://portal.trt11.jus.br/robots.txt
  OK 200 306731 text/html; charset=utf-8 6.1 https://portal.trt11.jus.br/index.php/sociedades/suspensao-de-prazos
  ```
  (robots.txt abre na nuvem, tem 502 bytes e barra `/images/`; localmente devolve 403.)
- **Cobertura:** parcial. Dá para ler as suspensões listadas (07-20/01, 20/04, 05/06, 10/08) e feriados do mês corrente em diante. Fica de fora: feriados nacionais/estaduais/municipais do ano (só no PDF barrado), dias parciais (Copa) e suspensões locais de Varas. Um motor só com isso entregaria calendário incompleto; recomendação: motor parcial só de suspensões + feriados futuros, ou aguardar fonte alternativa (ex.: RA 322/2025 no DEJT, não testado).
