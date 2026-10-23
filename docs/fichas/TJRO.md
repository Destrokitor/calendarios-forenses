# Ficha do tribunal: TJRO

- **Nome:** Tribunal de Justiça do Estado de Rondônia
- **Justiça / regime(s) de contagem:** Estadual; CPC.
- **Fonte(s) oficial(is):** Ato nº 2579/2025-PR (DJE nº 218, 25/11/2025, pp. 18–20), alterado por Atos 2942/2025 (DJE 236, 22/12/2025), 657/2026, 782/2026 e 1255/2026; versão consolidada no repositório de atos: https://atos.tjro.jus.br/files/compilado152025202606126a2c5bf933d1c.pdf ; original https://atos.tjro.jus.br/files/original090104202512226949411020647.pdf ; ficha do ato https://atos.tjro.jus.br/detalhar/6484 (nº do ato 657/2026). Conteúdo descrito apenas por resultados de busca (NÃO consegui abrir nenhum arquivo, por isso não há fixture e as âncoras abaixo NÃO foram conferidas à mão no documento).
- **Fixture(s) guardada(s):** nenhuma (nada baixou, nem no meu computador: "Empty reply from server").
- **Como o calendário é publicado (segundo resumos):** Anexo Único em tabela com os feriados/pontos facultativos 2026 e os municipais "observados somente no âmbito da respectiva comarca ou Fórum Digital" — ou seja, lista única com locais por comarca. Recesso: 20/12/2026 a 06/01/2027 em regime de plantão (Instrução 043/2019-PR). Formato do arquivo: PDF (texto, provável).
- **Locais:** por comarca, no Anexo Único (não verificado).
- **Particularidades (segundo resumos, A CONFERIR no ato):** pontos facultativos 02/01, 18/02, 05/06, 24/12, 31/12; 11/08→10/08 (Ato 657/2026), Dia do Servidor 28/10→30/10; 20/07 Dia do Servidor da Justiça (Ato 782/2026); feriado municipal de Ouro Preto do Oeste 16/06→15/06 (Ato 1255/2026). Há alterações no meio do ano — o motor precisaria acompanhar o consolidado.
- **Âncoras:** NÃO conferidas (sem acesso ao documento). Pistas a conferir: 2026-12-20..2027-01-06 recesso; 2026-06-05 ponto facultativo; 2026-10-30 Dia do Servidor; 2026-08-10; 2026-06-15 Ouro Preto do Oeste.
- **Pode rodar na nuvem?** **NÃO.** O host atos.tjro.jus.br fecha a conexão sem resposta (também do meu computador); www.tjro.jus.br devolve 200 de 16.668 bytes na nuvem, mas é a página de desafio do WAF (no meu computador o HTML só tem `href="/TSPD/?type=25"`, sem conteúdo nem links) — não contornar.
  - Run 39986359557: `ERRO RemoteDisconnected Remote end closed connection without response https://atos.tjro.jus.br/files/original090104202512226949411020647.pdf`
  - Run 39986359557: `ERRO RemoteDisconnected Remote end closed connection without response https://atos.tjro.jus.br/files/compilado152025202606126a2c5bf933d1c.pdf`
  - Run 39986359557: `ERRO RemoteDisconnected Remote end closed connection without response https://atos.tjro.jus.br/detalhar/6484`
  - Run 39987095421: `ERRO RemoteDisconnected Remote end closed connection without response https://atos.tjro.jus.br/`
  - Run 39987095421: `ERRO URLError <urlopen error [Errno -2] Name or service not known> https://diario.tjro.jus.br/`
  - Run 39987095421: `OK 200 16668 text/html 2.4 https://www.tjro.jus.br/` (desafio de bot, sem conteúdo útil)
- **Cobertura:** nenhuma legível. Categoria: **incompativel**. Fonte alternativa não achada (o DJE oficial não foi localizado em host aberto; migalhas.com.br tem cópia de OUTRO ato, não oficial).
