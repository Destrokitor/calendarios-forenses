# Ficha do tribunal: TRT2

- **Nome:** Tribunal Regional do Trabalho da 2ª Região (São Paulo, Grande SP e Baixada Santista)
- **Justiça / regime(s) de contagem:** Trabalhista. Dias úteis (CLT art. 775); suspensão 20/12 a 20/01 (art. 775-A). O TRT2 lança como "Recesso" só 01-06/01 e 20-31/12, e suspende prazos por portaria (21-23/01/2026).
- **Categoria:** **pronto_para_motor**
- **Fonte(s) oficial(is):**
  - Principal: https://ww2.trt2.jus.br/servicos/agenda/feriados-e-suspensoes-de-expediente (HTML, TYPO3 "calendarize"; calendário dos 12 meses de 2026 numa página só, SEM precisar de JavaScript: o texto de cada evento está no atributo `title` de cada dia). Atualizada por "Secretaria de Gestão Jurisprudencial, Normativa e Documental" (rodapé: "Atualizado em 19/08/2026").
  - Detalhe do dia (texto do ato e fundamento): `.../feriados-e-suspensoes-de-expediente/dia?tx_calendarize_calendar[action]=day&...[day]=D&...[month]=M&...[year]=2026` (link vem em cada `<a>` do dia). Traz "Portaria n. X/GP, de ...".
  - Normas (lista): link "Veja aqui" da página, https://basis.trt2.jus.br (não testado).
- **Fixture(s) guardada(s):** `tests/fixtures/trt2/feriados-suspensoes-2026.html` (página principal, baixada 23/10/2026); `dia-2026-01-22.html`, `dia-2026-02-18.html`, `dia-2026-04-20.html`, `dia-2026-06-29.html`, `dia-2026-07-13.html` (páginas de detalhe).
- **Formato:** HTML (texto, não PDF). Cada dia é `<td class="hasEvents">` com `<span class="label-calendar badge-XXX" title="Evento1 / Evento2 / ">` seguido de `<a href=...day%5D=D&month%5D=M&year%5D=2026>`. Os dias de "meses vizinhos" (classe `not-current-month`) repetem eventos: deduplicar por (data, texto).
- **Como o calendário é publicado (legenda do próprio site):** a cor (classe `badge-*`) separa os tipos:
  - `badge-secondary`: feriado nacional/estadual e dias sem expediente em TODA a jurisdição (ex.: "Feriado de Carnaval em todos os órgãos que integram o TRT da 2ª Região", "Suspensão de expediente em todos os órgãos...");
  - `badge-success`: feriado/aniversário MUNICIPAL ("Feriado religioso no Município de X", "Aniversário do Município de X");
  - `badge-info`: dia sem expediente em ÓRGÃO ESPECÍFICO ("Fórum Trabalhista de Cubatão", "12ª Vara do Trabalho de São Paulo", "Edifício Sede ..."): o texto curto não diz o efeito; o detalhe do dia diz (ver 13/07);
  - `badge-warning`: Recesso;
  - `badge-primary`: suspensão de prazo processual por portaria (21-23/01). Atenção: no mesmo dia pode haver várias cores; o texto "Suspensão dos prazos processuais" é o que manda.
  O site avisa: "Os dias assinalados não significam necessariamente suspensão dos prazos processuais. Cada evento deve ser consultado para verificar o órgão afetado". "A partir de 2019, o calendário registra apenas as suspensões de expediente/de prazo determinadas por ato normativo" (indisponibilidade de sistema fica em outro lugar: https://aplicacoes8.trt2.jus.br/sis/indisponibilidade/consulta, não lido).
- **Locais (municípios/órgãos):** 103 células com evento. Municípios citados pelo nome oficial ("Município de Guarujá", "Município de São Paulo (Sede)", etc.): cerca de 35 municípios (Corpus Christi lista 31). Órgãos: "Fórum Trabalhista de Cubatão/Arujá/Zona Sul/Zona Leste", "12ª Vara do Trabalho de São Paulo", "Edifício Sede". Não há lista fechada de locais no HTML (só os que têm evento). Para a lista de escolha do app, precisa de outra fonte ou aceitar só os que aparecem.
- **Particularidades / DUVIDA:**
  - Feriado municipal vale só no município (o site mostra "em órgãos especificados"); nunca aplicar ao tribunal inteiro.
  - Dia de Semana Santa: 01-05/04 todos "Feriado da Semana Santa em todos os órgãos" (inclui sáb/dom).
  - 18/02 (Quarta de Cinzas): "Suspensão de expediente [quarta-feira de Cinzas] (Portaria n. 50/GP...)". DUVIDA: expediente pleno suspenso ou parcial? O texto diz só "Suspensão de expediente"; o TRT2 não diz se o prazo corre. Tratar como `sem_expediente` só com decisão do revisor.
  - 20/04, 05/06, 10/07, 10/08, 07/12, 30/10 são "Suspensão de expediente"/"Antecipação"/"Transferência" por portaria: conta como `sem_expediente` (a fonte diz "dias sem expediente em toda a jurisdição" para cor secondary); o detalhe 20/04 diz só "Suspensão de expediente. (Portaria n. 50/GP, de 2 de outubro de 2025)".
  - 13/07 Cubatão (Portaria n. 17/GP.CR, de 13/07/2026): "Suspensão do expediente presencial, do atendimento presencial ao público e das audiências ... agendadas e não realizadas". DUVIDA: não diz que o prazo é suspenso (é processo eletrônico): NÃO tratar como suspensão de prazo, e sim como `parcial`/aviso local. Decisão do revisor.
  - Jogo da Copa (29/06): não há evento de TRT2 em 29/06 nesta agenda (só feriados religiosos de Praia Grande e Carapicuíba). Não inventar.
  - Recesso: grade mostra "Recesso" 01-06/01 e 20-31/12. 07-20/01 não aparece como suspensão (art. 775-A não é lançado pelo TRT2 como suspensão geral). DUVIDA para o revisor: o app aplica o art. 775-A por fora.
- **Âncoras conferidas à mão** (página principal e detalhe, 23/10/2026):
  1. **2026-02-16 e 2026-02-17**, "Feriado de Carnaval em todos os órgãos que integram o TRT da 2ª Região" (grade de fevereiro, `badge-secondary`).
  2. **2026-01-21, 22 e 23**, "Suspensão dos prazos processuais em todos os órgãos que integram o TRT 2ª Região", detalhe: "no período compreendido entre 21 e 23 de janeiro de 2026, com retomada de sua contagem a partir de 26 de janeiro de 2026 (Portaria n. 15/GP.CR, de 28 de outubro de 2025)" (`dia-2026-01-22.html`).
  3. **2026-04-20** "Suspensão de expediente em todos os órgãos" (Portaria n. 50/GP, de 2/10/2025) e **2026-04-21** "Feriado do Dia de Tiradentes em todos os órgãos" (`dia-2026-04-20.html`).
  4. **2026-06-04** "Feriado de Corpus Christi no Município de ..." em 31 municípios (local, não geral; São Paulo (Sede) está na lista) e **2026-06-05** "Suspensão de expediente em todos os órgãos" (grade de junho).
  5. **2026-12-20 a 2026-12-31** "Recesso" (e 01-06/01/2026 "Recesso"), `badge-warning` (grades de dezembro e janeiro). Âncora local: **2026-06-29** "Feriado religioso no Município de Praia Grande" e "... Carapicuíba" (Decreto-Lei n. 16/1967; Lei Municipal 3.215/2013), `dia-2026-06-29.html`.
- **Pode rodar na nuvem?** SIM para a página principal (run https://github.com/Destrokitor/calendarios-forenses/actions/runs/39986611463, conclusão `success`):
  ```
  OK 200 779673 text/html; charset=utf-8 5.3 https://ww2.trt2.jus.br/servicos/agenda/feriados-e-suspensoes-de-expediente
  ```
  Os links de detalhe (`.../dia?tx_calendarize_calendar%5Baction%5D=day&...`) NÃO foram provados na nuvem: o workflow `testar-urls` repassa a URL sem aspas ao shell e o `&` quebra a execução (1ª tentativa, run 39986467598, falhou por isso). Não precisa do detalhe para ler a lista; o detalhe só acrescenta a portaria/fundamento. Se o motor quiser o detalhe, precisa de teste próprio.
- **Cobertura:** completa para feriados nacionais/estaduais e suspensões gerais; completa para feriados municipais que o TRT2 registra; "órgãos específicos" só com o texto curto (efeito exige a página de detalhe).
