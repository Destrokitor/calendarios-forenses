# Ficha do tribunal: TRF4

- **Nome:** Tribunal Regional Federal da 4ª Região (RS, SC, PR)
- **Justiça / regime(s) de contagem:** Federal; dias úteis; Lei 5.010/66.
- **Classificação: `pronto_para_motor`** (feriados e locais); suspensões avulsas só pela lista de avisos (ver ressalva).
- **Fonte(s) oficial(is):** portal único da 4ª Região, tabelas HTML estruturadas, uma por órgão (iso-8859-1):
  - TRF4 (sede, Porto Alegre): https://www.trf4.jus.br/trf4/controlador.php?acao=calendario_feriados_listar&selOrgao=1
  - Seção RS: ...&selOrgao=2 ; SC: ...&selOrgao=3 ; PR: ...&selOrgao=4 (colunas MÊS, DIA, SUBSEÇÃO/UAA, FERIADO, LEGISLAÇÃO, TIPO). Seletor de ano (2026, 2025...). Atualizado em 30/03/2026 (RS, SC) e 21/05/2026 (PR).
  - Página dos feriados locais: .../controlador.php?acao=pagina_visualizar&id_pagina=4435 (aponta Portaria 1064/2022 e as 4 tabelas).
  - Suspensões avulsas: lista de avisos https://www.trf4.jus.br/trf4/controlador.php?acao=aviso_listar (itens com rótulo "PRAZOS", ex.: 28/09 RS, 22/09 PR, 21-22/09 RS, 17/06 TRF4, 21/10 sistemas fora). Cada aviso é uma página/ato à parte.
- **Fixture(s) guardada(s):** tests/fixtures/trf4/ (calendario_feriados_selOrgao1_trf4.html, ...selOrgao2/3/4.html, pagina_feriados_locais_4435.html, avisos_listar_prazos_suspensos.html).
- **Como o calendário é publicado:** tabela HTML limpa, uma linha por data; "Todas" na coluna subseção = vale para a seção toda; dias em intervalo ("1º a 6", "16 a 17", "20 a 31"). Meses por extenso, "1º" com ordinal.
- **Locais:** RS ~212 linhas municipais, SC ~113, PR ~146 (contagem da palavra "Municipal"), por subseção/UAA (ex.: Porto Alegre, Caçador, Apucarana). Nomes como na fonte.
- **Particularidades:** a tabela do TRF4 (selOrgao=1) tem feriados do município sede (Navegantes 02/02, Corpus Christi 04/06) e estadual RS (20/09); campo TIPO distingue Nacional/Estadual/Municipal. Recesso 1-6/01 e 20-31/12 como "Nacional". Dia do Servidor 30/10 (Portaria 233/2026). Não lista pontos facultativos nem suspensões avulsas (estas só nos avisos, com texto livre: DUVIDA de tipo, suspensão de prazo x expediente). Corpus Christi aparece como feriado municipal por cidade, não geral. Decretos municipais de 2026 podem entrar (ex.: Caçador 23/03, Decreto 12.135/2026): a tabela muda ao longo do ano.
- **Âncoras conferidas à mão:**
  1. 2026-02-16 e 17: Carnaval, Nacional (todas) (selOrgao=2, linha "Fevereiro 16 a 17 Todas").
  2. 2026-09-20: Data Magna do Estado (RS), Estadual (selOrgao=1).
  3. 2026-10-30: Dia do Servidor Público, Portaria 233/2026 (todas, nas 4 tabelas).
  4. 2026-02-02: Nossa Sra. dos Navegantes e Iemanjá em Porto Alegre, Lei Mun. 13.591/2023 (selOrgao=2).
  5. 2026-01-28: Apucarana, aniversário da cidade, Decreto Mun. 16/2026 (selOrgao=4); 2026-03-23 Florianópolis emancipação (selOrgao=3).
- **Pode rodar na nuvem?** SIM. testar-urls run 39990169828 (GitHub, 23/10/2026), literal:
```
OK 200 14308 text/html; charset=iso-8859-1 1.8 https://www.trf4.jus.br/trf4/controlador.php?acao=calendario_feriados_listar&selOrgao=1
OK 200 40764 text/html; charset=iso-8859-1 1.1 https://www.trf4.jus.br/trf4/controlador.php?acao=calendario_feriados_listar&selOrgao=2
OK 200 27753 text/html; charset=iso-8859-1 1.0 https://www.trf4.jus.br/trf4/controlador.php?acao=calendario_feriados_listar&selOrgao=3
OK 200 32730 text/html; charset=iso-8859-1 0.7 https://www.trf4.jus.br/trf4/controlador.php?acao=calendario_feriados_listar&selOrgao=4
OK 200 61093 text/html; charset=iso-8859-1 1.2 https://www.trf4.jus.br/trf4/controlador.php?acao=aviso_listar
OK 200 14039 text/html; charset=iso-8859-1 0.6 https://www.trf4.jus.br/trf4/controlador.php?acao=pagina_visualizar&id_pagina=4435
```
  robots.txt do TRF4 só veda /trf4/processos/, /upload/ etc.; a rota controlador.php?acao=... não é vedada.
- **Cobertura:** completa para feriados + locais; suspensões avulsas = parcial (lista de avisos exige ler cada aviso).
