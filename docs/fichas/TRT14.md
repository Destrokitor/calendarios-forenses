# Ficha do tribunal: TRT14

- **Nome:** Tribunal Regional do Trabalho da 14ª Região (Rondônia e Acre)
- **Justiça / regime(s) de contagem:** Trabalho; dias úteis (CLT art. 775), suspensão 20/12 a 20/01 (art. 775-A).
- **Fonte(s) oficial(is):**
  - Ato: Portaria GP nº 1640, de 18/12/2025 (PROAD 7849/2025), relação de feriados nacionais, estaduais, municipais e regimentais de 2026 + pontos facultativos, com quadro anexo. PDFs:
    `https://files.trt14.jus.br/portal/public/feriados-2026-09/PROAD%207849-2025%20-%20DOC%2056.pdf` (versão atual, listada na página de feriados)
    `https://portal.trt14.jus.br/portal/sites/default/files/noticias-anexos-2026-02/PROAD%207849-2025%20-%20DOC%208%20calendario.pdf`
  - Calendário institucional 2026 (PDF): `https://files.trt14.jus.br/portal/public/calendario-2026-09/Calend%C3%A1rio%20-%202026%20-%20TRT-14%20%281%29.pdf`
  - Índice (HTML, só links): `https://portal.trt14.jus.br/portal/calendarios-institucionais/feriados`
- **Fixture(s) guardada(s):** `tests/fixtures/trt14/feriados_pagina.html` e `calendarios_institucionais.html` (só índices com os links; NÃO há fixture do ato: o PDF não baixa).
- **Como o calendário é publicado:** PDF (portaria + quadro anexo) em `files.trt14.jus.br`. A página HTML só lista links. Não consegui ver o conteúdo do PDF (nem daqui: 403), então formato do quadro (texto x escaneado) NÃO verificado.
- **Locais:** não verificado (o quadro anexo deveria trazer municípios de RO e AC).
- **Particularidades:** não verificado. Pela busca, a portaria traz recitais sobre prorrogação de prazo (CPC) em feriados e pontos facultativos.
- **Âncoras conferidas à mão:** NENHUMA. O ato não foi lido (bloqueado). Não invento datas.
- **Pode rodar na nuvem?** NÃO. Teste GitHub Actions (run 39986139412, 23/10/2026), literal:
  ```
  ROBOTS-NEGA https://files.trt14.jus.br/portal/public/feriados-2026-09/PROAD%207849-2025%20-%20DOC%2056.pdf
  ROBOTS-NEGA https://files.trt14.jus.br/portal/public/calendario-2026-09/Calend%C3%A1rio%20-%202026%20-%20TRT-14%20%281%29.pdf
  OK 200 67637 text/html; charset=UTF-8 1.9 https://portal.trt14.jus.br/portal/calendarios-institucionais/feriados
  ERRO 403 https://portal.trt14.jus.br/portal/sites/default/files/noticias-anexos-2026-02/PROAD%207849-2025%20-%20DOC%208%20calendario.pdf
  ```
  No meu computador também dá 403 (CloudFront "Request blocked") em `files.trt14.jus.br` (inclusive `/robots.txt`), em `www.trt14.jus.br/portal/sites/default/files/...` e no `portal.trt14.jus.br/...doc 8`. Só a página-índice HTML abre, e ela não tem datas.
- **Outras fontes tentadas:** DEJT (`dejt.jt.jus.br`) devolveu 599 daqui; não testado na nuvem nem exploradas as buscas de lá (provável formulário/JS). Possível 2ª tentativa: ato no DEJT-Adm.
- **Cobertura:** nenhuma.
- **Categoria: `incompativel`** (todas as URLs do ato: ROBOTS-NEGA/403 na nuvem; só índice HTML abre).
