"""Download educado: um robô que se identifica, respeita robots.txt e não martela o site.

Não disfarça o robô de navegador. Se uma fonte bloquear, a solução é outra fonte
oficial do mesmo dado, não burlar o bloqueio (ver README, "Bloqueio de IP").
"""
from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from typing import Dict, Optional

USER_AGENT = "calendarios-forenses-robo/1.0 (+https://github.com/Destrokitor/calendarios-forenses)"


class ErroDeFonte(Exception):
    """A fonte não pôde ser lida (rede, bloqueio, robots.txt, resposta vazia)."""


class Cliente:
    def __init__(self, pausa: float = 2.0, tentativas: int = 3, timeout: int = 60, respeitar_robots: bool = True):
        self.pausa = pausa
        self.tentativas = tentativas
        self.timeout = timeout
        self.respeitar_robots = respeitar_robots
        self._ultimo_por_host: Dict[str, float] = {}
        self._robots: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}

    def _permitido(self, url: str) -> bool:
        if not self.respeitar_robots:
            return True
        partes = urllib.parse.urlsplit(url)
        base = "%s://%s" % (partes.scheme, partes.netloc)
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(base + "/robots.txt")
            try:
                rp.read()
                self._robots[base] = rp
            except Exception:  # sem robots.txt legível: segue, é o comportamento padrão da web
                self._robots[base] = None
        rp = self._robots[base]
        return True if rp is None else rp.can_fetch(USER_AGENT, url)

    def _esperar(self, url: str) -> None:
        host = urllib.parse.urlsplit(url).netloc
        agora = time.monotonic()
        ultimo = self._ultimo_por_host.get(host)
        if ultimo is not None and agora - ultimo < self.pausa:
            time.sleep(self.pausa - (agora - ultimo))
        self._ultimo_por_host[host] = time.monotonic()

    def baixar(self, url: str) -> bytes:
        if not self._permitido(url):
            raise ErroDeFonte("robots.txt não permite baixar %s" % url)
        ultimo_erro: Optional[Exception] = None
        for tentativa in range(self.tentativas):
            self._esperar(url)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    corpo = resp.read()
                if not corpo:
                    raise ErroDeFonte("resposta vazia de %s" % url)
                return corpo
            except urllib.error.HTTPError as e:
                ultimo_erro = e
                if e.code in (401, 403, 404, 410):  # insistir não adianta e parece ataque
                    break
            except (urllib.error.URLError, TimeoutError, ErroDeFonte) as e:
                ultimo_erro = e
            time.sleep(2 ** tentativa)
        raise ErroDeFonte("não consegui baixar %s: %s" % (url, ultimo_erro))
