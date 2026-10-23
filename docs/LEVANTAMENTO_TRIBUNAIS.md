# Levantamento: tribunais e regimes de contagem de prazo (23/10/2026)

Pesquisa feita em busca aberta + leitura do provimento do TJSP. O que não consegui
confirmar em fonte está marcado **[não confirmado]**. Nada aqui substitui conferir a
norma atual antes de implementar cada regra.

## 1. Quantos tribunais

| Justiça | Tribunais | Observação |
|---|---|---|
| Superiores | 5 | STF, STJ, TST, TSE, STM |
| Estadual comum | 27 | 26 estados + DF (TJDFT) |
| Estadual militar | 3 | TJM de SP, MG e RS |
| Federal | 6 | TRF1 a TRF6 (o TRF6, de Minas, é o mais recente) |
| Trabalho | 24 | TRT1 a TRT24 |
| Eleitoral | 27 | um TRE por estado + DF |
| **Total** | **92** | CNJ contava 90 em 2018 (sem STF e sem o TRF6) |

Dentro de cada tribunal o calendário ainda varia por local: comarca (justiça estadual),
subseção/sede (justiça federal), vara/município (TRT). No TJSP são 318 comarcas com lista
oficial; o TJMG complementa com portarias locais de cada Diretor do Foro; o TRT2 diz que
feriado local só vale nos prédios daquele município.

Fonte central de feriados forenses: **não existe**. O CNJ só recomenda (Recomendação 44/2020)
que cada tribunal publique o seu calendário local até 19/12 do ano anterior.

## 2. Regimes que contam prazo de forma diferente do cível

Legenda "motor atual": o que o app faz hoje (dias úteis ou corridos, prazo em dobro,
recesso 20/12–20/01, feriados nacionais + estaduais + datas do usuário).

| Regime | Como conta | Fonte | O que falta no motor atual |
|---|---|---|---|
| **Cível (CPC)** | Dias úteis (art. 219), exclui o dia do começo, inclui o do vencimento; suspensão de 20/12 a 20/01 (art. 220) | CPC | calendário do tribunal |
| **Trabalhista** | Dias úteis (CLT art. 775); suspensão de 20/12 a 20/01 (art. 775-A, Lei 13.545/2017); TRTs podem estender (ex.: TRT9 e TRT2 em jan/2026) | Lei 13.545/2017; portarias dos TRTs | calendário por TRT e extensões do recesso. Prazo da Fazenda no trabalho (DL 779/69) **[não confirmado]** |
| **Penal** | Dias corridos, contínuos e peremptórios (CPP art. 798); não suspende por feriado ou domingo, só prorroga o último dia se cair em dia sem expediente | CPP art. 798 | modo "penal" (corridos, sem recesso, prorrogação do fim); regra de início (ex.: Súmula 310 STF) |
| **Juizado cível (estadual e federal)** | Dias úteis (Lei 9.099 art. 12-A, Lei 13.728/2018); Fazenda **sem** prazo diferenciado (Lei 12.153 art. 7º) | Lei 9.099; Lei 12.153 | desligar o dobro da Fazenda nesse regime |
| **Juizado criminal** | Tese majoritária nas fontes: segue o CPP (corridos); **controverso**, sem jurisprudência firme que eu tenha achado | doutrina | decisão explícita de qual tese adotar |
| **ECA** | Dias corridos (art. 152 §2º, Lei 13.509/2017); sem prazo em dobro para Fazenda e MP; STJ (HC 475.610) afastou o CPC; há julgado anterior em sentido diverso | ECA; STJ | modo ECA |
| **Falência e recuperação** | Texto legal: dias corridos (art. 189 §1º I, Lei 14.112/2020), mas TJSP, TJMS, TJSC e TJPR têm julgados com dias úteis para recurso — **divergência viva**, risco real de intempestividade | Lei 11.101 | decisão e aviso específico |
| **Eleitoral** | No período eleitoral os prazos são contínuos e peremptórios (inclui sábado, domingo e feriado); fora do período, regra geral do CPC. Contagem em **horas** em alguns atos **[não confirmado]**; numeração das resoluções do TSE precisa de conferência | LC 64/90; Res. TSE 23.608 | calendário eleitoral do ano e modo "contínuo" |
| **Execução fiscal, improbidade, MS** | Em geral CPC. Mandado de segurança tem decadência de 120 dias (prazo material, não processual) | — | prazos **materiais** (prescrição e decadência) são outra categoria; o app trata só prazo processual |

Regras transversais que mudam o resultado e o motor só cobre em parte:
- **Quem é a parte:** Fazenda Pública, MP e Defensoria têm prazo em dobro e início na intimação pessoal (CPC 180, 183, 186). Em ações objetivas do STF o dobro não vale (ADI 5814).
- **Como foi comunicado:** publicação no DJe, intimação pelo portal (prazo tácito de 10 dias corridos, Lei 11.419 art. 5º), citação, carga. Cada uma muda o dia em que o prazo começa.
- **Recesso e extensões:** cada tribunal pode estender (TRF3 teve dias de recesso de 2 a 6/02; TJMG tem "emendas" de feriado).

## 3. Como cada tribunal publica o calendário (amostra de 5)

| Tribunal | Formato | Observação |
|---|---|---|
| TJSP | Provimento CSM no DJE (texto) + edital com lista por comarca (texto) | lido sem IA; 318 comarcas; só 2 itens fora do padrão |
| TJMG | Portaria conjunta com anexo único + portarias de alteração + portarias locais | cobertura parcial provável nos municipais |
| TRF3 | PDF de calendário, atualizado ao longo do ano | a própria página avisa que nem todo dia marcado suspende prazo |
| TRT2 | Página de agenda com eventos por órgão afetado | precisa separar feriado de suspensão e o prédio afetado |
| TRT6 | Portaria da presidência em PDF | formato próprio |

Conclusão da amostra: cinco tribunais, cinco formatos. Cada um dos 92 precisa de um leitor
próprio e de uma validação.

## 4. Ordem sugerida de construção (para você decidir)

1. Motor de regimes (cível, trabalhista, juizado, penal, ECA) com as regras da seção 2 e
   aviso onde houver controvérsia.
2. Calendário ao vivo: TJSP (modelo), depois os outros TJs, TRFs, TRTs e superiores.
3. TREs e TJMs numa segunda leva.
4. Painel de cobertura por tribunal e comarca (verificado, parcial, indisponível).

## 5. Fontes consultadas
- Provimento CSM 2.813/2025 (TJSP): https://esaj.tjsp.jus.br/gcn-services/api/publico/origemnormaleg/arquivo/lXJ1041xK4/RY1PXz518K
- Lista de feriados municipais do TJSP (republicada): https://cnbsp.org.br/2025/11/25/dje-csm-divulga-edital-sobre-aprovacao-de-feriados-municipais-para-2026/
- TRF3, calendário: https://www.trf3.jus.br/documentos/seju/Feriados/2025/2026_-_calendario_de_feriados_-_at_25.06.2026.pdf
- TRT2, agenda: https://ww2.trt2.jus.br/servicos/agenda/feriados-e-suspensoes-de-expediente
- TJMG, Portaria Conjunta 1.798/2026: https://www8.tjmg.jus.br/institucional/at/pdf/pc17982026.pdf
- CNJ, calendário local (Rec. 44/2020): https://www.migalhas.com.br/quentes/338168/cnj--tribunais-devem-disponibilizar-calendario-de-feriados-locais-em-sites
- CLT 775-A (Lei 13.545/2017): https://www2.camara.leg.br/legin/fed/lei/2017/lei-13545-19-dezembro-2017-785959-publicacaooriginal-154551-pl.html
- Juizados e CPP: https://emporiododireito.com.br/leitura/a-contagem-dos-prazos-no-processo-penal-a-alteracao-na-lei-n-9-099-95
- ECA corridos (STJ HC 475.610): https://juris.damasio.com.br/jurisprudencia/julgado/647/prazos-no-eca-em-dias-corridos-inaplicavel-o-art-219-do-cpc-2015
- Falência (Lei 14.112/2020): https://www.migalhas.com.br/coluna/tendencias-do-processo-civil/355320/prazos-na-recuperacao-judicial-e-falencia
- Eleitoral: https://temasselecionados.tse.jus.br/temas-selecionados/registro-de-candidato/recurso/prazo/prazo-continuo-e-peremptorio
