# Ficha do tribunal: TJDFT

- **Nome:** Tribunal de Justiça do Distrito Federal e dos Territórios
- **Justiça / regime(s) de contagem:** estadual comum (DF); CPC. Portaria Conjunta 105/2025, art. 5º: prazos que vencerem em feriado ficam automaticamente prorrogados para o primeiro dia útil.
- **Fonte(s) oficial(is):**
  - Principal (TABELA HTML, mantida durante o ano): https://www.tjdft.jus.br/feriados-e-expedientes-suspensos — colunas "Data | Descrição", uma linha por dia, formato dd/mm/aaaa, inclui feriados, pontos facultativos, semana santa, recesso e suspensões posteriores (ex.: "29/06/2026 PONTO FACULTATIVO - PORTARIA CONJUNTA 48/2026").
  - Ato: Portaria Conjunta nº 105, de 17/12/2025 (Diário Administrativo, disponibilizada 26/12/2025, publicada 29/12/2025), no SEI: https://sei.tjdft.jus.br/sei/publicacoes/controlador_publicacoes.php?acao=publicacao_visualizar&id_orgao_publicacao=0&id_documento=5146952 (HTML, charset ISO-8859-1; texto em 21 incisos do art. 2º, em prosa).
  - A AASP aponta "Ato nº 626/2025" do TRF5: não é do TJDFT.
- **Fixture(s) guardada(s):** tests/fixtures/tjdft/feriados_e_expedientes_suspensos.html, portaria_conjunta_105_2025_sei.html
- **Como o calendário é publicado:** tabela HTML (a página) + texto da portaria (HTML). A tabela tem cerca de 45 linhas em 2026 e é a melhor para o motor; botão "Próximo Ano" (não investiguei se há URL por ano).
- **Locais (comarcas/foros/municípios):** NÃO há. O Distrito Federal é uma só jurisdição: o calendário vale para todas as circunscrições. Locais = lista vazia (ou uma chave única).
- **Particularidades:**
  - A tabela diz "RECESSO FORENSE - ART. 60, LEI 11967/2008" (digitação; a portaria cita Lei 11.697/2008) em 02 a 06/01 e 20 a 31/12 (menos 24, 25 e 31/12, que aparecem como véspera/Natal/Ano Novo). A portaria em si NÃO lista o recesso: só a tabela. Recesso do início de 2026 é 02 a 06/01.
  - Feriados forenses: 16 a 18/02 (carnaval e cinzas), 01 a 05/04 (semana santa), 11/08, 01 e 02/11, 08/12 (art. 60 Lei 11.697/2008).
  - Pontos facultativos (portaria art. 2º os inclui na lista de "feriados"; a tabela os trata como expediente suspenso): 20/04, 04/06 (Corpus Christi), 05/06, 10/08, 07/12, 24/12 (véspera), 31/12 (véspera) e 30/10 (transferência do Dia do Servidor, 28/10). Efeito de ponto facultativo: o site chama de "expedientes suspensos"; tratar como `sem_expediente` e registrar DUVIDA para revisão.
  - O art. 3º (cartórios extrajudiciais) tem lista DIFERENTE (ex.: 18/02 só até 12h; 30/11) — não confundir com o calendário judicial.
  - Suspensões durante o ano entram só na tabela do site (29/06 por Portaria Conjunta 48/2026; também 1º/05 em notícia).
- **Âncoras conferidas à mão** (tabela da página e art. 2º da Portaria Conjunta 105/2025):
  1. 2026-01-01, Confraternização Universal (inciso I).
  2. 2026-02-16, 17 e 18, carnaval e quarta-feira de cinzas, art. 60 Lei 11.697/2008 (inciso II; tabela "FERIADO FORENSE").
  3. 2026-04-20, ponto facultativo, Portaria Conjunta 105/2025 (inciso IV; tabela).
  4. 2026-10-30, Dia do Servidor transferido do 28/10 (inciso XIII; tabela "LEI 8112/90 E PORT. CONJ. 105/2025").
  5. 2026-12-20 a 12-23 e 12-26 a 12-30, recesso forense (tabela; fora do texto da portaria).
- **Pode rodar na nuvem?** SIM para a tabela do site. Saída literal (execução `testar-urls` nº 39986386976, 23/10/2026):
  `OK 200 139468 text/html;charset=utf-8 1.7 https://www.tjdft.jus.br/feriados-e-expedientes-suspensos`
  (A URL do SEI tem `&` e não pôde ser testada pelo workflow atual, que quebra no shell. A tabela basta para o motor.)
- **Cobertura:** completa. Categoria: **pronto_para_motor** (ler a tabela HTML; usar a portaria só como fonte de motivo/comprovação).
