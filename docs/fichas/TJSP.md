# Ficha do tribunal: TJSP

- **Nome:** Tribunal de Justiça do Estado de São Paulo (1º e 2º graus, Foro Judicial). Categoria: `pronto_para_motor`
  (cobertura `parcial` no sentido estrito: ver "O que fica de fora").
- **Regime de contagem:** CPC (dias úteis). Motor: `robo/motores/tjsp.py` (é o MOTOR MODELO dos demais).

## Fontes oficiais (todas abrem na nuvem; teste de 23/10/2026, workflow `testar-urls`, run 39987451512)

| id no motor | O que é | URL | Teste na nuvem |
|---|---|---|---|
| `portal` | Consulta pública "Expediente Forense/Suspensão de Prazos". A página monta as tabelas chamando 2 endereços JSON por comarca e ano | `https://www.tjsp.jus.br/CanaisComunicacao/Feriados/PesquisarFeriados?nomeMunicipio=Bauru&codigoMunicipio=0&ano=2026` e `.../PesquisarSuspensoes?...` (página: `.../Feriados/ExpedienteForense`) | `OK 200 2485 application/json 2.0` / `OK 200 7186 application/json 1.0` / página `OK 200 56625 text/html 1.2` |
| `comarcas` | Lista oficial das comarcas, por RAJ (321 itens, "Nome - 44ª CJ") | `https://www.tjsp.jus.br/QuemSomos/QuemSomos/RegioesAdministrativasJudiciarias` | `OK 200 72876 text/html 1.2` |
| (anos) | Anos disponíveis na consulta | `https://www.tjsp.jus.br/CanaisComunicacao/Feriados/ObterAnos` | `OK 200 709 text/html 1.0` |
| `provimento` | Provimento CSM 2.813/2025 (DJE 25/11/2025, Ed. 4334, 2 páginas) | `https://esaj.tjsp.jus.br/gcn-services/api/publico/origemnormaleg/arquivo/lXJ1041xK4/RY1PXz518K` | `OK 200 183920 application/octet-stream 2.4` |

robots.txt do tjsp.jus.br só barra /Segmento/, /Concursos/, /Handlers etc.: os endereços acima são permitidos
(conferido com `urllib.robotparser` e o User-Agent do robô).

**Os endereços JSON não estão documentados** (são os que a própria página chama; achados lendo o JavaScript da página).
Se o TJSP mudar a página, a validação reprova (âncoras, `min_locais`) e o robô marca `desatualizado`.

## Fixtures (`tests/fixtures/tjsp/`, guardadas em 23/10/2026)
- `provimento-csm-2813-2025.pdf`: o PDF do e-SAJ acima.
- `consulta-2026.json`: resposta real dos 2 endereços JSON para as 320 comarcas (chave = nome usado no portal).
- `comarcas-raj.html`: a página das RAJ. `anos.html`: resposta de `ObterAnos`.

## Como o calendário é publicado (e por que o motor lê o JSON, não só o PDF)
- O **provimento** (art. 1º) lista 18 dias sem expediente de 2026 em texto limpo; §1º traz o recesso (1 a 6/01 e 20 a 31/12);
  art. 2º, Quarta-feira de Cinzas (18/02) com atendimento a partir das 13h; o PDF de 2 páginas traz só o começo
  (A–B) da relação de feriados municipais. A lista completa (~318 comarcas) está só no DJE de 25/11/2025.
- A **consulta pública** tem os mesmos dias do provimento, MAIS os feriados municipais de cada comarca, MAIS o que
  mudou depois. Exemplo real: o provimento diz Dia do Servidor em **28/10**; a consulta traz **30/10**, "ALTERADO PELO
  PROVIMENTO CSM Nº 2845/2026" (não achei o texto desse provimento; confiei na página oficial do próprio tribunal).
  Por isso 28/10 **não** é âncora. Município: Bariri, Catanduva, Guarujá, Itajobi etc. também mudaram a data depois do edital.
- A consulta **não traz** o recesso de 20 a 31/12 nem a Quarta-feira de Cinzas: esses vêm do PDF (`pdftotext -layout`).
- Mistura dias do provimento e municipais numa só lista por comarca. O motor chama de GERAL a data presente em ≥ 90% das
  comarcas (não depende do texto "PROVIMENTO CSM"); o resto vai em `locais[COMARCA]`.

## Locais
- 320 comarcas em `locais` (321 da lista da RAJ, menos "Vila Mimosa", que a consulta pública não conhece). 13 ficam com lista
  vazia (feriados municipais iguais aos do provimento). 536 dias municipais no total.
- Nome = o do portal, maiúsculo, com acento (`normalizar_local`). Seis nomes da lista da RAJ têm grafia diferente da consulta
  e foram mapeados em `ALIAS_PORTAL` (ex.: Carapicuiba -> Carapicuíba, Santana do Parnaíba -> Santana de Parnaíba, São Luis ->
  São Luiz do Paraitinga, "Estrela D'Oeste" -> "Estrela dOeste"). O DJE grafa "Moji Guaçu" e "Ipauçu"; o portal e a RAJ, "Mogi Guaçu"
  e "Ipaussu": o motor usa a grafia do portal. Quem montar a lista de escolha do app deve usar essas chaves.
- Feriados municipais móveis (Sexta-Feira Santa, Corpus Christi, Carnaval da comarca) já vêm como data na consulta; quando
  coincidem com o dia do provimento, ficam só em `geral` (não repetem na comarca).

## Âncoras (conferidas à mão no PDF do provimento, art. 1º, e na consulta pública)
1. 2026-02-16 Carnaval (segunda).
2. 2026-02-17 Carnaval (terça).
3. 2026-04-02 Endoenças.
4. 2026-04-03 Sexta-feira da Paixão.
5. 2026-05-01 Dia do Trabalho. 6. 2026-11-20 Consciência Negra. 7. 2026-12-08 Dia da Justiça.
Recesso exigido (`exige_recesso`): 1 a 6/01 (consulta) e 20 a 31/12 (PDF). Os testes também conferem as datas móveis com o
algoritmo da Páscoa (`pascoa()` no motor): Carnaval = Páscoa-48/-47, Paixão = -2, Corpus Christi = +60.

## Conferência cruzada (cópia de terceiro, só conferência)
A relação do DJE copiada por cnbsp.org.br (317 linhas) foi comparada com o resultado do motor: 306 de 313 comarcas batem
exatamente; as 7 divergências são datas que o portal já corrigiu depois do edital (Bariri 16/06->15/06, Catanduva, Guarujá, Itajobi,
Nova Granada, Santa Fé do Sul, Urupês) e Campinas/Indaiatuba/Salto têm dia a mais no portal. Faltam 4 grafias (Ipauçu, Moji Guaçu,
Santa Rosa do Viterbo, Santana do Parnaíba), explicadas acima. O motor NÃO depende dessa cópia.

## Como o motor descobre o ano seguinte
- `ObterAnos` lista os anos com dados (hoje 2013–2026). Se o ano pedido não está, ou está mas com menos de 10 dias gerais
  (cadastro parcial) e é futuro: `AindaNaoPublicado`. O de 2027 deve aparecer por volta de nov/2026.
- O PDF do provimento NÃO tem endereço estável: o e-SAJ usa códigos aleatórios (`.../arquivo/<cod1>/<cod2>`) e não achei página de
  listagem nem API de busca que abra (testei `/gcn-services/api/publico/origemnormaleg` e `/gcn/`: 404). Quando sair o de 2027, quem
  revisa deve achar o link (portal do TJSP -> Normas, ou DJE de nov/2026, "Provimento CSM ... suspensão do expediente forense no
  exercício de 2027") e acrescentar em `PROVIMENTOS` no motor. **Sem ele o motor funciona**, mas o recesso de 20 a 31/12 entra como
  `suspensao_prazo` (CPC art. 220, fonte `cpc-220`) em vez de `recesso`, e a Quarta-feira de Cinzas fica de fora. REVISAR em nov/2026.

## Particularidades e dúvidas jurídicas (`# DUVIDA:` no código)
1. "Suspensão do expediente" (20/04, 05/06, 10/07, 07/12/2026): tem reposição de horas pelos servidores, mas o art. 1º diz "não
   haverá expediente": tipo `sem_expediente`.
2. 07 a 20/01: "Suspensão dos prazos processuais, art. 116 §2º do RITJSP": tipo `suspensao_prazo` (fórum abre, prazo não corre).
3. Quarta-feira de Cinzas (18/02/2026): atendimento a partir das 13h (art. 2º §2º): `parcial`, "a partir das 13h".
4. Dia parcial municipal (Andradina, 06/08: "a partir das 12 horas"): `parcial`, "a partir das 12h".
5. Feriado municipal: o tribunal só publica; eventual exigência de prova (CPC art. 1.003 §6º) é do advogado.
6. Dia do Servidor 28/10 -> 30/10 por provimento de 2026 que não li (ver acima).
7. Sem o provimento do ano, recesso de dezembro como `suspensao_prazo` (acima).

## O que fica de fora (`parcial` no motor)
- Suspensões de prazo de **unidades específicas** por comunicado conjunto (varas, anexos, juizados, UPJ, RAJ inteira em migração
  SAJ->eproc): vêm como texto livre, sem campo estruturado da unidade afetada. São ~36 comunicados em 2026. Lançá-los na comarca
  inteira suspenderia prazo de quem não foi afetado; ignorar é o erro seguro só se o app avisar. O app deve remeter o advogado à
  página oficial para varas em migração.
- Suspensões do 2º grau e de processos físicos (links da própria página), e indisponibilidade de sistemas (`/Indisponibilidade`).
- Município que não é sede de comarca (a consulta devolve vazio).
- Vila Mimosa (consta na lista da RAJ, sem calendário na consulta).

## Desempenho
O motor faz ~643 requisições (2 por comarca + 3) com a pausa padrão de 2 s do `Cliente`: ~22 minutos no GitHub Actions.
Sem timeout no `executar.py`, mas o job diário deve prever isso.

## Pode rodar na nuvem?
Sim, todas as fontes (tabela acima). `precisa_ip_brasil = False`. O motor precisa de `pdftotext` (poppler-utils; já instalado
nos workflows `robo` e `testar-motor`).
Prova do MOTOR inteiro na nuvem (`testar-motor.yml -f sigla=TJSP`) fica para a etapa 3 (depende do commit).

## Cobertura
Parcial (ver "O que fica de fora"). Geral em 2026: 51 dias = 18 do art. 1º do provimento (com o Dia do Servidor em 30/10) + 1 parcial (18/02) + 6 de recesso em janeiro + 12 de recesso em dezembro + 14 de suspensão de prazo (07 a 20/01), menos as sobreposições (07 e 08/12 já são do provimento).
