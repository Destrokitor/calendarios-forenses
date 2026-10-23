# Ficha do tribunal: STJ

- **Nome:** Superior Tribunal de Justiça
- **Justiça / regime(s) de contagem:** Superior (CPC; CPP art. 798). Recesso próprio (Emenda Regimental 16/2014).
- **Categoria:** `pronto_para_motor` (com ressalvas abaixo)
- **Fonte(s) oficial(is):**
  - Página "Horários de Funcionamento" (HTML, tabela Feriado | Datas | Fundamento legal; criada 2019, conteúdo de 2026 atualizado 04/02/2026): https://www.stj.jus.br/sites/portalp/Contato-e-ajuda/Fale-conosco/Horarios-de-funcionamento
  - O ato por trás: Portaria STJ/GP n. 1010/2025 (a notícia do STJ a chama de "STJ/GDG 1.010/2025"). PDF no BDJur: https://bdjur.stj.jus.br/server/api/core/bitstreams/6257b5ff-8c9d-408f-a7d5-c6d7064af8eb/content . Abre na nuvem (ver prova) mas deu 403 no meu computador, então NÃO tenho cópia nem conferi o texto do ato.
  - Comunicados de notícia (HTML) para dias avulsos, ex.: https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2026/16042026-Tribunal-nao-tera-expediente-nos-dias-20-e-21-de-abril.aspx
- **Fixture(s) guardada(s):** tests/fixtures/stj/horarios_funcionamento_2026.html, tests/fixtures/stj/noticia_20_21_abril_2026.html
- **Formato:** HTML (tabela de texto). Sem OCR.
- **Como o calendário é publicado:** uma tabela de 21 linhas na página acima; cada linha traz o nome, a data (ex.: "16 e 17 de fevereiro", "1º a 3 de abril", "20 de dezembro a 6 de janeiro") e o fundamento. Pontos facultativos aparecem na mesma tabela com fundamento "Ponto facultativo". A página não tem ano explícito nas datas (vale "para o ano de 2026" pela frase de abertura): a cada janeiro o motor precisa conferir que a frase cita o ano certo.
- **Locais (comarcas/foros/municípios):** nenhum (Brasília). `locais` = {}.
- **Particularidades:**
  - Ponto facultativo vira "sem expediente" no STJ: a notícia de 16/04/2026 diz "não terá expediente na segunda e na terça (20 e 21)", 20/4 por ponto facultativo; e "prazos observarão arts. 219, 224 e 231 CPC e 798 CPP" (ou seja, tratar como dia sem expediente com prorrogação).
  - Recesso: 20/12 a 6/1 (art. 2º Emenda Regimental 16/2014). A tabela NÃO fala de suspensão de prazos (20/12 a 20/1, CPC art. 220) nem de férias de julho: o STJ não publica essa parte na página. Para suspensão de prazo seria preciso outra fonte.
  - "Quarta-feira de Cinzas, 18 de fevereiro (até 14h)": linha de ponto facultativo; efeito parcial.
  - # DUVIDA: a tabela lista "Dia do Servidor Público, 28 de outubro, art. 236 da Lei 8.112" como feriado; noticiário secundário (Migalhas) diz ponto facultativo em 30/10. Não consegui ler a portaria. Resolver na revisão.
  - # DUVIDA: a linha "Independência do Brasil, 7 de dezembro, Ponto facultativo" tem rótulo claramente errado (7/12 é ponto facultativo; a Independência é 7/9). Motor deve ignorar o nome e usar só data + fundamento.
  - # DUVIDA: "Corpus Christi, 4 e 5 de junho, ponto facultativo" (ambos pontos facultativos).
  - Dia 30/11 (Dia do Evangélico) e 20/11 no DF: a página afirma que 30/11 NÃO é feriado no STJ; 20/11 (Consciência Negra) é feriado (Lei 14.759/2023).
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2026-02-16 e 2026-02-17, Carnaval: tabela, "Carnaval | 16 e 17 de fevereiro | Art. 81, § 2º, III, do RISTJ".
  2. 2026-04-01 a 2026-04-03, Semana Santa: tabela, "Semana Santa | 1º a 3 de abril | Art. 81, § 2º, III, do RISTJ".
  3. 2026-04-20 (ponto facultativo) e 2026-04-21 (Tiradentes): tabela e comunicado de 16/04/2026 ("não terá expediente ... dias 20 e 21").
  4. 2026-08-11 Criação dos Cursos Jurídicos e 2026-12-08 Dia da Justiça: tabela, art. 81 §2º IV RISTJ.
  5. 2026-12-20 a 2027-01-06, recesso forense: tabela, "Recesso Forense | 20 de dezembro a 6 de janeiro | Art. 2º da Emenda Regimental n. 16 de 19/11/2014". (Para jan/2026 vale 1 a 6/1.)
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 200 23254 text/html;charset=UTF-8 0.9 https://www.stj.jus.br/sites/portalp/Contato-e-ajuda/Fale-conosco/Horarios-de-funcionamento
OK 200 413716 application/pdf;charset=UTF-8 2.6 https://bdjur.stj.jus.br/server/api/core/bitstreams/6257b5ff-8c9d-408f-a7d5-c6d7064af8eb/content
```
```
gh run 39986812345 (testar-urls, conclusão: success)
OK 200 13761 text/html;charset=UTF-8 0.5 https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2026/16042026-Tribunal-nao-tera-expediente-nos-dias-20-e-21-de-abril.aspx
```
- **Pode rodar na nuvem?** Sim.
- **Cobertura:** feriados, pontos facultativos e recesso: completa. Suspensão de prazos (CPC 220) e dias avulsos: parcial (só por comunicados de notícia, sem lista própria).
