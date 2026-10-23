"""Descoberta automática: todo módulo em robo/motores/ que defina `MOTOR` é registrado."""
from __future__ import annotations

import importlib
import pkgutil
from typing import Dict

from .base import Motor


def descobrir() -> Dict[str, Motor]:
    motores: Dict[str, Motor] = {}
    for info in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if info.name == "base":
            continue
        modulo = importlib.import_module("%s.%s" % (__name__, info.name))
        motor = getattr(modulo, "MOTOR", None)
        if motor is not None:
            if motor.sigla in motores:
                raise RuntimeError("dois motores para %s" % motor.sigla)
            motores[motor.sigla] = motor
    return motores
