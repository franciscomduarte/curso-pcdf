"""Observabilidade mínima: métricas por serviço + o traço de uma investigação.

Três coisas que todo sistema em produção precisa e que a Aula 8 ainda não
tinha: quantas chamadas cada Service recebeu, quantas falharam, e quanto
tempo cada uma levou. É a base de qualquer painel real (Prometheus/Grafana),
sem nenhuma dependência externa — os números vêm do próprio `Cluster`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Metricas:
    chamadas: dict[str, int] = field(default_factory=dict)
    falhas: dict[str, int] = field(default_factory=dict)
    latencias_ms: dict[str, list[float]] = field(default_factory=dict)

    def registrar(self, servico: str, latencia_ms: float, ok: bool) -> None:
        self.chamadas[servico] = self.chamadas.get(servico, 0) + 1
        if not ok:
            self.falhas[servico] = self.falhas.get(servico, 0) + 1
            return
        self.latencias_ms.setdefault(servico, []).append(latencia_ms)

    def taxa_de_erro(self, servico: str) -> float:
        total = self.chamadas.get(servico, 0)
        if total == 0:
            return 0.0
        return self.falhas.get(servico, 0) / total

    def latencia_media_ms(self, servico: str) -> float:
        amostras = self.latencias_ms.get(servico, [])
        return sum(amostras) / len(amostras) if amostras else 0.0

    def latencia_p95_ms(self, servico: str) -> float:
        """Percentil 95 pelo método "nearest-rank": o menor valor tal que
        pelo menos 95% das amostras são iguais ou menores que ele."""
        amostras = sorted(self.latencias_ms.get(servico, []))
        if not amostras:
            return 0.0
        indice = max(0, math.ceil(len(amostras) * 0.95) - 1)
        return amostras[indice]

    def painel(self) -> str:
        linhas = [f"{'SERVICE':<22} {'CHAMADAS':>9} {'FALHAS':>7} {'ERRO%':>7} "
                  f"{'LAT.MÉDIA':>10} {'LAT.P95':>9}"]
        for servico in sorted(self.chamadas):
            linhas.append(
                f"{servico:<22} {self.chamadas[servico]:>9} {self.falhas.get(servico, 0):>7} "
                f"{self.taxa_de_erro(servico) * 100:>6.1f}% "
                f"{self.latencia_media_ms(servico):>8.1f}ms {self.latencia_p95_ms(servico):>7.1f}ms"
            )
        return "\n".join(linhas)


def formatar_traco(atendido_por: list[dict]) -> str:
    """O traço de UMA investigação — cada etapa, o pod que atendeu, a duração."""
    linhas = []
    for passo in atendido_por:
        linhas.append(f"  {passo['etapa']:<12} -> {passo['pod']:<28} {passo['duracao_ms']:.1f}ms")
    return "\n".join(linhas)
