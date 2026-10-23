# Ficha do tribunal: TJMSP

- **Nome:** Tribunal de Justiça Militar do Estado de São Paulo
- **Justiça / regime(s) de contagem:** Militar estadual (CPPM/CPP; CPC subsidiário).
- **Categoria:** `incompativel`
- **Fonte(s) oficial(is) conhecidas (todas no domínio www.tjmsp.jus.br):**
  - Notícia "Calendário de feriados forenses de 2026 já está disponível" (01/12/2025): https://www.tjmsp.jus.br/2025/12/01/calendario-de-feriados-forenses-de-2026-ja-esta-disponivel/ , que remete ao Provimento nº 145/2025-AssPres (publicado no Diário da Justiça Militar de 28/11/2025).
  - Notícia "Recesso Forense 2025/2026" (09/12/2025): https://www.tjmsp.jus.br/2025/12/09/recesso-forense-2025-2026/
  - Página inicial e feed/RSS.
  - Procurei outra fonte oficial (Diário da Justiça Militar eletrônico em outro endereço): não achei; os subdomínios que testei (dje., www3., diario., esaj., eproc. de tjmsp.jus.br) não resolvem.
- **Fixture(s) guardada(s):** nenhuma. O site devolve 403 também no meu computador (todas as URLs acima, inclusive robots.txt), então não há cópia.
- **Formato:** desconhecido (não consegui abrir nada). Pelos resumos de busca, a notícia lista feriados em texto.
- **Locais:** desconhecido.
- **Particularidades (SÓ de resumo de busca, NÃO conferido por mim; não usar como dado):** o Provimento 145/2025-AssPres lista Carnaval 16 e 17/2, Endoenças 2/4, Sexta-feira Santa 3/4, Tiradentes 21/4, Trabalho 1/5, Corpus Christi 4/6, Data Magna paulista 9/7, Independência 7/9, N. Sra. Aparecida 12/10, Servidor 28/10, Finados 2/11, Consciência Negra 20/11, Justiça 8/12; "sem expediente" 20/4, 5/6, 10/7 e 7/12; 18/2 expediente começa 3h depois. Isso é calendário do TJSP quase igual, a ser conferido se um dia o site abrir.
- **Âncoras conferidas à mão:** nenhuma (não consegui ler a fonte).
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
ROBOTS-NEGA https://www.tjmsp.jus.br/
ROBOTS-NEGA https://www.tjmsp.jus.br/2025/12/01/calendario-de-feriados-forenses-de-2026-ja-esta-disponivel/
ROBOTS-NEGA https://www.tjmsp.jus.br/2025/12/09/recesso-forense-2025-2026/
ROBOTS-NEGA https://www.tjmsp.jus.br/feed/
```
  (O script trata o 403 de robots.txt como "robots nega" e não busca a página. Localmente: https://www.tjmsp.jus.br/ , /robots.txt , /feed/ , /wp-json/ e as duas notícias dão HTTP 403. Nada foi contornado.)
- **Pode rodar na nuvem?** Não.
- **Cobertura:** nenhuma.
