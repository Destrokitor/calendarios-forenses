# Ficha do tribunal: TJTO

- **Nome:** Tribunal de Justiça do Estado do Tocantins
- **Justiça / regime(s) de contagem:** Estadual; CPC.
- **Fonte(s) oficial(is):** Portaria nº 3741, de 10/11/2025 (Presidente), "Instituir o calendário de feriados e pontos facultativos ... exercício de 2026", publicada no Diário da Justiça nº 5995 de 10/11/2025, pp. 39–40. PDF do DJ (API pública): https://diario.tjto.jus.br/api/diario/03512a628c56487e9b4d0ebba3c0e9c4 (id = `idFileStorage` sem hífens; lista: `https://diario.tjto.jus.br/api/diario/publicados?ano=2025&mes=11&page=1` devolve JSON com `numDiario`, `dtPublicacao`, `idFileStorage`). O portal www.tjto.jus.br está em "manutenção" por incidente cibernético (22/10/2026): só devolve página de aviso (9.257 bytes) em qualquer rota, inclusive a lista "Feriados municipais das comarcas".
- **Fixture(s) guardada(s):** tests/fixtures/tjto/portaria-3741-2025-dj-5995-2025-11-10-pags39-40.pdf (págs. 39–40 do DJ 5995; texto).
- **Como o calendário é publicado:** Art. 1º tabela de 2 colunas (DATAS | FERIADOS E/OU PONTOS FACULTATIVOS) com a lista estadual; Art. 4º feriados municipais da Capital (19/03 Padroeiro de Palmas, 20/05 aniversário); **Art. 5º: "As Comarcas do interior ... terão feriados municipais próprios, competindo ao magistrado Diretor do Foro deliberar sobre o expediente" — SEM lista na portaria.** Existe documento à parte "Feriados municipais das comarcas" (página do portal, ano de referência 2023) hoje fora do ar; portarias avulsas por comarca (ex.: Portaria 3134/2026, DJ 6200: Goiatins 13/10 e 12/11).
- **Locais:** só Palmas é nominal. Interior: por comarca/Diretor do Foro (portarias soltas).
- **Particularidades:** pontos facultativos (20/04, 05/06, 10/08, Art. 3º) — DUVIDA se suspendem prazo. Transferências: 28/10→30/10 e 08/12→18/12 (Art. 2º). 15/08 Senhor do Bonfim (Lei 4.509/2024), 05/10 Criação do Estado, 08/09 Padroeira. Datas em texto ("16 e 17 de fevereiro", "1º, 2 e 3 de abril"). **Sem recesso na portaria** (DUVIDA: fonte do recesso 20/12–06/01 é outra; o site de calculadora cita apenas CPC art. 220). Em 20–23/10/2026 prazos suspensos por Decreto Judiciário 772 (incidente cibernético) — exemplo de suspensão avulsa fora do calendário.
- **Âncoras conferidas à mão:**
  1. 2026-02-16 e 2026-02-17 Carnaval — Art. 1º, "16 e 17 de fevereiro".
  2. 2026-04-01 a 2026-04-03 Semana Santa — Art. 1º, "1º, 2 e 3 de abril".
  3. 2026-10-30 Dia do Servidor Público (transferido de 28/10) — Art. 1º e Art. 2º.
  4. 2026-12-18 Dia da Justiça (transferido de 08/12) — Art. 1º e Art. 2º.
  5. Local: 2026-03-19 Padroeiro de Palmas e 2026-05-20 aniversário de Palmas — Art. 4º.
- **Pode rodar na nuvem?** SIM para o Diário da Justiça (API); NÃO para o portal (manutenção).
  - Run 39986359557: `OK 200 1598047 application/pdf 4.2 https://diario.tjto.jus.br/api/diario/6418b8ff46d942ac8aed3317ce6a1849` (DJ 6200 de 08/10/2026)
  - Run 39986359557: `OK 200 9257 text/html; charset=utf-8 0.6 https://www.tjto.jus.br/comunicacao/noticias/tjto-publica-calendario-de-feriados-e-pontos-facultativos-para-2026` (é a página de manutenção, não a notícia)
  - Run 39986359557: `OK 200 9257 text/html; charset=utf-8 1.6 https://www.tjto.jus.br/informacoes/feriados/21127-feriados-municipais-das-comarcas/download` (idem: aviso de manutenção, não o PDF)
  - A URL exata do DJ 5995 (…/03512a628c56…) NÃO foi testada na nuvem; foi testada outra edição do mesmo endpoint (DJ 6200). Motor: achar a edição por `publicados?ano=2025&mes=11` e baixar.
- **Cobertura:** estaduais + Palmas completos; interior fora. Categoria: **parcial**.
