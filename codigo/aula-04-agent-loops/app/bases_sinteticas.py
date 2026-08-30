"""Dados fictícios para o laboratório.

>>> Todos os dados são FICTÍCIOS e destinados exclusivamente ao treinamento.

Na Aula 3 estas consultas viriam de um servidor MCP. Aqui elas são funções
locais — o foco desta aula é o LOOP que decide quando chamá-las e quando parar.
"""

from __future__ import annotations

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

VEICULOS: dict[str, dict] = {
    "ABC1D23": {"marca_modelo": "Honda CG 160", "situacao": "consta alerta de furto (simulado)"},
    "XYZ9Z87": {"marca_modelo": "Fiat Argo", "situacao": "sem apontamentos (simulado)"},
}

OCORRENCIAS_HISTORICO: list[dict] = [
    {"protocolo": "PCDF-SIM-2001", "natureza": "Furto", "regiao": "Taguatinga",
     "dias_atras": 2, "resumo": "Furto de motocicleta em via pública."},
    {"protocolo": "PCDF-SIM-2002", "natureza": "Furto", "regiao": "Taguatinga",
     "dias_atras": 6, "resumo": "Tentativa de furto de motocicleta, autor fugiu."},
]

DOCUMENTOS: list[dict] = [
    {"id": "DOC-SIM-01", "assunto": "apreensão",
     "trecho": "Auto de apreensão de motocicleta Honda CG sem placa, em 04/08/2026."},
    {"id": "DOC-SIM-02", "assunto": "declaração",
     "trecho": "Termo de declaração da vítima sobre o horário do fato."},
]
