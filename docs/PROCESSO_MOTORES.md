# Como criar os motores gastando pouco: Haiku + Sonnet + Opus

Objetivo: 92 motores sem pagar preço de modelo grande em tarefa mecânica, e sem deixar um
modelo barato decidir o que é decisão jurídica. O robô da meia-noite **não usa IA**: o custo
de tokens existe só na construção e quando uma fonte muda de layout.

## Princípio

O que protege a qualidade não é o modelo, é o **contrato + testes + validação** (já prontos
em `robo/`). Um motor escrito por qualquer modelo só entra se passar nisso. Então:

| Etapa | Modelo | O que faz | Saída |
|---|---|---|---|
| 0. Fundação (uma vez) | Opus | contrato dos dados, validação, regras de regime, este processo | `robo/`, `docs/` |
| 1. Reconhecimento (por tribunal) | Sonnet | acha as fontes oficiais, baixa **uma cópia** para `tests/fixtures/`, descreve o formato, confere à mão 5 datas | `docs/fichas/<SIGLA>.md` |
| 2. Escrita do motor | Haiku | lê a ficha + fixture e escreve `robo/motores/<sigla>.py` até os testes passarem | motor + testes verdes |
| 3. Revisão | Sonnet | roda validação, confere amostra contra a fonte, procura o que o teste não pega (dia parcial, feriado x suspensão de prazo, local fora do padrão) | aprovado / devolve com apontamentos |
| 4. Escalada | Opus | só nos casos abaixo | decisão |

## Quando escalar para o Opus
- A fonte é ambígua sobre **efeito jurídico** (feriado local, suspensão só de um órgão,
  "ponto facultativo", expediente parcial).
- O Haiku falhou 3 vezes seguidas nos mesmos testes.
- Um regime de contagem tem controvérsia (falência, juizado criminal, eleitoral).
- A revisão do Sonnet achou divergência que ele não sabe resolver.

## Regras para gastar menos
1. **Fixture primeiro.** Quem faz o reconhecimento baixa a fonte uma vez e guarda. Ninguém
   mais acessa a internet para desenvolver; o Haiku trabalha só sobre arquivo local.
2. **Contexto mínimo.** Cada agente recebe: a ficha do tribunal, o trecho relevante da
   fixture e `robo/modelo.py`. Nada de repositório inteiro.
3. **Lote por padrão de fonte.** Tribunais que publicam do mesmo jeito (mesmo CMS, mesmo
   formato de PDF) são feitos em sequência: o motor do primeiro vira exemplo do resto.
4. **Testes escritos antes** (Sonnet, na etapa 1): âncoras conferidas à mão em
   `esperado["ancoras"]`. Um motor que "passa" sem âncora não vale.
5. **Medir.** Cada motor registra em `docs/custos.md` quem fez cada etapa e quantas
   tentativas levou. Depois de 5 motores, revisar se o Haiku está compensando; se o
   retrabalho passar do que se economiza, subir o piso para Sonnet.

## O que o Haiku NUNCA decide sozinho
Tipo do dia (`sem_expediente` x `suspensao_prazo` x `parcial`), abrangência (tribunal x
comarca) e qualquer regra de contagem. Em dúvida, ele marca `# DUVIDA:` no código e a revisão
resolve.

## Manutenção
O robô detecta mudança de layout porque a validação reprova (âncora ausente, poucos dias).
Um motor quebrado: baixar a nova fonte como fixture, Haiku tenta o conserto, revisão confere,
escala se falhar.
