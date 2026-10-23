# Sonda de acesso (23/10/2026)

Medição de quais sites de tribunal respondem ao robô, a partir de um servidor do GitHub
(EUA), com o robô identificado (`Mozilla/5.0 (compatible; calendarios-forenses-robo/1.0; ...)`).

| Resultado | Quantos (dos 64 do escopo) |
|---|---|
| Respondem | 36 |
| HTTP 403 (recusam o robô) | 19 → marcados `incompativel` em `robo/registro.py` |
| Tempo esgotado / outro erro | 9 (TJAM, TJMS, TJRJ, TJRS, TRF3, TRF6, TRT6, TRT12, TRT23): a reavaliar |

Também testado: Chromium real (Playwright, sem disfarce) no GitHub. Não ajudou: continuou
bloqueado. Conclusão: o bloqueio é da origem (IP de nuvem americana) ou do tipo de cliente; o
projeto **não** usa técnicas de evasão (disfarce de User-Agent, "stealth", CAPTCHA).

Importante: "a página inicial responde" não prova que o CALENDÁRIO esteja acessível; cada
tribunal só deixa de ser `sem_motor` quando o motor dele lê o calendário de verdade, rodando
no GitHub (workflow `testar-motor`).

Reexecutar: `python3 scripts/sondar_dominios.py` (ou o workflow `sonda-de-dominios`).
