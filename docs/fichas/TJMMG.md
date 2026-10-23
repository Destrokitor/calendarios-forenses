# Ficha do tribunal: TJMMG

- **Nome:** Tribunal de Justiça Militar do Estado de Minas Gerais
- **Justiça / regime(s) de contagem:** Militar estadual (CPPM/CPP; CPC subsidiário). Segue o calendário de feriados do TJMG (Belo Horizonte), conforme os próprios comunicados.
- **Categoria:** `parcial`
- **Fonte(s) oficial(is):** NÃO há calendário anual nem portaria de feriados 2026 do TJMMG no site. Cada dia sem expediente sai (a) no Diário da Justiça Militar Eletrônico (DJMe, sem endereço que eu tenha conseguido abrir) e (b) numa NOTÍCIA do portal (WordPress, com API pública JSON): https://tjmmg.jus.br/wp-json/wp/v2/posts?after=2025-10-15T00:00:00&per_page=100 (campos id, date, title, link, content). Os comunicados citam a base normativa: art. 313 da LC estadual 59/2001, Resolução TJMG 458/2004 e Portaria Conjunta TJMG 1.798/PR/2026 (consolida os feriados 2026 das comarcas de MG; 121 páginas; é ato do TJMG, deve ficar na ficha do TJMG; o TJMMG só a cita).
  - Posts de 2026 usados (id: título): 48130 Carnaval; 49125 Semana Santa; 49463 Tiradentes; 49717 Dia do Trabalho; 50204 Corpus Christi; 50536 e 50579 Copa (24 e 29/6, Portaria Conjunta 337/2026); 52005 Independência; 52496 N. Sra. Aparecida; 47401 e 47831 recesso 2025/26. Padrão do título: "TJMMG (não terá|suspende|altera) expediente ...".
- **Fixture(s) guardada(s):** tests/fixtures/tjmmg/noticias_expediente_2026.json (11 posts, JSON da API, campo `content` em HTML).
- **Formato:** texto livre dentro de notícia (HTML dentro de JSON). Datas em prosa ("de 1º a 3 de abril", "nos dias 4 e 5 de junho", "segunda-feira, 12"), sem estrutura. Dá para um motor por regex, mas é frágil e SÓ cobre dias já passados ou já anunciados (os avisos saem poucos dias antes). Dia de fim de ano de 2026 ainda não existe.
- **Locais:** um só (Belo Horizonte, onde ficam o Tribunal e as Auditorias). `locais` = {}.
- **Particularidades:**
  - Todo comunicado distingue: "não haverá expediente" + "prazos prorrogados para o primeiro dia útil" (= `sem_expediente`) e "alteração de horário" (= `parcial`: 11 a 13/2 expediente até 14h; 24/6 das 8h às 16h; 29/6 das 8h às 11h).
  - Recesso 20/12/2025 a 6/1/2026 (plantão), com suspensão de audiências, sessões e PRAZOS de 20/12 a 20/1; prazos retomados em 21/1 (posts 47401, 47831): `recesso` x `suspensao_prazo` são períodos diferentes.
  - 5/6/2026 sem expediente por Corpus Christi (post 50204: "dias 4 e 5"): na Portaria TJMG o 5/6 vale onde Corpus Christi é feriado municipal de BH. # DUVIDA: confirmar na Portaria Conjunta 1.798 como o dia 5/6 é classificado (sem_expediente ou suspensão).
  - Pontos facultativos que o TJMG adota (20/4, 30/10, 7/12) aparecem como "sem expediente" nos comunicados ("20 e 21 de abril, em razão do feriado de Tiradentes").
  - Dependência: as datas do TJMMG são as do TJMG/BH; quem fizer o motor do TJMG pode reaproveitar.
- **Âncoras conferidas à mão** (data, motivo, onde conferi):
  1. 2026-04-01 a 03, Semana Santa, sem expediente, prazos prorrogados: post 49125 ("não haverá expediente ... de 1º a 3 de abril").
  2. 2026-04-20 e 21, sem expediente (Tiradentes): post 49463.
  3. 2026-05-01, Dia do Trabalho: post 49717; 2026-09-07 Independência: post 52005.
  4. 2026-06-04 e 05, Corpus Christi, sem expediente: post 50204.
  5. 2025-12-20 a 2026-01-20: recesso e suspensão de prazos; recesso encerrado em 6/1; prazos retomados 21/1: posts 47401 e 47831.
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 200 303075 text/html; charset=UTF-8 2.9 https://tjmmg.jus.br/tjmmg-nao-tera-expediente-na-semana-santa/
OK 200 6359 application/json; charset=UTF-8 1.2 https://tjmmg.jus.br/wp-json/wp/v2/posts/49125
```
- **Pode rodar na nuvem?** Sim (portal e API JSON, HTTP 200).
- **Cobertura:** parcial. Não há lista anual; só comunicados por evento, em prosa. O que fica de fora: dias ainda não anunciados (recesso de dez/2026), pontos facultativos não divulgados em notícia, qualquer ato que só saia no DJMe.
