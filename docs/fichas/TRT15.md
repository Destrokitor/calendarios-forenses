# Ficha do tribunal: TRT15

- **Nome:** Tribunal Regional do Trabalho da 15ª Região (Campinas / interior de SP)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT 775), suspensão 20/12 a 20/01 (775-A).
- **Fonte(s) oficial(is) (todas PDF com texto, quem publica: Presidência/Corregedoria):**
  1. Feriados do tribunal todo + recesso + "suspensão de expediente": Anexo da Portaria GP-CR nº 016/2025 ("Feriados com emenda em 2026", republicada por erro material): `https://trt15.jus.br/sites/portal/files/fields/normas-institucionais/anexos/2025/anexo_portaria-gp-cr-no-0162025_id50386.pdf` (1 página).
  2. Feriados MUNICIPAIS (1ª instância, por localidade): Portaria CR nº 2/2025 de 27/11/2025 (HTML do ato: `https://trt15.jus.br/legislacao/normas-institucionais/portarias/portaria-cr-no-22025`) + Anexo Único (PDF): `https://trt15.jus.br/sites/portal/files/roles/institucional/corregedoria/Feriados/Feriados%20Municipais%202026%20-%20Anexo%20%C3%9Anico%20-%20Atualizado%2027_11_2025%20-%20Ato%200000457-92.2025%20-%20P%C3%A1gina1.pdf`
  3. Índice das portarias de feriados municipais (para detectar alterações/anos): `https://trt15.jus.br/transparencia/feriados-municipais`
- **Fixture(s):** `tests/fixtures/trt15/anexo_portaria_gp_cr_016_2025.pdf`, `feriados_municipais_2026_anexo_unico.pdf`, `portaria_cr_2_2025.html`, `feriados_municipais.html`.
- **Como é publicado:** PDF com texto (pdftotext -layout funciona). Anexo 1: tabela por mês com colunas S T Q Q S (seg a sex) e asterisco (*) = suspensão de expediente. Anexo Único: tabela `Localidade | Dia | Mês | Motivo | Legislação`, ~102 linhas, localidade sem feriado vem como "Não haverá feriado municipal que recaia em dia útil" (serve para montar a lista de comarcas: locais com lista vazia). Dia às vezes "1º".
- **Locais:** ~dezenas de municípios sede de Vara (nome como "Campinas", "Campos do Jordão"...). A portaria admite alteração no ano por nova lei municipal (checar o índice 3 para portarias novas; elas "alteram a redação").
- **Particularidades (ARMADILHAS):**
  - O Anexo 1 usa **tachado** (11/08 e 28/10 aparecem riscados, pois o feriado foi transferido para 10/08 e 30/10) e o `pdftotext` NÃO mostra o tachado: o 11/08 e o 28/10 saem como datas normais. O motor precisa tratar a transferência pelo texto "transferido para o dia ...".
  - Feriado x suspensão: "* Suspensão de expediente" aparece em 18/02 (quarta de cinzas), 20/04, 05/06, 10/07, 10/08, 30/10, 07/12 (asterisco colado ao dia). O texto do anexo não diz se é suspensão de prazo ou sem expediente; tratar como suspensão de expediente (prazo prorroga). # DUVIDA: efeito exato.
  - Recesso: 1-2 e 5-6/01 ("Confraternização/Recesso") e 21-31/12. Os dias 7 a 20/01 não são listados (vêm da regra do art. 775-A).
  - **Divergência:** 12/08 "Dia do Evangélico (feriado municipal em Campinas, Lei 16.785/2025)" está no Anexo 1 como "**", mas o Anexo Único da CR 2/2025 diz que Campinas "não haverá feriado municipal que recaia em dia útil" (12/08/2026 é quarta). # DUVIDA: aplicar 12/08 a Campinas? Quem revisa decide.
  - 07/12 (Dia da Padroeira, Lei Municipal 3.902/1970) é lei de Campinas, mas o anexo trata como suspensão do tribunal todo.
- **Âncoras conferidas à mão (Anexo da Portaria GP-CR 016/2025, página única, vistas em imagem do PDF):**
  1. 2026-02-16 e 2026-02-17: Carnaval (Lei 5.010/1966 art. 62, III).
  2. 2026-02-18: Suspensão de expediente / quarta-feira de cinzas (marcada com *).
  3. 2026-08-10: Suspensão de expediente + Dia da Instalação dos Cursos Jurídicos (transferido do dia 11, que está tachado).
  4. 2026-10-30: Dia do Servidor Público transferido do 28/10 (tachado), com *.
  5. Municipal (Anexo Único da CR 2/2025): Amparo, 08/04 "Aniversário da Cidade", Lei Municipal 612/1968; Andradina 20/01 "Feriado Religioso", Lei 1309/1990 e 06/08, Lei 3054/2014.
- **Pode rodar na nuvem?** SIM. Run 39986139412 (GitHub Actions, 23/10/2026), literal:
  ```
  OK 200 146434 text/html; charset=UTF-8 1.2 https://trt15.jus.br/legislacao/normas-institucionais/portarias/portaria-cr-no-22025
  OK 200 63160 application/pdf 0.6 https://trt15.jus.br/sites/portal/files/roles/institucional/corregedoria/Feriados/Feriados%20Municipais%202026%20-%20Anexo%20%C3%9Anico%20-%20Atualizado%2027_11_2025%20-%20Ato%200000457-92.2025%20-%20P%C3%A1gina1.pdf
  OK 200 185874 application/pdf 0.3 https://trt15.jus.br/sites/portal/files/fields/normas-institucionais/anexos/2025/anexo_portaria-gp-cr-no-0162025_id50386.pdf
  OK 200 153738 text/html; charset=UTF-8 0.8 https://trt15.jus.br/transparencia/feriados-municipais
  ```
- **Cobertura:** completa para o que o tribunal publica (geral + municipal da 1ª instância), com as duas dúvidas acima.
- **Categoria: `pronto_para_motor`.**
