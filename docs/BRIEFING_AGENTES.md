# Roteiro para quem for fazer um motor (agente ou pessoa)

Leia antes: `README.md`, `robo/modelo.py` (o formato), `robo/motores/base.py`,
`docs/MOTOR_MODELO.py`, `docs/PROCESSO_MOTORES.md` e `docs/LEVANTAMENTO_TRIBUNAIS.md`.
Motor pronto de exemplo: `robo/motores/tjsp.py` (quando existir).

## Regras que NÃO se negociam
1. **Nada de IA** dentro do motor: só leitura determinística (regex, HTML, `pdftotext`).
2. **Nada de disfarce:** não mude o User-Agent (`robo/rede.py`), não use "stealth",
   proxy, CAPTCHA ou qualquer jeito de burlar bloqueio. Site que recusa o robô => relatar
   `incompativel`, com evidência. Procurar OUTRA fonte oficial do mesmo dado é permitido
   (Diário da Justiça, portaria em outro endereço, etc.).
3. **Nada que dependa do computador do dono.** O motor roda no GitHub Actions. Testar só
   no seu computador não vale: prove na nuvem (ver abaixo).
4. **Nenhum dado pessoal** nos arquivos (nomes de advogados, OAB, e-mails).
5. **Não invente data.** Dúvida sobre o EFEITO de um dia (feriado x suspensão de prazo x
   expediente parcial): comentário `# DUVIDA:` e registre na ficha. Quem revisa decide.
6. Cada dia tem `fonte` (id de uma entrada de `fontes`) e `motivo` copiado/resumido da fonte.

## Etapa 1: reconhecimento (modelo Sonnet)
Para cada tribunal designado:
1. Ache a(s) fonte(s) OFICIAL(is) do calendário/feriados/suspensões do ANO CORRENTE. Prefira
   ato normativo (provimento, portaria, resolução) a página de notícia.
2. Baixe uma cópia em `tests/fixtures/<sigla>/` (nome com ano; PDF, HTML ou TXT). Descreva a
   origem na ficha.
3. **Prove que a fonte abre na nuvem:**
   `gh workflow run testar-urls.yml -f urls="URL1 URL2"` e depois
   `gh run list --workflow testar-urls.yml --limit 1` / `gh run view <id> --log`.
   Anote o resultado literal na ficha.
4. Escreva `docs/fichas/<SIGLA>.md` (modelo: `docs/fichas/_FICHA_MODELO.md`), com 5 ÂNCORAS:
   datas conferidas À MÃO no ato (data, motivo, em que trecho do documento está).
5. Classifique o tribunal em UMA das categorias:
   - `pronto_para_motor`: fonte lida na nuvem e formato claro;
   - `incompativel`: nenhuma fonte oficial abre na nuvem (liste as URLs testadas e o erro);
   - `parcial`: dá para ler parte (explique o que fica de fora, ex.: feriados municipais
     só em portarias locais soltas).
6. NÃO escreva o motor nesta etapa.

## Etapa 2: o motor (modelo Haiku)
Recebe a ficha + fixture + este roteiro.
1. Copie `docs/MOTOR_MODELO.py` para `robo/motores/<sigla>.py` (sigla em minúscula).
2. Preencha `esperado` (`min_geral`, `min_locais`, `ancoras`, `exige_recesso`) com os números
   da ficha. Âncoras são obrigatórias.
3. Escreva `tests/test_<sigla>.py` (unittest) que lê a FIXTURE (sem rede) e confere: as
   âncoras, a contagem mínima, `validar(...) == []`, e um caso de local.
4. Rode: `python3 -W error -m unittest discover -s tests` até passar.
5. Se falhar 3 vezes no mesmo ponto, PARE e registre na ficha o que travou.

## Etapa 3: prova na nuvem e revisão (modelo Sonnet)
1. Commitar e `git push`; rode `gh workflow run testar-motor.yml -f sigla=<SIGLA>` e leia o
   resultado. Só vale se o status final for `verificado` ou `parcial`.
2. Confira 5 datas ALEATÓRIAS (além das âncoras) contra a fonte original.
3. Procure o que o teste não pega: dia parcial, feriado local aplicado ao tribunal inteiro,
   suspensão de prazo tratada como feriado, local com nome diferente do oficial.
4. Se o motor não consegue ler na nuvem: remova-o (ou nem crie) e inclua a sigla em
   `INCOMPATIVEIS` de `robo/registro.py` com a evidência.
5. Registre a linha em `docs/custos.md`.
