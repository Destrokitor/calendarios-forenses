# Ficha do tribunal: TRF6

- **Nome:** Tribunal Regional Federal da 6ª Região (Minas Gerais)
- **Justiça / regime(s) de contagem:** Federal; dias úteis; Lei 5.010/66.
- **Classificação: `incompativel`** a partir do GitHub (EUA): tempo esgotado em todos os hosts do TRF6. A fonte em si é a melhor do grupo (ato único com locais); candidato a `precisa_ip_brasil`.
- **Fonte(s) oficial(is):**
  - Portaria Presi 1/2026 (feriados e pontos facultativos 2026 do 1º e 2º graus + feriados municipais com fechamento por subseção): https://portal.trf6.jus.br/wp-content/uploads/2026/01/SEI_1571312_Portaria_Presi_1.pdf (PDF com texto, 5 páginas).
  - Página: https://portal.trf6.jus.br/calendario-2/ (aponta a portaria e o calendário ilustrado https://portal.trf6.jus.br/wp-content/uploads/2026/03/Calendario-TRF6-2026-Feriados-locais-1.pdf, 22 MB, texto extraível 53 mil caracteres; NÃO guardado por tamanho).
  - Suspensões avulsas (ex.: Juiz de Fora, Portaria Disub 1/2026, 24-25/02): avisos em https://sjmg.trf6.jus.br/category/avisos/ (não lido).
- **Fixture(s) guardada(s):** tests/fixtures/trf6/ (portaria_presi_1_2026.pdf, calendario_pagina.html, noticia_calendario_2026.html). Baixadas do meu computador (lá abre; NÃO é prova de nuvem).
- **Como o calendário é publicado:** PDF com texto; lista numerada (art. 1º, I a XX) e art. 2º com "Em <cidade>" seguido de linhas "dia de mês: motivo". Muito regular.
- **Locais:** ~28 cidades no art. 2º (Belo Horizonte, Divinópolis, Governador Valadares, Ipatinga, Ituiutaba, Janaúba, Juiz de Fora, Lavras, Manhuaçu, Montes Claros, Muriaé, Paracatu, Passos, Patos de Minas, Poços de Caldas, Ponte Nova, Pouso Alegre, São João del-Rei, São Sebastião do Paraíso, Sete Lagoas, Teófilo Otoni, Uberaba, Uberlândia, Unaí, Varginha, Viçosa...). Nomes como na portaria.
- **Particularidades:** Corpus Christi 04/06 é FEICHADO como feriado religioso (Lei Mun. BH 11.397/2022) em toda a 6ª Região (diferente do TRF1/TRF5, onde é ponto facultativo). Ponto facultativo: 18/02 (até 14h), 20/04, 05/06, 10/08, 30/10 (transf. do 28/10), 07/12. Recesso 1-6/01 e 20-31/12. A portaria foi assinada pelo Vice-Presidente em exercício.
- **Âncoras conferidas à mão (Portaria Presi 1/2026):**
  1. 2026-02-16 e 17: Carnaval, feriado (art. 1º II); 18/02 ponto facultativo até 14h (III).
  2. 2026-06-04: Corpus Christi, feriado religioso (art. 1º VIII).
  3. 2026-08-15: Assunção de N. Senhora em Belo Horizonte (art. 2º; sábado).
  4. 2026-01-30: aniversário de Governador Valadares; 2026-06-01 São Firmino em Divinópolis (art. 2º).
  5. 2026-12-20 a 31: recesso forense (art. 1º XX).
- **Pode rodar na nuvem?** NÃO. testar-urls run 39990199502 e retentativa run 39991707556 (GitHub, 23/10/2026), literal:
```
ROBOTS-INDISPONIVEL robots.txt de https://portal.trf6.jus.br indisponível (<urlopen error timed out> https://portal.trf6.jus.br/calendario-2/
ROBOTS-INDISPONIVEL robots.txt de https://portal.trf6.jus.br indisponível (<urlopen error timed out> https://portal.trf6.jus.br/wp-content/uploads/2026/01/SEI_1571312_Portaria_Presi_1.pdf
ROBOTS-INDISPONIVEL robots.txt de https://portal.trf6.jus.br indisponível (<urlopen error timed out> https://portal.trf6.jus.br/trf6-divulga-calendario-institucional-de-2026-...
ROBOTS-INDISPONIVEL robots.txt de https://sjmg.trf6.jus.br indisponível (<urlopen error timed out>): https://sjmg.trf6.jus.br/category/avisos/
ROBOTS-INDISPONIVEL robots.txt de https://www.trf6.jus.br indisponível (<urlopen error timed out>):  https://www.trf6.jus.br/
```
  Do meu computador (Brasil) tudo responde 200 e os robots.txt permitem (`Disallow:` vazio). Ou seja: o bloqueio é da origem (IP de nuvem americana).
- **Cobertura:** completa para feriados + locais se rodar com IP brasileiro (`precisa_ip_brasil = True`); suspensões avulsas só pelos avisos.
