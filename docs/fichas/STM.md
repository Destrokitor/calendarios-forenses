# Ficha do tribunal: STM

- **Nome:** Superior Tribunal Militar (Justiça Militar da União)
- **Justiça / regime(s) de contagem:** Militar da União, superior (CPPM; CPC subsidiário no que couber).
- **Categoria:** `incompativel`
- **Fonte(s) oficial(is):**
  - Calendário do STM 2026 (PDF, "versão de 6/11/2025", Secretaria do Tribunal Pleno), link na página inicial: https://www.stm.jus.br/images/servicos-e-sistemas/atendimento-ao-cidadao/calendario-oficial/calendario_2026_STM.pdf
  - Não achei ato normativo (resolução/ato) de 2026 com a lista de dias. O PDF cita só "Art. 66, § 2º, da LOMAN; Art. 44 do RISTM".
- **Fixture(s) guardada(s):** tests/fixtures/stm/calendario_2026_STM.pdf (baixada no meu computador).
- **Formato:** PDF com texto parcial: números dos dias e alguns nomes ("CARNAVAL", "TIRADENTES", "SEMANA SANTA"...) em caixas soltas, SEM data junto do nome. A CATEGORIA de cada dia (feriado, recesso, férias coletivas, sessão de início/encerramento) é só COR da célula (legenda: vermelho = Feriados Nacionais e na Justiça Militar da União; azul = Recesso; verde = Férias coletivas dos Ministros; amarelo = sessões de abertura/encerramento). Texto não basta; seria preciso ler a cor do vetor.
- **Locais:** nenhum. (As Auditorias/CJMs têm plantão em páginas próprias; não achei calendário local.)
- **Particularidades (lidas na imagem do PDF, não em texto):** vermelho: 16 e 17/2, 1 a 3/4, 21/4, 1/5, 7/9, 12/10, 1 e 2/11, 15/11 e 8/12; azul (recesso): 1 a 6/1 e 20 a 31/12; verde (férias): 7 a 31/1 e 2 a 31/7; amarelo (sessão de abertura/encerramento do ano judiciário): 2/2, 1/7, 3/8 e 18/12. Dias só em caixa, SEM cor: 4/6 (Corpus Christi), 18/2 (Cinzas), 28/10 (Servidor), 20/11 (Consciência Negra) e 30/11 (Bandeira).
  - # DUVIDA: o STM considera 4/6, 20/11 e 28/10 dias úteis? (só caixa, sem vermelho). Não há texto que diga.
  - # DUVIDA: não há menção a suspensão de prazo (CPC 220) nem a pontos facultativos.
- **Âncoras conferidas à mão** (olhando a imagem do PDF; sem texto de apoio):
  1. 2026-02-16 e 17: vermelho, caixa "CARNAVAL".
  2. 2026-04-01 a 03: vermelho, caixa "SEMANA SANTA"; 2026-04-21 vermelho "TIRADENTES".
  3. 2026-05-01 vermelho "Dia do TRABALHO"; 2026-09-07 vermelho "INDEPENDÊNCIA"; 2026-10-12 vermelho "N. Sra. APARECIDA".
  4. 2026-07-02 a 31: verde (férias coletivas dos Ministros); 2026-01-07 a 31 verde.
  5. 2026-12-20 a 31: azul (recesso do Tribunal); 2026-01-01 a 06 azul.
- **Prova na nuvem (GitHub Actions):**
```
gh run 39986601404 (testar-urls, conclusão: success)
OK 200 247 text/html; charset=utf-8 2.2 https://www.stm.jus.br/images/servicos-e-sistemas/atendimento-ao-cidadao/calendario-oficial/calendario_2026_STM.pdf
```
```
gh run 39986812345 (testar-urls, conclusão: success)
OK 200 247 text/html; charset=utf-8 1.4 https://www.stm.jus.br/
OK 200 247 text/html; charset=utf-8 0.6 https://www.stm.jus.br/robots.txt
```
  (A nuvem recebe 247 bytes de HTML, também para robots.txt, no lugar do PDF e da página inicial; no meu computador os mesmos endereços entregam o conteúdo normal. É resposta de proteção anti-robô; NÃO foi tentado contornar. Não consegui ver o corpo dessa resposta porque o script só imprime tamanho.)
- **Pode rodar na nuvem?** Não (HTTP 200 mas 247 bytes HTML, não PDF).
- **Cobertura:** nenhuma pela nuvem. Mesmo liberando, só leitura de cor do PDF.
