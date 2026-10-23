# Ficha do tribunal: TJAC

- **Nome:** Tribunal de Justiça do Estado do Acre
- **Justiça / regime(s) de contagem:** estadual comum; CPC (dias úteis, art. 219, e art. 224 §1º). A portaria manda aplicar o art. 224 §1º do CPC aos prazos que vencerem em dia de suspensão.
- **Fonte(s) oficial(is):**
  - Principal: Portaria PRESI nº 6569/2025 (publicada no DJe 7.950, 3.2.2026, p. 18-19, assinada em 30/01/2026), com o calendário 2026 em tabela (mês, dia, evento, tipo, natureza, legislação).
    URL: https://webdev.tjac.jus.br/wp-content/uploads/2025/12/Portaria_PRESI_TJAC_6569_2025.pdf
  - Base citada: Decreto estadual nº 11.809/2025 (calendário do Executivo).
  - A página AASP diz "não divulgado em meios oficiais" para o TJAC: está errada, a portaria existe.
- **Fixture(s) guardada(s):** tests/fixtures/tjac/portaria_presi_6569_2025.pdf (7 páginas, PDF com camada de texto; `pdftotext -layout` lê bem)
- **Como o calendário é publicado:** PDF com texto, tabela por mês. Colunas: DIA, SEMANA, EVENTO, TIPO (Feriado / Feriado Forense / Ponto facultativo), NATUREZA (Nacional / Estadual / Municipal (Cidade...) / Regimental), LEGISLAÇÃO. Células quebram em várias linhas (o difícil é juntar linhas quebradas, em especial as de vários municípios).
- **Locais (comarcas/foros/municípios):** os feriados MUNICIPAIS vêm DENTRO da mesma tabela, na coluna NATUREZA ("Municipal (Xapuri)", "Municipal (Senador Guiomard, Assis Brasil e Manoel Urbano)", ou "Feriado Municipal (Acrelândia, Bujari, Capixaba, ...)" no dia 28/04). São os municípios do interior com ato citado (cerca de 20 cidades: Xapuri, Epitaciolândia, Porto Acre, Rodrigues Alves, Plácido de Castro, Sena Madureira, Senador Guiomard, Assis Brasil, Manoel Urbano, Mâncio Lima, Capixaba, Bujari, Feijó, Brasileia, Tarauacá, Cruzeiro do Sul, Marechal Thaumaturgo, Santa Rosa do Purus, Acrelândia, Jordão, Rio Branco...). Um mesmo dia pode valer para vários municípios. A lista de comarcas em si não está no documento: municípios sem ato citado não aparecem (podem ficar com lista vazia).
- **Particularidades:**
  - Art. 2º: aniversário de município = feriado municipal; naquela comarca só há plantão.
  - Art. 2º, parágrafo único: pontos facultativos MUNICIPAIS dependem de adesão (diretor do foro, avisa a Presidência com 72 h; na capital a Presidência decide). Não dá para saber pelo documento se houve adesão: tratar ponto facultativo municipal como DUVIDA.
  - A tabela mistura "Feriado", "Feriado Forense" (carnaval 16, 17 e 18/02; Quinta e Sexta-feira Santa), "Feriado regimental" (11/08 Dia do Advogado, 08/12 Dia da Justiça) e "Ponto facultativo" (04/06 Corpus Christi, 06/08, 24 e 31/12 — estadual; 20/04 não aparece). O efeito de "ponto facultativo" sobre o prazo não é dito: DUVIDA.
  - Datas "adiadas": 20/01 Dia do Católico "comemoração adiada para o dia 22"; 28/10 Servidor "adiada para o dia 30"; 17/11 Tratado de Petrópolis "adiada para o dia 19". A linha da tabela está na data original e a nota fala da data transferida: DUVIDA qual vale para o expediente forense (o motor não deve inventar; registrar as duas).
  - Entradas em sábado/domingo aparecem na tabela (ex.: 08/03 domingo, 24/01 sábado): não alteram prazo útil.
  - O documento NÃO fala do recesso/suspensão de 20/12 a 20/01 (CPC art. 220): isso o motor teria de aplicar por regra fixa.
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2026-01-01, Confraternização Universal, Feriado Nacional (tabela JANEIRO, pág. 3).
  2. 2026-02-16, 17 e 18, Carnaval / Quarta-feira de Cinzas, Feriado Forense, art. 37 §1º II da LC 221/2010 (tabela FEVEREIRO, pág. 3).
  3. 2026-06-15, Aniversário do Estado do Acre, Feriado Estadual, Lei Estadual 14/1964 (tabela JUNHO, pág. 4).
  4. 2026-11-05, Aniversário do Município de Marechal Thaumaturgo, Feriado Municipal (tabela NOVEMBRO, pág. 6) [exemplo de local].
  5. 2026-12-28, Aniversário do Município de Rio Branco, Feriado Municipal, Lei Municipal 330/1981 (tabela DEZEMBRO, pág. 7) [exemplo de local].
- **Pode rodar na nuvem?** SIM. Saída literal (execução `testar-urls` nº 39986386976, 23/10/2026):
  `OK 200 293786 application/pdf 4.9 https://webdev.tjac.jus.br/wp-content/uploads/2025/12/Portaria_PRESI_TJAC_6569_2025.pdf`
- **Cobertura:** completa para o que o tribunal publica (nacional/estadual/forense + municipais citados na mesma tabela). Categoria: **pronto_para_motor**. Ressalvas: células multi-município, DUVIDAs de datas transferidas e de ponto facultativo, e recesso 20/12-20/01 não consta do ato. Se a Portaria for alterada durante o ano, a URL nova só aparece no site do tribunal (não há índice de alterações achado).
