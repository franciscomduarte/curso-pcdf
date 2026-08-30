"""Dados fictícios. Todos os dados são FICTÍCIOS e destinados ao treinamento."""

from __future__ import annotations

import re

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

OCORRENCIAS: dict[str, str] = {
    "PCDF-SIM-0002": (
        "03/08/2026, Taguatinga. Dois indivíduos em motocicleta anunciaram assalto e "
        "levaram o celular da vítima; um portava simulacro de arma de fogo. "
        "Placa citada por testemunha: ABC1D23."
    ),
    "PCDF-SIM-0009": (
        "18/08/2026, Asa Sul. A comunicante percebeu a ausência da bicicleta que "
        "estava na garagem do prédio. Sem arrombamento e sem testemunhas."
    ),
}

VEICULOS = {"ABC1D23": {"situacao": "consta alerta de furto (simulado)"}}


def extrair_campos(texto: str) -> dict:
    t = texto.lower()
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    placa = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)
    regiao = next((r for r in ("Taguatinga", "Asa Sul", "Ceilândia", "Guará") if r.lower() in t), None)
    return {
        "data_fato": f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None,
        "local": regiao,
        "placa_citada": placa.group(0) if placa else None,
        "grave_ameaca": any(g in t for g in ("assalto", "arma", "anunciaram", "simulacro")),
    }


def consultar_veiculo(placa: str) -> dict:
    return {"placa": placa, **VEICULOS.get(placa, {"situacao": "sem apontamentos (simulado)"})}


# Tabela DIDÁTICA e simplificada — não é orientação jurídica.
TIPIFICACOES = {
    "com_ameaca": {"artigo": "Art. 157 do CP (roubo)", "natureza": "Roubo"},
    "sem_ameaca": {"artigo": "Art. 155 do CP (furto)", "natureza": "Furto"},
}
