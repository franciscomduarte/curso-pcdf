"""Bases fictícias que o servidor MCP expõe.

>>> Todos os dados são FICTÍCIOS e destinados exclusivamente ao treinamento.
>>> Placas, nomes, protocolos e documentos NÃO correspondem a nada real.

Estas "bases" são só dicionários em memória. O ponto da aula é que o agente
NUNCA fala com elas direto — ele fala com o servidor MCP, que decide o que
expor e registra cada acesso.
"""

from __future__ import annotations

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

# --- base de veículos (fictícia) ---------------------------------------------
VEICULOS: dict[str, dict] = {
    "ABC1D23": {"marca_modelo": "Honda CG 160", "cor": "preta",
                "situacao": "consta alerta de furto (simulado)"},
    "XYZ9Z87": {"marca_modelo": "Fiat Argo", "cor": "branca",
                "situacao": "sem apontamentos (simulado)"},
    "QRS4T56": {"marca_modelo": "VW Gol", "cor": "prata",
                "situacao": "sem apontamentos (simulado)"},
}

# --- base de ocorrências já registradas (fictícia) --------------------------
OCORRENCIAS_HISTORICO: list[dict] = [
    {"protocolo": "PCDF-SIM-2001", "natureza": "Furto", "regiao": "Asa Norte", "dias_atras": 2,
     "resumo": "Furto de bicicleta em garagem de prédio, sem arrombamento."},
    {"protocolo": "PCDF-SIM-2002", "natureza": "Furto", "regiao": "Asa Norte", "dias_atras": 5,
     "resumo": "Subtração de notebook em área comum de condomínio."},
    {"protocolo": "PCDF-SIM-2003", "natureza": "Roubo", "regiao": "Taguatinga", "dias_atras": 1,
     "resumo": "Roubo de celular em parada de ônibus, dupla em motocicleta."},
    {"protocolo": "PCDF-SIM-2004", "natureza": "Estelionato", "regiao": "Ceilândia", "dias_atras": 9,
     "resumo": "Golpe do falso anúncio de venda com pagamento por Pix."},
    {"protocolo": "PCDF-SIM-2005", "natureza": "Furto", "regiao": "Guará", "dias_atras": 20,
     "resumo": "Furto de fios de cobre em obra."},
]

# --- documentos sintéticos (fictícios) -------------------------------------
DOCUMENTOS: list[dict] = [
    {"id": "DOC-SIM-01", "titulo": "Termo de declaração (modelo)",
     "trecho": "A comunicante afirma que percebeu a ausência dos bens ao retornar..."},
    {"id": "DOC-SIM-02", "titulo": "Auto de apreensão (modelo)",
     "trecho": "Foram apreendidos: 1 aparelho celular, 1 capacete, sem documentação..."},
    {"id": "DOC-SIM-03", "titulo": "Relatório de análise de vínculos (modelo)",
     "trecho": "Não foram identificados vínculos entre os envolvidos nas ocorrências..."},
]

POLITICA_DE_USO = (
    "Este servidor expõe consultas de APOIO à triagem. As respostas são rascunho para "
    "análise humana. É proibido: usar para decidir autoria, indiciamento ou prisão; "
    "cruzar dados fora do escopo autorizado; persistir resultados fora da trilha de "
    "auditoria. Todo acesso é registrado."
)
