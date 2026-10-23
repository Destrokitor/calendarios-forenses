# Ficha do tribunal: TRF1

- **Nome:** Tribunal Regional Federal da 1ª Região (DF, GO, TO, MT, BA, PI, MA, PA, AP, AM, AC, RO, RR, MG-fora; MG passou ao TRF6)
- **Justiça / regime(s) de contagem:** Federal; dias úteis (CPC); feriados forenses da Lei 5.010/66 art. 62.
- **Classificação: `incompativel`** (ver "Pode rodar na nuvem?").
- **Fonte(s) oficial(is):**
  - Portaria Presi 5/2026 (feriados nacionais e pontos facultativos 2026, TRF + todas as seções): https://www.trf1.jus.br/trf1/avisos/divulgados-os-feriados-nacionais-e-os-pontos-facultativos-no-ambito-da-1-regiao-em-2026 (HTML, texto do ato)
  - Notícia espelho: https://www.trf1.jus.br/trf1/noticias/confira-os-feriados-nacionais-e-pontos-facultativos-da-justica-federal-da-1-regiao-em-2026- (cita "Presi 5/2025" por erro de digitação; o ato é 5/2026)
  - Suspensões avulsas (Copa): Portaria Presi 368/2026 (24/06: expediente 9h-16h, audiências suspensas, prazos prorrogados) e Presi 380/2026 (29/06: ponto facultativo, prazos prorrogados) em /trf1/avisos/...
  - Feriados locais: NÃO são centralizados. Art. 2º da Presi 5/2026 remete ao Provimento Coger 10126799 e a portarias do diretor de foro de cada seção (ex.: SJBA-DIREF 30/2026). O PDF da SJBA fica em sistemas.trf1.jus.br/dspace e responde só uma página de aviso "disponível apenas na rede interna/VPN".
- **Fixture(s) guardada(s):** tests/fixtures/trf1/ (portaria_presi_5_2026_aviso.html, noticia_feriados_2026.html, sjba_aviso_portaria_diref_30_2026.html, portaria_presi_368_2026_copa_24jun.html, portaria_presi_380_2026_copa_29jun.html). Baixadas do meu computador (abrem aqui; NÃO é prova de nuvem).
- **Como o calendário é publicado:** texto em página HTML (lista I..XXII). Fácil de ler, se o robô pudesse.
- **Locais:** 13 seções (SJAC, SJAM, SJAP, SJBA, SJDF, SJGO, SJMA, SJMT, SJPA, SJPI, SJRO, SJRR, SJTO), cada uma com portaria própria; subseções por município sede. Sem lista única.
- **Particularidades:** feriado x ponto facultativo: 18/02 (até 14h), 20/04, 04/06 (Corpus Christi), 05/06, 10/08, 30/10 (transf. do 28/10), 07/12 são PONTO FACULTATIVO (não feriado). Recesso 20/12/2026-06/01/2027. Inciso XV falta na numeração do ato (XIV -> XVI). 01-06/01/2026 (recesso) vêm da portaria de 2025.
- **Âncoras conferidas à mão (Portaria Presi 5/2026, art. 1º):**
  1. 2026-02-16 e 17: Carnaval, feriado (inc. II).
  2. 2026-02-18: Quarta-feira de Cinzas, ponto facultativo até 14h (inc. III) -> dia parcial.
  3. 2026-04-01 a 03: Semana Santa, feriado (inc. IV).
  4. 2026-06-04: Corpus Christi, PONTO FACULTATIVO (inc. VIII) (no TRF6 é feriado: não confundir).
  5. 2026-12-20 a 2027-01-06: recesso forense (inc. XXI). Extra: 2026-06-29 ponto facultativo com prazos prorrogados (Presi 380).
- **Pode rodar na nuvem?** NÃO. Execução do testar-urls (run 39990127510, GitHub, 23/10/2026), literal:
```
ROBOTS-NEGA https://www.trf1.jus.br/trf1/avisos/divulgados-os-feriados-nacionais-e-os-pontos-facultativos-no-ambito-da-1-regiao-em-2026
ROBOTS-NEGA https://www.trf1.jus.br/trf1/noticias/confira-os-feriados-nacionais-e-pontos-facultativos-da-justica-federal-da-1-regiao-em-2026-
ROBOTS-NEGA https://www.trf1.jus.br/sjba/avisos/justica-federal-da-bahia-divulga-portaria-de-feriados-e-pontos-facultativos-para-2026
ROBOTS-NEGA https://www.trf1.jus.br/trf1/avisos/decretado-ponto-facultativo-...-copa-do-mundo-de-2026
ROBOTS-NEGA https://www.trf1.jus.br/trf1/avisos/portaria-dispoe-sobre-o-horario-...-copa-do-mundo-de-2026
OK 200 2201 text/html; charset=UTF-8 1.0 https://sistemas.trf1.jus.br/dspace/bitstream/123/410379/1/SEI_24392084_Portaria_SJBA_Diref_30.pdf   (2201 bytes = página "só rede interna/VPN", não o PDF)
```
  `https://www.trf1.jus.br/robots.txt` tem `User-agent: *` / `Disallow: /` (só buscadores nominais liberados). Regra 2: não burlar. Também: portal.trf1.jus.br/robots.txt deu 504 e sistemas.trf1.jus.br/ecalendario deu 403 (do meu computador).
- **Cobertura:** nenhuma pela via oficial aberta. Outra fonte oficial possível (não testada): Diário/DJe da Justiça Federal ou o e-Calendário (interno). Recomendação: `incompativel` com evidência acima; reavaliar se o TRF1 liberar robots.
