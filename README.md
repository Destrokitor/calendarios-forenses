# calendarios-forenses

Calendários dos tribunais brasileiros (dias sem expediente, recessos e suspensões de
prazo), lidos todo dia das fontes oficiais e gravados em arquivos JSON abertos. Alimenta
o app **Calculadora de Prazos**, mas qualquer um pode usar os dados.

> **Aviso:** estes dados são uma conferência automática do que cada tribunal publicou, na
> data indicada em cada arquivo. Não substituem a consulta ao ato oficial nem os autos. A
> responsabilidade pelo prazo é de quem advoga.

## Como funciona

```
fontes oficiais ──► motores (um por tribunal) ──► validação ──► dados/<TRIBUNAL>/<ANO>.json
                                                      │                  dados/cobertura.json
                                                      └─ reprovou? mantém o dado anterior
                                                         e marca o tribunal "desatualizado"
```

- **Motores** (`robo/motores/`): cada um sabe ler a fonte de UM tribunal e devolve o
  calendário no formato de `robo/modelo.py`. Nenhum usa IA.
- **Validação** (`robo/validacao.py`): calendário lido pela metade, com data fora do ano,
  sem as datas-âncora conferidas à mão ou sem recesso **não é gravado**.
- **Cobertura** (`dados/cobertura.json`): para cada um dos 64 tribunais, o estado atual:
  `verificado`, `parcial`, `desatualizado`, `indisponivel`, `incompativel` (o site do tribunal
  recusa a consulta automática: o app avisa e sugere o cálculo simplificado) ou `sem_motor`, com a data da
  última leitura boa. O app mostra isso ao usuário. Nunca esconde falha.
- **Robô** (`robo/executar.py`): roda os motores e atualiza tudo.
- **Vigia** (`robo/vigia.py`): confere se os dados estão frescos; se não, o GitHub avisa por e-mail.

## Onde roda

Tudo na nuvem, nada depende do computador de ninguém.

- **GitHub Actions, todo dia às 01:00 (Brasília)** (`.github/workflows/robo.yml`): roda os
  motores, grava os dados e roda o vigia, que falha (com e-mail do GitHub) se os dados
  estiverem com mais de 2 dias.
- Alguns sites de tribunal podem bloquear o IP do GitHub (que fica nos EUA). Esses motores
  são marcados `precisa_ip_brasil = True` e rodam num servidor brasileiro na nuvem
  (`--grupo brasil`). Quais são: ver `docs/SONDA.md`, medido com `scripts/sondar_dominios.py`.

### Bloqueio de IP
O robô se identifica (`User-Agent` próprio), respeita `robots.txt`, faz uma requisição por
vez com pausa e não insiste depois de 401/403/404. Se uma fonte bloquear, a solução é achar
outra fonte oficial do mesmo dado, não disfarçar o robô.

## Comandos

```bash
python3 -m unittest discover -s tests      # testes
python3 -m robo.executar --so TJSP         # roda um tribunal
python3 -m robo.executar                   # roda todos
python3 -m robo.vigia                      # confere se está fresco
python3 scripts/sondar_dominios.py         # quais sites respondem daqui
```

## Estado

Esqueleto pronto (contrato de dados, validação, robô, vigia, agendamento, testes). Motores:
nenhum ainda; ver `dados/cobertura.json` e `docs/PROCESSO_MOTORES.md`. A lista dos 64
tribunais (sem Justiça Eleitoral, fora do escopo) e dos regimes de contagem está em `docs/LEVANTAMENTO_TRIBUNAIS.md`.
