"""Dados e lógica determinística. Todos os dados são FICTÍCIOS (treinamento)."""

from __future__ import annotations

import re

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

OCORRENCIAS: dict[str, str] = {
    "PCDF-SIM-0002": (
        "03/08/2026, Taguatinga. Dois indivíduos em motocicleta anunciaram assalto e "
        "levaram o celular da vítima; um portava simulacro de arma. Placa citada: ABC1D23."
    ),
    "PCDF-SIM-0009": (
        "18/08/2026, Asa Sul. Comunicante percebeu a ausência da bicicleta da garagem. "
        "Sem arrombamento, sem testemunhas."
    ),
    "PCDF-SIM-0011": (
        "20/08/2026, Ceilândia. Relato confuso sobre um veículo e um objeto subtraído; "
        "faltam data e local exatos."
    ),
}

VEICULOS = {"ABC1D23": {"situacao": "consta alerta de furto (simulado)"}}
HISTORICO = [
    {"protocolo": "PCDF-SIM-2003", "regiao": "Taguatinga", "natureza": "Roubo"},
    {"protocolo": "PCDF-SIM-2007", "regiao": "Guará", "natureza": "Furto"},
]


def extrair_campos(texto: str) -> dict:
    t = texto.lower()
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    placa = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)
    regiao = next((r for r in ("Taguatinga", "Asa Sul", "Ceilândia", "Guará") if r.lower() in t), None)
    return {
        "data_fato": f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None,
        "local": regiao,
        "placa_citada": placa.group(0) if placa else None,
        "tem_violencia": any(g in t for g in ("assalto", "arma", "anunciaram", "simulacro")),
        "confuso": "confuso" in t or "faltam" in t,
    }


def consultar_veiculo(placa: str) -> dict:
    return {"placa": placa, **VEICULOS.get(placa, {"situacao": "sem apontamentos (simulado)"})}


def consultar_similares(regiao: str | None, natureza: str | None = None,
                        ampla: bool = False) -> list[dict]:
    """`ampla=False`: só a mesma região. `ampla=True`: qualquer região, mesma natureza."""
    if ampla:
        return [h for h in HISTORICO if natureza and h["natureza"].lower() == natureza.lower()]
    return [h for h in HISTORICO if regiao and h["regiao"].lower() == regiao.lower()]
