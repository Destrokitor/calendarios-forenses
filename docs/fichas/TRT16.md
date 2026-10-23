# Ficha do tribunal: TRT16

- **Nome:** Tribunal Regional do Trabalho da 16ª Região (Maranhão)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT 775), suspensão 20/12 a 20/01 (775-A).
- **Fonte(s) oficial(is):**
  - Calendário Institucional 2026, instituído pela Portaria GP nº 681/2025 (19/09/2025): PDF `https://www.trt16.jus.br/site/conteudo/calendario/arquivos/2025-09_arquivo-upload_calendario-institucional-2026.pdf`
  - Lista de feriados do mês (HTML, alimentada por banco, por município): `https://www.trt16.jus.br/site/conteudo/calendario/cieEvtListaFeriados.php` (a página do calendário `https://www.trt16.jus.br/calendario-institucional` é só um `<iframe>` para `.../site/conteudo/calendario/cieEvtPrincipal.php`).
  - Retificações: Portaria GP nº 759/2026 (Timon), divulgada por notícia `https://www.trt16.jus.br/noticias/trt-16-altera-calendario-dos-feriados-de-timon`. Suspensão nos feriados: Ato GP nº 7/2020.
  - Atos normativos ficam na Biblioteca Digital (`bibliotecadigital.trt16.jus.br`, DSpace/Angular com JavaScript; `robots.txt` proíbe `/search`): não serve para robô sem busca.
- **Fixture(s):** `tests/fixtures/trt16/calendario_institucional.html` (página-casca com o iframe), `noticia_calendario.html`, `noticia_timon.html`. NÃO há fixture do calendário (PDF e lista dão 403).
- **Como é publicado:** PDF (formato não verificado) e lista HTML por mês/município com campos DIA | TIPO | ABRANG. | MUNIC. | DESC. | LINK (pelo que a busca mostrou; não consegui abrir). Feriados locais e retificações (como Timon) entram por portaria do GP e atualizam a lista.
- **Locais:** municípios do MA com Vara (Timon, Imperatriz, Caxias, Bacabal, Açailândia, São João dos Patos...), segundo a busca.
- **Particularidades (informação de segunda mão, a conferir):** pontos facultativos 20/04, 05/06 e 07/12; transferências 28/07->27/07, 11/08->10/08 e 28/10->30/10. Nada disso foi lido no ato original.
- **Âncoras conferidas à mão:** NENHUMA no calendário. Só confere na fixture `noticia_timon.html`: Portaria GP 759/2026 inclui 04/10 (São Francisco de Assis) na VT de Timon (Decreto Municipal 746/2026) e exclui 15/10 de Timon. Isso não basta.
- **Pode rodar na nuvem?** NÃO para os dados. Run 39986139412 (GitHub Actions, 23/10/2026), literal:
  ```
  ERRO 403 https://www.trt16.jus.br/site/conteudo/calendario/arquivos/2025-09_arquivo-upload_calendario-institucional-2026.pdf
  ERRO 403 https://www.trt16.jus.br/site/conteudo/calendario/cieEvtListaFeriados.php
  OK 200 42844 text/html; charset=UTF-8 1.7 https://www.trt16.jus.br/calendario-institucional
  OK 200 47786 text/html; charset=UTF-8 1.4 https://www.trt16.jus.br/noticias/trt-16-altera-calendario-dos-feriados-de-timon
  ```
  Daqui também 403 (Apache "Forbidden") em tudo sob `/site/conteudo/calendario/`, inclusive o iframe `cieEvtPrincipal.php`. Só abrem páginas Drupal (casca do calendário e notícias), que não trazem as datas. Não tentei driblar.
- **Cobertura:** nenhuma.
- **Categoria: `incompativel`** (calendário PDF, lista HTML e iframe: 403 na nuvem). Possível rota futura: portaria 681/2025 no DEJT ou na Biblioteca Digital, mas a primeira não foi localizada e a segunda exige JavaScript.
