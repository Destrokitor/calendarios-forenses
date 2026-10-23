# Ficha do tribunal: TRT7

- **Nome:** Tribunal Regional do Trabalho da 7ª Região (Ceará)
- **Justiça / regime(s) de contagem:** Trabalhista. Dias úteis (CLT art. 775); art. 775-A.
- **Categoria:** **incompativel**
- **Fonte(s) oficial(is) conhecidas (pelo índice de busca; todas FALHAM na nuvem):**
  - Portaria TRT7.GP nº 518, de 18/11/2025 (dias sem expediente 2026), alterada pela Portaria nº 64/2026 (pontos facultativos 20/04, 05/06, 10/08 e 07/12, seguindo TST/CSJT) e nº 127/2026 (feriado municipal de Fortaleza em 13/04/2026, tricentenário, Lei Municipal 11.649/2026). Ato Conjunto TRT7.GP.CORREG nº 2/2026 (29/06, Copa: expediente 7h30-12h, prazos prorrogados). Informações do índice de busca, NÃO lidas no original.
  - Página "Calendário de Feriados 2026" (lista por data/localidade, segundo o índice de busca).
- **Fixture(s) guardada(s):** `tests/fixtures/trt7/home-trt7-2026-10-23.html` (só a página inicial; não traz o calendário) e `LEIAME.txt`. Nenhuma cópia do calendário foi possível.
- **Formato:** não verificado (nenhuma fonte abriu).
- **URLs testadas e erro (nuvem, literal):** runs https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986611463 , .../39986961133 , .../39987256478 (todos `success` como workflow; as URLs falham):
  ```
  OK 200 115177 text/html; charset=UTF-8 1.2 https://www.trt7.jus.br/
  ERRO 404 https://www.trt7.jus.br/index.php/servicos/agendas-e-calendarios/calendario-de-feriados-do-trt-ce/16348-calendario-de-feriados-2026
  ERRO 404 https://www.trt7.jus.br/files/atos_normativos/portarias_presidencia/2025/PORTARIA%20PRESI%20518-2025%20este.pdf
  ERRO 404 https://www.trt7.jus.br/files/atos_normativos/portarias_presidencia/2026/PORTARIA%20PRESI%20N%2064-2026.pdf
  ERRO 404 https://www.trt7.jus.br/files/atos_normativos/portarias_presidencia/2026/PORTARIA%20PRESI%20N%20127-2026.pdf
  ERRO 404 https://www.trt7.jus.br/files/atos_normativos/atos_conjuntos/2026/ATO%20CONJ%20TRT7.GP%20CORREG%20N%202-2026.pdf
  ERRO 404 https://www.trt7.jus.br/index.php/noticias/todas-as-noticias/16378-trt-ce-divulga-calendario-de-feriados-em-2026
  ERRO 404 https://www.trt7.jus.br/index.php/noticias/todas-as-noticias/16743-justica-do-trabalho-do-ceara-atualiza-calendario-de-2026-com-novos-pontos-facultativos-2
  ERRO 404 https://www.trt7.jus.br/index.php/servicos/agendas-e-calendarios.html
  ERRO 404 https://www.trt7.jus.br/index.php/servicos/agendas-e-calendarios/calendario-de-feriados-do-trt-ce
  ERRO 403 https://www.trt7.jus.br/index.php
  ROBOTS-NEGA https://servicos.trt7.jus.br/categoria_servico/25c5dd36-42ab-4a45-9667-c82a0b38cdd1
  ERRO 404 https://www.trt7.jus.br/robots.txt
  OK 200 86629 text/html; charset=UTF-8 https://www.trt7.jus.br/index.php/legislacao/atos-normativos/portarias.html
  ```
  A última é um espelho estático antigo ("Página atualizada em 22/10/2025"), sem as portarias de 2026. Do computador do autor (NÃO vale como prova) as mesmas URLs com `?option=com_content&...` dão 403 do CloudFront e as de `/files/...` dão 404. O Portal de Serviços (`servicos.trt7.jus.br`), para onde o site aponta ("Agendas e calendários"), é barrado pelo `robots.txt` do próprio tribunal na nuvem (ROBOTS-NEGA). Nada disso foi contornado.
- **Locais, particularidades:** não verificado. Pelo índice de busca: a portaria 518 trata pontos facultativos "nas Varas do Trabalho sediadas em municípios que não possuam norma legal que estabeleça a data como feriado municipal", e feriados municipais de cada cidade do Ceará, com acréscimos avulsos por portaria (Fortaleza 13/04).
- **Âncoras conferidas à mão:** NÃO foi possível (nenhum ato lido). Datas só do índice de busca, sem valor de âncora: 20/04, 05/06, 10/08, 07/12 (pontos facultativos, Portaria 64/2026); 13/04 Fortaleza (Portaria 127/2026); 29/06 (Ato Conjunto 2/2026).
- **Pode rodar na nuvem?** NÃO (ver acima).
- **Cobertura:** nenhuma. Sugestão para depois: procurar o ato no Diário Eletrônico da Justiça do Trabalho (DEJT) ou aguardar o tribunal liberar o Portal de Serviços; o calendário nacional da Justiça do Trabalho não substitui os feriados municipais do Ceará.
