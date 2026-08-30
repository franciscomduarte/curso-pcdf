"""O agente extrator.

Neste ponto da unidade o "agente" ainda é simples: uma única passada
(percepção -> ação -> observação), sem loop de várias iterações. O loop
completo (ReAct) é a Aula 4.

Responsabilidades:
  - receber o texto bruto da ocorrência (percepção);
  - pedir a extração ao LLM plugado (ação);
  - validar e devolver a Ocorrencia (observação);
  - repetir com backoff se a chamada falhar (robustez mínima).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from .esquema import Ocorrencia
from .llm import ExtratorLLM, MockExtrator

logger = logging.getLogger("sigma.extrator")


@dataclass
class AgenteExtrator:
    llm: ExtratorLLM
    tentativas: int = 3
    espera_base: float = 1.5  # segundos; dobra a cada tentativa

    @classmethod
    def com_mock(cls) -> "AgenteExtrator":
        return cls(llm=MockExtrator())

    def processar(self, ocorrencia_id: str, texto: str) -> Ocorrencia:
        erro_final: Exception | None = None
        for tentativa in range(1, self.tentativas + 1):
            try:
                logger.info("extraindo %s (tentativa %d)", ocorrencia_id, tentativa)
                resultado = self.llm.extrair(texto)
                logger.info("%s -> %s", ocorrencia_id, resultado.natureza.value)
                return resultado
            except Exception as exc:  # rede, parsing, validação Pydantic...
                erro_final = exc
                logger.warning("%s falhou: %s", ocorrencia_id, exc)
                if tentativa < self.tentativas:
                    time.sleep(self.espera_base * 2 ** (tentativa - 1))
        raise RuntimeError(
            f"Extração de {ocorrencia_id} falhou após {self.tentativas} tentativas"
        ) from erro_final
