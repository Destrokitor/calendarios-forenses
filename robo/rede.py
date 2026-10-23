"""Download educado: um robô que se identifica, respeita robots.txt e não martela o site.

Identifica-se como robô no formato padrão da web ("Mozilla/5.0 (compatible; nome; +url)", o mesmo de buscadores), que alguns filtros exigem; não finge ser navegador de pessoa. Se uma fonte bloquear, a solução é outra fonte
oficial do mesmo dado, não burlar o bloqueio (ver README, "Bloqueio de IP").
"""
from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional

from .robots import permitido as permitido_por_robots

AGENTE = "calendarios-forenses-robo"  # o nome que os robots.txt veem
USER_AGENT = "Mozilla/5.0 (compatible; calendarios-forenses-robo/1.0; +https://github.com/Destrokitor/calendarios-forenses)"


class ErroDeFonte(Exception):
    """A fonte não pôde ser lida (rede, bloqueio, robots.txt, resposta vazia)."""


class Cliente:
    def __init__(self, pausa: float = 2.0, tentativas: int = 3, timeout: int = 60, respeitar_robots: bool = True):
        self.pausa = pausa
        self.tentativas = tentativas
        self.timeout = timeout
        self.respeitar_robots = respeitar_robots
        self._ultimo_por_host: Dict[str, float] = {}
        self._robots: Dict[str, Optional[str]] = {}

    def _texto_robots(self, base: str) -> Optional[str]:
        """Conteúdo do robots.txt, ou None se "não disponível" (4xx): pela RFC 9309 isso
        libera o acesso. Levanta ErroDeFonte se o servidor falha (5xx/rede): a RFC manda
        assumir que tudo é proibido, e o robô obedece."""
        req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": USER_AGENT})
        ultimo: Optional[Exception] = None
        for tentativa in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as e:
                if 400 <= e.code < 500:
                    return None
                ultimo = e
            except (urllib.error.URLError, TimeoutError) as e:
                ultimo = e
            time.sleep(2)
        raise ErroDeFonte("robots.txt de %s indisponível (%s): por precaução não acesso" % (base, ultimo))

    def _permitido(self, url: str) -> bool:
        if not self.respeitar_robots:
            return True
        partes = urllib.parse.urlsplit(url)
        base = "%s://%s" % (partes.scheme, partes.netloc)
        if base not in self._robots:
            self._robots[base] = self._texto_robots(base)
        texto = self._robots[base]
        if texto is None:
            return True
        caminho = partes.path or "/"
        if partes.query:
            caminho += "?" + partes.query
        return permitido_por_robots(texto, AGENTE, caminho)

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
