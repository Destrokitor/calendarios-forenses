# Ficha do tribunal: TJPA

- **Nome:** Tribunal de Justiça do Estado do Pará
- **Justiça / regime(s) de contagem:** estadual comum; CPC. Art. 3º: prazos que expirarem em dia de suspensão seguem o art. 224 §1º do CPC.
- **Fonte(s) oficial(is):** Portaria nº 4765/2025-GP, de 20/10/2025 (DJe de 21/10/2025, ed. 8186): art. 1º "não haverá expediente ... nas datas definidas como feriados nacionais, estaduais e pontos facultativos, indicadas no Anexo único"; art. 2º transfere o ponto facultativo do Dia do Servidor de 28/10 para 30/10/2026. URL: https://www.tjpa.jus.br/CMSPortal/VisualizarArquivo?idArquivo=2234620
- **Fixture(s) guardada(s):** tests/fixtures/tjpa/portaria_4765_2025_gp.pdf (2 páginas)
- **Como o calendário é publicado:** **PDF ESCANEADO (imagem JPEG de 200 dpi, sem camada de texto)**: `pdftotext` devolve 2 caracteres e `pdfimages -list` mostra 2 imagens. Sem OCR não dá. Conferi à mão olhando as imagens. Não achei versão em texto (HTML ou DJe) desse ato; só tentei a busca na web e o portal, sem mais.
- **Locais (comarcas/foros/municípios):** o Anexo só tem datas gerais, uma exceção: 4 de junho Corpus Christi como "Feriado Nacional" com fundamento "Lei nº 9.093/95 c/c Lei Municipal nº 6306/67" (isto é, município de Belém). NÃO há feriados municipais do interior nem lista por comarca. 26/10 "Recírio" (Círio de Nazaré, ponto facultativo) também é local, sem dizer onde.
- **Particularidades:** Anexo por data: 01/01 feriado nacional; 16/02 ponto facultativo; 17/02 suspensão do expediente forense (Lei 1.408/1951); 18/02 ponto facultativo; 02/04 ponto facultativo; 03/04 feriado nacional; 20/04 ponto facultativo; 21/04 feriado nacional; 01/05; 04/06 Corpus Christi; 05/06 ponto facultativo; 07/09; 12/10; 26/10 Recírio, ponto facultativo; 30/10 Dia do Servidor, ponto facultativo; 02/11; 20/11; 07/12 ponto facultativo; 08/12 Dia da Justiça, feriado forense nacional. Não aparecem 25/12 nem recesso de fim de ano na tabela (a tabela termina em 08/12): DUVIDA.
- **Âncoras conferidas à mão** (olhando a imagem do Anexo, pág. 2):
  1. 2026-02-17, Carnaval, "Suspensão Nacional do Expediente Forense", Lei 1.408/1951.
  2. 2026-04-03, Sexta-feira Santa, Feriado Nacional.
  3. 2026-10-26, Recírio, ponto facultativo; 2026-10-30, Dia do Servidor, ponto facultativo (art. 2º transfere de 28/10).
  4. 2026-06-04, Corpus Christi, Feriado Nacional (Lei 9.093/95 c/c Lei Municipal 6306/67).
  5. 2026-12-08, Dia da Justiça, Feriado Forense Nacional.
- **Pode rodar na nuvem?** SIM abre; o problema é o formato. Saída literal (execução `testar-urls` nº 39986386976, 23/10/2026):
  `OK 200 442309 application/pdf 5.0 https://www.tjpa.jus.br/CMSPortal/VisualizarArquivo?idArquivo=2234620`
- **Cobertura:** nenhuma sem OCR. Categoria: **incompativel** (a única fonte achada abre na nuvem, mas é imagem escaneada e o projeto não usa OCR). Dá para o dono transcrever a tabela à mão uma vez por ano (19 linhas) ou achar o ato em texto no DJe do TJPA.
