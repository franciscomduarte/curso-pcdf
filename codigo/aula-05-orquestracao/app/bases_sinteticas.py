"""Ocorrências e bases fictícias.

>>> Todos os dados são FICTÍCIOS e destinados exclusivamente ao treinamento.
"""

from __future__ import annotations

import re

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

OCORRENCIAS: dict[str, str] = {
    "PCDF-SIM-0002": (
        "03/08/2026, Taguatinga. A vítima relata que dois indivíduos em motocicleta "
        "anunciaram assalto e levaram o celular; um portava simulacro de arma. "
        "Placa da moto dos autores anotada por testemunha: ABC1D23."
    ),
    "PCDF-SIM-0009": (
        "18/08/2026, Asa Sul. Comunicante percebeu a ausência da bicicleta que estava "
        "na garagem do prédio ao retornar. Sem sinais de arrombamento, sem testemunhas."
    ),
}

VEICULOS = {
    "ABC1D23": {"marca_modelo": "Honda CG 160", "situacao": "consta alerta de furto (simulado)"},
}

HISTORICO = [
    {"protocolo": "PCDF-SIM-2003", "natureza": "Roubo", "regiao": "Taguatinga",
     "resumo": "Roubo de celular por dupla em motocicleta."},
    {"protocolo": "PCDF-SIM-2007", "natureza": "Furto", "regiao": "Asa Sul",
     "resumo": "Furto de bicicleta em área comum."},
]


# --- "ferramentas" que o Consultor usa -----------------------------------
def consultar_veiculo(placa: str) -> dict:
    d = VEICULOS.get(placa.upper())
    return {"placa": placa.upper(), "encontrado": bool(d), **(d or {})}


def consultar_similares(regiao: str) -> list[dict]:
    return [h for h in HISTORICO if h["regiao"].lower() == regiao.lower()]


# --- extração determinística (o "trabalho" do Extrator) ------------------
def extrair_campos(texto: str) -> dict:
    t = texto.lower()
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    data = f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None
    placa = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)
    regiao = next((r for r in ("Taguatinga", "Asa Sul", "Asa Norte", "Ceilândia", "Guará")
                   if r.lower() in t), None)
    return {"data_fato": data, "local": regiao,
            "placa_citada": placa.group(0) if placa else None,
            "tem_violencia": any(g in t for g in ("assalto", "arma", "simulacro", "anunciaram")),
            "sem_arrombamento": "sem sinais de arrombamento" in t or "sem arrombamento" in t}
