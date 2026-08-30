"""As funções de consulta que o servidor MCP expõe como ferramentas.

São funções Python comuns e puras (só leem as bases sintéticas). O servidor é
quem decide se elas podem ser chamadas, por quem, e registra o acesso.
"""

from __future__ import annotations

from .bases_sinteticas import DOCUMENTOS, OCORRENCIAS_HISTORICO, VEICULOS
from .esquema import FerramentaSpec, ParametroSpec


def consultar_veiculo(placa: str) -> dict:
    """Consulta uma placa na base fictícia de veículos."""
    dados = VEICULOS.get(placa.strip().upper())
    if not dados:
        return {"placa": placa, "encontrado": False}
    return {"placa": placa.upper(), "encontrado": True, **dados}


def consultar_ocorrencias_similares(natureza: str, regiao: str, dias: int = 15) -> list[dict]:
    """Ocorrências fictícias da mesma natureza e região nos últimos N dias."""
    n, r = natureza.strip().lower(), regiao.strip().lower()
    return [
        o for o in OCORRENCIAS_HISTORICO
        if o["natureza"].lower() == n and o["regiao"].lower() == r and o["dias_atras"] <= dias
    ]


def buscar_documento(termo: str) -> list[dict]:
    """Busca um termo nos títulos/trechos de documentos sintéticos."""
    t = termo.strip().lower()
    return [d for d in DOCUMENTOS if t in d["titulo"].lower() or t in d["trecho"].lower()]


# --- descrição das ferramentas (o que o cliente descobre) -------------------
ESPECIFICACOES: dict[str, FerramentaSpec] = {
    "consultar_veiculo": FerramentaSpec(
        nome="consultar_veiculo",
        descricao="Consulta uma placa na base fictícia de veículos. Args: placa.",
        parametros=[ParametroSpec(nome="placa", descricao="Placa no formato ABC1D23")],
        sensivel=True,  # consulta a dados de veículo — pede confirmação humana
    ),
    "consultar_ocorrencias_similares": FerramentaSpec(
        nome="consultar_ocorrencias_similares",
        descricao="Lista ocorrências da mesma natureza e região nos últimos N dias. "
        "Args: natureza, regiao, dias (opcional).",
        parametros=[
            ParametroSpec(nome="natureza"),
            ParametroSpec(nome="regiao"),
            ParametroSpec(nome="dias", tipo="int", obrigatorio=False),
        ],
    ),
    "buscar_documento": FerramentaSpec(
        nome="buscar_documento",
        descricao="Busca um termo em documentos sintéticos. Args: termo.",
        parametros=[ParametroSpec(nome="termo")],
    ),
}

IMPLEMENTACOES = {
    "consultar_veiculo": consultar_veiculo,
    "consultar_ocorrencias_similares": consultar_ocorrencias_similares,
    "buscar_documento": buscar_documento,
}
