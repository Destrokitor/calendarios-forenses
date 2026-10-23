# Ficha do tribunal: TJMRS

- **Nome:** Tribunal de Justiça Militar do Estado do Rio Grande do Sul
- **Justiça / regime(s) de contagem:** Militar estadual (CPPM/CPP; CPC subsidiário).
- **Categoria:** `parcial`
- **Fonte(s) oficial(is):**
  - Atos da Presidência, portarias (HTML com ementas e links para PDFs de texto): https://www.tjmrs.jus.br/atos-presidencia/categoria/portarias
  - Portaria 105/2025 (recesso e suspensão de prazos 20/12/2025 a 20/1/2026), PDF: https://www.tjmrs.jus.br/public/files/publicacoes/3493_2025121907_PORTARIA%20N%C2%BA%20105.2025%20-%20Recesso%20e%20suspens%C3%A3o%20de%20prazos.pdf
  - Resolução TJMRS 311/2024 (expediente suspenso de 20/12 a 6/1) e 312/2024 (prazos suspensos "anualmente" de 20/12 a 20/1): PDFs em https://www.tjmrs.jus.br/atos-presidencia/categoria/resolucoes (links `public/files/publicacoes/3185_...` e `3186_...`).
  - NÃO existe ato anual com feriados 2026 do TJMRS. A lista de portarias de 2026 (174 atos até 22/10) não tem nenhuma sobre feriado, ponto facultativo ou suspensão de expediente; as resoluções antigas "dias em que haverá horário diferenciado" não aparecem para 2026.
- **Fixture(s) guardada(s):** tests/fixtures/tjmrs/ (portaria_105_2025_recesso_2025_2026.pdf, resolucao_311_2024_expediente_natalino.pdf, resolucao_312_2024_prazos_20dez_20jan.pdf, noticia_prorrogacao_prazos_eproc_21_10_2026.html).
- **Formato:** PDF com texto (leitura limpa) e HTML. Sem OCR.
- **Como o calendário é publicado:** só o recesso de fim de ano por portaria + resolução permanente. Feriados nacionais/estaduais não são listados pelo tribunal (provável uso do calendário do TJRS/Porto Alegre, que é de outro tribunal). Prorrogações pontuais saem em notícia (ex.: 21/10/2026, eproc fora do ar das 10h às 14h; prazos vencidos no dia prorrogados, Ato Conjunto 03/2026-P e CGJME).
- **Locais:** Porto Alegre (sede) e Auditorias Militares (Porto Alegre, Santa Maria, Passo Fundo). Sem calendário local próprio.
- **Particularidades:**
  - Recesso = expediente suspenso 20/12 a 6/1 (Res. 311/2024, art. 1º); suspensão de PRAZOS vai até 20/1 (Res. 312/2024, art. 1º, "anualmente"; exceção para urgências e réus presos). São dois períodos diferentes: `recesso` x `suspensao_prazo`.
  - Como a 312 diz "anualmente", o período 20/12/2026 a 20/1/2027 já vale sem nova portaria (a Portaria 105/2025 só repete). # DUVIDA: aceitar a regra permanente ou esperar a portaria de dezembro/2026?
  - Prorrogação de vencimento por indisponibilidade do eproc (21/10/2026) é `suspensao_prazo` de um dia, que sai em notícia; não é feriado.
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2025-12-20 a 2026-01-06, expediente suspenso (recesso): Portaria 105/2025, art. 1º.
  2. 2026-01-01 a 2026-01-06, parte de 2026 do mesmo recesso: idem.
  3. 2025-12-20 a 2026-01-20, prazos suspensos: Portaria 105/2025, art. 2º.
  4. todo ano 20/12 a 20/1, prazos suspensos: Resolução 312/2024, art. 1º ("anualmente"); 20/12 a 6/1 expediente: Resolução 311/2024, art. 1º.
  5. 2026-10-21, prazos com vencimento no dia prorrogados para o 1º dia útil seguinte (eproc indisponível 10h às 14h): notícia de 21/10/2026, citando Ato Conjunto 03/2026-P e CGJME.
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 200 875023 text/html; charset=UTF-8 8.7 https://www.tjmrs.jus.br/atos-presidencia/categoria/portarias
OK 200 193856 application/pdf 1.9 https://www.tjmrs.jus.br/public/files/publicacoes/3493_2025121907_PORTARIA%20N%C2%BA%20105.2025%20-%20Recesso%20e%20suspens%C3%A3o%20de%20prazos.pdf
```
  (A Resolução 311/312 e a notícia 21/10 não foram incluídas no disparo; só o índice de portarias e a Portaria 105. Mesmo site e mesmo caminho `public/files/publicacoes/`.)
- **Pode rodar na nuvem?** Sim (índice HTML e PDF, HTTP 200).
- **Cobertura:** parcial. Só recesso e suspensão de prazos de fim de ano. Feriados nacionais, pontos facultativos, dias avulsos de 2026 não têm fonte do TJMRS; teriam de vir de outra regra (a aplicar por quem revisa).
