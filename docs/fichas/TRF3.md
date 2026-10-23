# Ficha do tribunal: TRF3

- **Nome:** Tribunal Regional Federal da 3ª Região (SP e MS)
- **Justiça / regime(s) de contagem:** Federal; dias úteis; Lei 5.010/66.
- **Classificação: `incompativel`** a partir do GitHub (EUA): robots.txt e arquivos dão tempo esgotado. Conteúdo seria `parcial` (ver abaixo); candidato a `precisa_ip_brasil` se houver runner brasileiro.
- **Fonte(s) oficial(is):**
  - Página índice "Feriados e Suspensões de expedientes": https://www.trf3.jus.br/seju/calendario-dos-feriados (lista os atos por ano: Portaria CATRF3R 48/2025 = expediente 2026; Port. 53/2026 = suspensão de prazos e expediente presencial em 02/03/2026; demais suspensões entram aqui).
  - Calendário PDF 2026 (grade mensal, com a portaria de cada data, atualizado até 25/06/2026): https://www.trf3.jus.br/documentos/seju/Feriados/2025/2026_-_calendario_de_feriados_-_at_25.06.2026.pdf
  - Feriados das subseções SP: Portaria DFORSP 338/2026 (Diretor do Foro SP, 16/01/2026): https://www.jfsp.jus.br/documentos/subsecoes/assis/atos-normativos/Portaria_DFORSP_338-2026.pdf (conteúdo não lido: não abre daqui). MS: portaria do JFMS não localizada.
- **Fixture(s) guardada(s):** tests/fixtures/trf3/calendario_feriados_2026_atualizado_24.02.2026.pdf e pagina_feriados_e_suspensoes_wayback_20260509.html. ATENÇÃO: cópias do Internet Archive (snapshot 09/05/2026) do PDF oficial; os endereços oficiais dão tempo esgotado no meu computador também, então a versão de 25/06/2026 (com os jogos da Seleção, Port. 56/57) NÃO foi obtida.
- **Como o calendário é publicado:** PDF com texto, mas em grade de calendário (3 meses lado a lado; as notas de cada mês saem misturadas no pdftotext; precisaria ler por colunas/bbox). Índice em HTML com links para portarias em PDF.
- **Locais:** o PDF é do TRF/SP capital (traz 25/01 aniversário de São Paulo e 09/07). Subseções SP e MS: portarias do diretor de foro de cada seção (SP: DFORSP 338/2026; MS: não achei).
- **Particularidades:** o site avisa que nem todo dia marcado suspende prazo. Distinguir: "Feriado Legal", "Não haverá expediente" (05/06, 20/04), "Suspensão dos prazos processuais e do expediente presencial" (02/03), e jogos da Seleção (expediente alterado; ver portarias 56/57 de junho). Recesso: 02-06/01 e 20-31/12; 24 e 31/12 por Port. 48.
- **Âncoras conferidas à mão (PDF de 24/02/2026):**
  1. 2026-01-25: Aniversário da cidade de São Paulo (local, SP capital).
  2. 2026-03-02: Suspensão dos prazos processuais e do expediente presencial (Port. CATRF3R 53, 20/02/2026) -> tipo suspensao_prazo.
  3. 2026-04-01 e 02: Feriado Legal (Port. CATRF3R 48/2025); 03/04 Sexta-Feira Santa.
  4. 2026-06-04: Corpus Christi; 2026-06-05: "Não haverá expediente" (Port. 48).
  5. 2026-07-09: Revolução Constitucionalista (estadual SP). Extras: 20/04 sem expediente; 11/08 feriado legal; 30/10 Dia do Servidor (originalmente 28/10); 24 e 31/12 pela Port. 48.
- **Pode rodar na nuvem?** NÃO. testar-urls run 39990156689 e retentativa run 39991721519 (GitHub, 23/10/2026), literal:
```
ROBOTS-INDISPONIVEL robots.txt de https://www.trf3.jus.br indisponível (The read operation timed out https://www.trf3.jus.br/documentos/seju/Feriados/2025/2026_-_calendario_de_feriados_-_at_25.06.2026.pdf
ROBOTS-INDISPONIVEL robots.txt de https://www.trf3.jus.br indisponível (The read operation timed out https://www.trf3.jus.br/seju/calendario-dos-feriados
ROBOTS-INDISPONIVEL robots.txt de https://www.jfsp.jus.br indisponível (The read operation timed out https://www.jfsp.jus.br/documentos/subsecoes/assis/atos-normativos/Portaria_DFORSP_338-2026.pdf
```
  Do meu computador: curl para www.trf3.jus.br e www.jfsp.jus.br também falha (código 000/28, timeout), mesmo com HTTP/1.1 e 120s. Sinal de bloqueio/lentidão por origem; sem disfarce (regra 2).
- **Cobertura:** se houver IP brasileiro: parcial (TRF + SP capital pelo PDF; subseções SP pela DFORSP 338; MS indefinido; suspensões avulsas pela página índice, cada uma um PDF).
