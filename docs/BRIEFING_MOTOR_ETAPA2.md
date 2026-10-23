# Etapa 2: escrever o motor de UM tribunal (leia inteiro)

Contexto: repositório /Users/pedro/calendarios-forenses, robô Python 3.9 (sem IA) que lê calendários
de tribunais no GitHub Actions. Português nos comentários. Regras inegociáveis: `docs/BRIEFING_AGENTES.md`.

## Leia nesta ordem
1. `docs/BRIEFING_AGENTES.md` (regras), `robo/modelo.py` (formato), `robo/motores/base.py`, `robo/validacao.py`.
2. Motores prontos para imitar (estilo e estrutura): `robo/motores/tjsp.py` (o grande), `robo/motores/tjdft.py` e
   `robo/motores/trt24.py` (HTML), `robo/motores/tjrr.py` e `robo/motores/tjse.py` (PDF), com os testes
   `tests/test_<sigla>.py`.
3. A ficha do tribunal em `docs/fichas/<SIGLA>.md` (fonte, formato, âncoras, dúvidas) e as fixtures em
   `tests/fixtures/<sigla>/`.

## O que criar (SÓ isto)
- `robo/motores/<sigla>.py` com `MOTOR = ...` no fim; `tests/test_<sigla>.py`.
- Se a ficha classifica o tribunal como `incompativel` mas a instrução da tarefa diz que o robots.txt foi corrigido,
  atualize só a linha de categoria da ficha.
- NÃO edite nenhum outro arquivo. NÃO faça git commit/push. NÃO acesse a internet (trabalhe sobre as fixtures; PDFs:
  `pdftotext -layout` por subprocess; `-bbox` se precisar de colunas).

## Como
- Separe `baixar` (usa `rede.baixar(url)`, URL da ficha) de `interpretar(conteudo, ano)` (puro, testável).
- Cada dia: `fonte` válida (entrada em `fontes`), `motivo` do documento, tipo só de `modelo.TIPOS`
  (parcial exige `horario`). Intervalos ("20 a 31/12") viram um Dia por data. Nome de local com `normalizar_local`.
- Efeito jurídico de um dia (feriado x suspensão de prazo x ponto facultativo): siga a decisão da ficha; sem decisão,
  o mais conservador (NÃO inventar suspensão de prazo) + comentário `# DUVIDA:`. Nunca invente data.
- `esperado`: `min_geral`, `min_locais`, `ancoras` (da ficha, em `geral`), `exige_recesso` (True só se o ato traz recesso).
  A ficha pode não trazer contagem: use o que você leu, um pouco abaixo, e diga isso na entrega.
- Cobertura incompleta (ex.: feriados municipais não listados; alterações posteriores não lidas): descreva exatamente
  o que fica de fora no atributo `parcial` do motor.
- Ano que a fonte não cobre: levante `AindaNaoPublicado` (não é falha). O padrão `anos()` pede ano corrente e o seguinte.
- Fonte com endereço que muda por ano/edição: registre na ficha como localizar a do próximo ano (ou diga que não achou).

## Testes
`tests/test_<sigla>.py` (unittest): lê só a fixture; confere âncoras, contagem mínima, `validar(...) == []`, um caso de
local e um caso parcial/suspensão se existir. Rode `python3 -W error -m unittest discover -s tests` até TUDO passar.
Cuidado: uma data pode ter dois registros (feriado + recesso); não guarde por dicionário de data.
Se falhar 3 vezes no mesmo ponto, PARE e escreva no fim da ficha a seção "Travou em:".

## Entrega (≤ 10 linhas)
Arquivos criados; nº de dias gerais/locais lidos; âncoras conferidas; o que ficou fora; tentativas até os testes passarem;
qualquer ponto em que você NÃO tem certeza do efeito jurídico.
