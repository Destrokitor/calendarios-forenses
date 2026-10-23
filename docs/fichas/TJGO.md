# Ficha do tribunal: TJGO

- **Nome:** Tribunal de Justiça do Estado de Goiás
- **Justiça / regime(s) de contagem:** Estadual; CPC (dias úteis) no cível.
- **Categoria:** `pronto_para_motor`
- **Fonte(s) oficial(is):**
  1. https://docs.tjgo.jus.br/institucional/feriados/DOC_feriados_2026_08062026.pdf (PDF "FERIADOS 2026", do próprio tribunal, versão de 08/06/2026; inclui o ponto facultativo de 20/03, MotoGP).
  2. https://www.tjgo.jus.br/files/2026/01%20-%20Janeiro/Calendario%20do%20TJGO_2026_publicado-2.pdf (versão anterior, sem o item de 20/03).
  A home `https://www.tjgo.jus.br/` dá 403 na nuvem; os dois PDFs acima abrem (hosts `docs.tjgo.jus.br` e `www.tjgo.jus.br/files/...`).
- **Fixture(s) guardada(s):** `tests/fixtures/tjgo/feriados_tjgo_2026_08062026.pdf` (+ `.txt` via `pdftotext -layout`) e `calendario_tjgo_2026.pdf` (+ `.txt`).
- **Como o calendário é publicado:** tabela em PDF de 2 páginas: data ("16 de fevereiro", "20/12/26 a 6/1/2027"), dia da semana, descrição, alcance. Linhas quebradas em várias linhas de texto (alcance fica na coluna da direita).
- **Locais:** só 1 feriado local, "Feriado Municipal (restrito ao Tribunal e às comarcas de Goiânia, Iporá, Leopoldo de Bulhões e Senador Canedo)" em 24 de maio. Sai como texto livre no campo de alcance (lista de municípios após "comarcas de"). Demais feriados municipais de outras comarcas NÃO constam: cobertura parcial só nos locais.
- **Particularidades:** alcance muda por linha: "Feriado Nacional", "Feriado no Tribunal e em todas as comarcas*", "Ponto Facultativo em todo o Poder Judiciário Estadual", "Feriado Estadual (Lei 20.756/20)". 18/02 só "até 12h" (dia parcial). Recesso 20/12/2026 a 6/1/2027 (Art. 123 do Regimento Interno). O PDF avisa que as datas podem mudar e que a Presidência pode decretar pontos facultativos durante o ano. Há datas em fim de semana (24/05, 26/07, 24/10, 15/11).
  - DUVIDA: "Ponto Facultativo" (20/04, 05/06, 20/03) é suspensão de prazo ou só expediente? A tabela não diz; quem revisa decide.
  - DUVIDA: o arquivo muda ao longo do ano (nome com a data 08062026): o motor deve ler a URL mais nova; a URL pode mudar de nome.
- **Âncoras conferidas à mão** (no PDF `feriados_tjgo_2026_08062026.pdf`):
  1. 16 e 17/02/2026, Carnaval, "Feriado no Tribunal e em todas as comarcas" (pág. 1).
  2. 18/02/2026 "até 12h", Carnaval (dia parcial, pág. 1).
  3. 01 a 03/04/2026, Semana Santa (pág. 1).
  4. 08/12/2026, Dia da Justiça, Art. 123 do Regimento Interno (pág. 1).
  5. 20/12/2026 a 06/01/2027, Recesso Forense (pág. 1-2).
  Extra: 24/05/2026, municipal restrito a Goiânia, Iporá, Leopoldo de Bulhões e Senador Canedo.
- **Pode rodar na nuvem?** SIM (GitHub Actions, 23/10/2026), literal:
```
OK 200 148442 application/pdf 0.2 https://docs.tjgo.jus.br/institucional/feriados/DOC_feriados_2026_08062026.pdf
OK 200 118843 application/pdf 0.4 https://www.tjgo.jus.br/files/2026/01%20-%20Janeiro/Calendario%20do%20TJGO_2026_publicado-2.pdf
ERRO 403 https://www.tjgo.jus.br/          (home recusa; run 39986370049 e 39986365227)
ERRO URLError ... No address associated with hostname https://dje.tjgo.jus.br/
```
  (runs 39986370049 e 39986365227 do workflow testar-urls)
- **Cobertura:** parcial quanto a feriados municipais (só o de 24/05); completa para o calendário do Tribunal/comarcas todas.
