# Ficha do tribunal: TJRR

- **Nome:** Tribunal de Justiça do Estado de Roraima
- **Justiça / regime(s) de contagem:** Estadual; CPC.
- **Fonte(s) oficial(is):** Portaria TJRR/PR n. 1558, de 19/12/2025 (Presidente), publicada no DJe Ano XXVI, Edição 8006 de 22/12/2025, pp. 3–7. URL: https://diario.tjrr.jus.br/dpj/dpj-20251222.pdf (PDF com texto, 80 páginas, 2.612.868 bytes; o ato ocupa as páginas 3–7).
- **Fixture(s) guardada(s):** tests/fixtures/tjrr/portaria-1558-2025-dje-8006-2025-12-22-pags1e3a7.pdf (capa + págs. 3–7 do DJe; texto).
- **Como o calendário é publicado:** Anexo Único em tabela (DATA | DESCRIÇÃO | COMARCA), duas partes: "a) FERIADOS DA CAPITAL" (com "Todas as Comarcas" para os gerais e "Comarca de Boa Vista" para os da capital) e "b) FERIADOS DOS MUNICÍPIOS DO INTERIOR DO ESTADO" (comarca por linha). **Uma lista única com os locais por comarca.**
- **Locais:** comarcas: Boa Vista, Mucajaí, Bonfim, Caracaraí, Alto Alegre, São Luiz do Anauá, Pacaraima, Rorainópolis, Posto Avançado de Caroebe e de Iracema (nomes como na fonte; uma linha pode juntar várias comarcas: "Comarcas de Mucajaí, São Luiz do Anauá, Alto Alegre e Bonfim").
- **Particularidades:** Art. 3º: "Ficam suspensos o expediente e os prazos processuais ... nas datas consideradas como feriados ou pontos facultativos" — ou seja, ponto facultativo AQUI também suspende prazo. Recesso explícito no anexo: 01–06/01/2026 e 20–31/12/2026. Intervalos em uma célula ("16 a 18/2/2026", "1º a 3/4/2026"). Art. 2º: feriados/pontos decretados depois por outros Poderes não constam e são só comunicados — podem existir atos complementares em outros números do DJe (DUVIDA: não verifiquei portarias posteriores de 2026). Há "ponto facultativo referente ao feriado" de véspera/dia seguinte.
- **Âncoras conferidas à mão:**
  1. 2026-01-01 a 2026-01-06 Recesso forense, Todas as Comarcas — Anexo, a).
  2. 2026-02-16 a 2026-02-18 Segunda e Terça de carnaval e Quarta de cinzas, Todas as Comarcas — Anexo, a).
  3. 2026-12-20 a 2026-12-31 Recesso forense, Todas as Comarcas — Anexo, a).
  4. 2026-07-09 Aniversário do Município de Boa Vista (e 10/07 ponto facultativo), Comarca de Boa Vista — Anexo, a).
  5. Local interior: 2026-05-27 Aniversário do Município de Caracaraí, Comarca de Caracaraí — Anexo, b).
- **Pode rodar na nuvem?** SIM.
  - Run 39986359557: `OK 200 2612868 application/pdf 5.6 https://diario.tjrr.jus.br/dpj/dpj-20251222.pdf`
  - Run 39987095421: `OK 200 83119 text/html; charset=utf-8 2.4 https://www.tjrr.jus.br/` (apenas página inicial)
- **Cobertura:** completa para 2026 segundo a portaria base (verificar se há retificação em DJe posterior). Categoria: **pronto_para_motor**. Obs.: o motor deve ler uma edição fixa do DJe (URL com a data); se a Portaria for alterada, a alteração sairá em outra edição.
