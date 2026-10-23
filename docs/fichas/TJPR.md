# Ficha do tribunal: TJPR

- **Nome:** Tribunal de Justiça do Estado do Paraná
- **Justiça / regime(s) de contagem:** Estadual; CPC (dias úteis). Compensação de 1h em alguns dias suspensos (ver DUVIDA).
- **Fonte(s) oficial(is):** Decreto Judiciário n.º 621/2025 - P-SEP (SEI 0064955-90.2025.8.16.6000), assinado em 19/11/2025 pela Presidente. URL: https://portal.tjpr.jus.br/pesquisa_athos/anexo/7104379 (PDF com texto, 2 páginas zip + 7 pág.; 71.779 bytes).
- **Fixture(s) guardada(s):** tests/fixtures/tjpr/decreto-judiciario-621-2025.pdf (baixada do computador do dono; a PROVA de nuvem está abaixo).
- **Como o calendário é publicado:** um único decreto anual, PDF com texto (`pdftotext -layout` lê limpo). Art. 1º feriados do tribunal; Art. 2º suspensões de expediente COM compensação de 1h; Art. 3º suspensões sem compensação (24 e 31/12); **Art. 4º consolida os feriados locais dos municípios-sede de comarca, mês a mês** ("dia N: Município (motivo), ...").
- **Locais (comarcas/foros/municípios):** ~150 municípios-sede aparecem no Art. 4º, nome do município sem sufixo ("São José dos Pinhais", "Foz do Iguaçu"). Município que não aparece não tem feriado próprio. Uma lista única, nada de portaria solta por comarca (feriado municipal novo no meio do ano pode sair em decreto à parte — não verificado).
- **Particularidades:** (a) Art. 2º: 16/02, 02/04, 20/04 e 05/06 = "suspenso o expediente ... mediante compensação de 1h" => tipo suspensao_prazo/sem_expediente? DUVIDA para quem revisa. (b) 24 e 31/12 suspensos (Art. 3º). (c) 08/09 Padroeira de Curitiba só no município de Curitiba (aparece no Art. 1º, não no 4º). (d) 30/10 (Dia do Funcionário Público, transferido de 28/10) e 18/12 (Dia da Justiça, transferido de 8/12). (e) 15/11 cai em domingo. (f) **O decreto NÃO menciona recesso forense (20/12–06/01)**: DUVIDA, a fonte do recesso precisa ser outra (ou aplicar a regra do CPC art. 220 e registrar). Feriado de 03/04 = Paixão de Cristo; 05/06 e 02/04 são suspensões.
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2026-02-17 Carnaval — Art. 1º, "fevereiro: dia 17 (terça-feira) - Carnaval".
  2. 2026-06-04 Corpus Christi — Art. 1º, "junho: dia 04 (quinta-feira) - Corpus Christi".
  3. 2026-12-18 Dia da Justiça (transferido do dia 08/12) — Art. 1º, "dezembro: dias 18 (sexta-feira) - Dia da Justiça".
  4. 2026-02-16 véspera de Carnaval, expediente suspenso com compensação de 1h — Art. 2º (DUVIDA do efeito).
  5. Local: 2026-03-19 São José dos Pinhais (Dia do Padroeiro) — Art. 4º, "Março: ... dia 19: ... São José dos Pinhais (Dia do Padroeiro do Município)". Também 2026-09-08 só Curitiba (Art. 1º).
- **Pode rodar na nuvem?** SIM (teste no GitHub Actions). Atenção: a 1ª tentativa deu 503 e a 2ª deu 200 em 22,3 s — o servidor é lento/oscila; o motor precisa de tentativas com espera.
  - Run 39986359557: `ERRO 503 https://portal.tjpr.jus.br/pesquisa_athos/anexo/7104379`
  - Run 39987095421: `OK 200 71779 application/pdf 22.3 https://portal.tjpr.jus.br/pesquisa_athos/anexo/7104379`
  - robots.txt de portal.tjpr.jus.br: só `Disallow: /tjpr-assinador/` (o caminho acima é permitido).
- **Cobertura:** completa para feriados/suspensões/locais; **recesso fora do decreto** (ver Particularidades). Categoria: **pronto_para_motor** (com a ressalva do recesso e da oscilação 503).
