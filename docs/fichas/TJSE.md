# Ficha do tribunal: TJSE

- **Nome:** Tribunal de Justiça de Sergipe
- **Justiça / regime(s) de contagem:** Estadual; CPC.
- **Fonte(s) oficial(is):** "Calendário 2026 — Comarcas de Aracaju e do interior do Estado e respectivos distritos" (PDF do TJSE, sem número de ato): https://www.tjse.jus.br/portal/arquivos/documentos/publicacoes/calendarios/calendario-tjse-2026.pdf (PDF com texto, 7 páginas, 262.991 bytes). Complementos por portaria normativa avulsa (ex.: PN 18/2026-GP1 Quinta Santa, PN 24/2026 20/04, PN 72/2026 10–11/08), divulgadas em https://agencia.tjse.jus.br/noticias/... (notícias).
- **Fixture(s) guardada(s):** tests/fixtures/tjse/calendario-tjse-2026.pdf (baixada do computador do dono).
- **Como o calendário é publicado:** um PDF mês a mês com duas colunas: "FERIADOS — COMARCAS/DISTRITOS" (nacionais, estaduais e municipais: "02/02 – Capela (Padroeira)", "17/03 – Aracaju (Aniversário da Capital)") e "PREVISÃO DE PONTOS FACULTATIVOS". Última linha: "RECESSO FORENSE – DE 20/12/2026 A 06/01/2027". **Locais na mesma lista**, nome do município + motivo entre parênteses; feriado geral sem município.
- **Locais:** ~90 linhas municipais (Aracaju, Lagarto, Itabaiana, Estância...).
- **Particularidades:** pontos facultativos são só "PREVISÃO" — viram dia sem expediente por portaria normativa posterior (ex.: 02/04, 20/04, 10/08). DUVIDA: ponto facultativo não suspende prazo sozinho; só se o tribunal declarar sem expediente. Carnaval: 16/02 ponto facultativo, 17/02 feriado, 18/02 "Quarta-feira de Cinzas" ponto facultativo. 16/03 ponto facultativo só em Aracaju/TJ. "30/10 Dia do Funcionário Público", "14/12 Dia do Ministério Público" listados como feriados. Layout de colunas dificulta ligar o ponto facultativo ao mês no texto (usar `-layout`).
- **Âncoras conferidas à mão (no PDF):**
  1. 2026-03-17 Aracaju (Aniversário da Capital) — março, coluna Feriados, local Aracaju.
  2. 2026-07-08 Emancipação Política de Sergipe — julho.
  3. 2026-02-17 Carnaval (feriado); 16/02 e 18/02 pontos facultativos — fevereiro.
  4. 2026-12-20 a 2027-01-06 Recesso Forense — rodapé de dezembro.
  5. 2026-10-30 Dia do Funcionário Público — outubro; e 2026-08-11 Dia do Magistrado.
- **Pode rodar na nuvem?** NÃO pelo robô atual: `ROBOTS-NEGA`. O robots.txt do host é `User-agent: * / Disallow: / / Allow: /portal` (confirmado no meu computador). O `urllib.robotparser` do projeto aplica a primeira regra (`Disallow: /`) e nega tudo; pelo padrão RFC 9309 (regra mais específica vence) `/portal/...` seria PERMITIDO. Decisão de política do orquestrador/dono (não mudei nada). Resultados literais:
  - Run 39986359557: `ROBOTS-NEGA https://www.tjse.jus.br/portal/arquivos/documentos/publicacoes/calendarios/calendario-tjse-2026.pdf`
  - Run 39987095421: `ROBOTS-NEGA https://www.tjse.jus.br/portal/`
  - Run 39987095421: `ERRO URLError <urlopen error timed out> https://agencia.tjse.jus.br/noticias/item/16541-tiradentes-ponto-facultativo-e-feriado`
- **Cobertura:** se liberado: parcial (pontos facultativos dependem de portarias avulsas em notícias, hospedadas em host que deu timeout).
- **Categoria: pronto_para_motor** (o `incompativel` anterior veio de um erro do nosso leitor de robots.txt, já corrigido em `robo/robots.py`, RFC 9309). Evidência do teste de nuvem de 24/10: `OK 200 262991 application/pdf` em https://www.tjse.jus.br/portal/arquivos/documentos/publicacoes/calendarios/calendario-tjse-2026.pdf.
