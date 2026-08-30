"""BROKER — despacha cada PEDIDO para o especialista com a capacidade certa.

Diferença para o pipeline: o broker não decide o fluxo, só roteia pedidos que
chegam (do usuário, de outros agentes, de uma fila). A lista de pedidos pode
vir fora de ordem ou incompleta — o broker resolve as dependências que
conseguir e devolve o que não deu.

    pedidos = ["classificar", "extrair", "revisar"]  ->  broker reordena pelo que cada um precisa
"""

from __future__ import annotations

from ..especialistas import REGISTRO, Dossie
from ..metricas import Metricas

# capacidade -> especialista
CAPACIDADES = {
    "extrair": "extrator",
    "classificar": "classificador",
    "enriquecer": "consultor",
    "revisar": "revisor",
}


class Broker:
    def __init__(self) -> None:
        self.registro = dict(REGISTRO)

    def orquestrar(self, d: Dossie, pedidos: list[str]) -> tuple[Dossie, Metricas]:
        m = Metricas(padrao="broker")
        fila = [CAPACIDADES[p] for p in pedidos if p in CAPACIDADES]
        pendentes = list(fila)
        progresso = True
        while pendentes and progresso:
            progresso = False
            for nome in list(pendentes):
                spec = self.registro[nome]
                if spec.precisa <= {k for k in ("campos", "classificacao") if d.tem(k)}:
                    d = spec.funcao(d, m)
                    m.rodadas += 1
                    pendentes.remove(nome)
                    progresso = True
        for nome in pendentes:
            d.pendencias.append(f"broker não pôde despachar '{nome}' (dependência não satisfeita)")
        return d, m


def orquestrar(d: Dossie, pedidos: list[str] | None = None) -> tuple[Dossie, Metricas]:
    return Broker().orquestrar(d, pedidos or ["classificar", "extrair", "enriquecer", "revisar"])
