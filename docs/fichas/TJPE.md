# Ficha do tribunal: TJPE

- **Nome:** Tribunal de Justiça de Pernambuco
- **Justiça / regime(s) de contagem:** Estadual; CPC.
- **Fonte(s) oficial(is):** Ato Conjunto nº 43, de 13/10/2025 (Presidente + Corregedor-Geral), publicado no DJe Edição 304/2025 de 14/10/2025. URLs: https://portal.tjpe.jus.br/documents/d/portal/feriados-2026-pdf (PDF com texto, 1.020.363 bytes — é a página do DJe com o ato) e notícia https://portal.tjpe.jus.br/-/tjpe-divulga-calend%C3%A1rio-de-feriados-forenses-de-2026 .
- **Fixture(s) guardada(s):** tests/fixtures/tjpe/ato-conjunto-43-2025-dje-304.pdf (baixada do computador do dono — NÃO vale como prova de nuvem).
- **Como o calendário é publicado:** ato único, PDF com texto. Art. 1º lista 21 feriados (incisos I–XXI) e o parágrafo único lista o RECESSO por dias soltos (02–06/01, 23 e 25–30/06, 20–24 e 26–31/12); Art. 2º feriado municipal do Recife (16/07); Art. 3º 13/02 expediente normal com trabalho remoto; **Art. 4º: "nas Comarcas do interior ... nos feriados definidos em lei municipal" — SEM lista**.
- **Locais:** só Recife (16/07, Nossa Senhora do Carmo) é nominal. Interior: nenhuma lista; depende de leis municipais de ~100 municípios.
- **Particularidades:** 18/02 (Cinzas) e 05/04 (domingo) e 15/11 (domingo) listados como feriados; Corpus Christi transferido de 04/06 para 22/06 (inciso XI); 24/06 São João; dias 23, 25–30/06 de "recesso junino"; 10/08 antecipado do dia 11/08; 30/10 transferido do 28/10; 8/12 também em dezembro, mas 20–31/12 é recesso (24/12 e 25/12 dentro). Art. 6º: calendário pode ser alterado (há atos posteriores, ex.: o ato do calendário 2027 saiu em 09/2026).
- **Âncoras conferidas à mão:**
  1. 2026-06-22 Corpus Christi (transferido de 04/06) — Art. 1º, inciso XI.
  2. 2026-03-06 Data Magna de Pernambuco — Art. 1º, inciso V.
  3. 2026-12-20 a 2026-12-31 recesso (menos o já listado 25/12 como Natal; dias 20,21,22,23,24,26..31 no parágrafo único) — Art. 1º, parágrafo único.
  4. 2026-07-16 Nossa Senhora do Carmo, só Comarca do Recife — Art. 2º.
  5. 2026-10-30 Dia do Servidor Público (transferido de 28/10) — Art. 1º, inciso XVI.
- **Pode rodar na nuvem?** **NÃO.** O robô desiste antes de baixar: o robots.txt do host não pôde ser lido na nuvem (o `urllib.robotparser` trata 401/403/5xx como "proibido"; no meu computador o robots.txt é `Disallow:` vazio e o PDF abre 200). Resultado literal:
  - Run 39987095421: `ROBOTS-NEGA https://portal.tjpe.jus.br/-/tjpe-divulga-calend%C3%A1rio-de-feriados-forenses-de-2026`
  - Run 39987095421: `ROBOTS-NEGA https://portal.tjpe.jus.br/documents/d/portal/feriados-2026-pdf`
  - Run 39987095421: `ROBOTS-NEGA https://www.tjpe.jus.br/`
  - (Run 39986359557: `ROBOTS-NEGA https://portal.tjpe.jus.br/documents/d/portal/feriados-2026-pdf`)
  Nenhuma outra fonte oficial de host diferente foi achada (o DJe está sob o mesmo domínio).
- **Cobertura:** mesmo que abrisse: parcial (feriados locais do interior fora; só Recife).
- **Categoria: pronto_para_motor** (corrigido em 24/10: o PDF abriu na nuvem, `OK 200 1020363 application/pdf` em https://portal.tjpe.jus.br/documents/d/portal/feriados-2026-pdf; o ROBOTS-NEGA acima era erro do nosso leitor de robots.txt, já corrigido). Motor em `robo/motores/tjpe.py`, cobertura `parcial` (só Recife nominal).
