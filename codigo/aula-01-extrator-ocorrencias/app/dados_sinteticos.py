"""Dados sintéticos para os laboratórios da Aula 1.

>>> Todos os dados utilizados neste laboratório são fictícios e destinados
>>> exclusivamente ao treinamento. Nomes, endereços, placas, telefones, CPFs e
>>> quaisquer outros identificadores NÃO correspondem a pessoas ou fatos reais.

Formato de cada item: dicionário com 'id' e 'texto' (o texto livre que um
comunicante poderia registrar). O agente extrator transforma 'texto' em um
objeto Ocorrencia validado.
"""

AVISO_DADOS = (
    "Todos os dados deste laboratório são FICTÍCIOS e destinados exclusivamente "
    "ao treinamento."
)

OCORRENCIAS_BRUTAS: list[dict[str, str]] = [
    {
        "id": "PCDF-SIM-0001",
        "texto": (
            "Em 15/08/2026, por volta das 21h, na Asa Norte, a comunicante Marina "
            "Alves relatou que seu notebook e uma bicicleta foram subtraídos da "
            "garagem do prédio enquanto ela estava fora. Não houve arrombamento "
            "aparente. Testemunha: o porteiro Jorge Nunes, que percebeu um homem "
            "desconhecido no hall por volta das 20h30."
        ),
    },
    {
        "id": "PCDF-SIM-0002",
        "texto": (
            "No dia 03/08/2026, em Taguatinga, a vítima Rafael Souza informou que "
            "dois indivíduos em uma motocicleta Honda CG preta, placa fictícia "
            "ABC1D23, anunciaram assalto e levaram seu celular e a carteira na "
            "parada de ônibus da Avenida Central. Um dos autores portava simulacro "
            "de arma de fogo."
        ),
    },
    {
        "id": "PCDF-SIM-0003",
        "texto": (
            "Registro de 10/08/2026: a comunicante Beatriz Lima afirma que vem "
            "recebendo mensagens intimidatórias de um ex-colega de trabalho, "
            "identificado apenas como 'Diego', pelo aplicativo de mensagens, com "
            "ameaças de agressão. Local dos fatos: residência da vítima, no Guará."
        ),
    },
    {
        "id": "PCDF-SIM-0004",
        "texto": (
            "Em 22/07/2026, no Lago Sul, o Sr. Henrique Prado comunicou que um "
            "veículo Fiat Argo branco, placa fictícia XYZ9Z87, teve os quatro pneus "
            "furados e a lataria riscada durante a madrugada, na porta de sua casa. "
            "Prejuízo estimado informado pela vítima."
        ),
    },
    {
        "id": "PCDF-SIM-0005",
        "texto": (
            "No dia 05/08/2026, em Ceilândia, a vítima Carla Menezes relatou que "
            "efetuou um Pix de valor elevado para uma conta indicada em um anúncio "
            "falso de venda de celular em rede social. O produto nunca foi entregue "
            "e o vendedor, que se identificava como 'LojaTechDF', bloqueou o contato."
        ),
    },
]


def por_id(ocorrencia_id: str) -> dict[str, str]:
    for item in OCORRENCIAS_BRUTAS:
        if item["id"] == ocorrencia_id:
            return item
    raise KeyError(f"Ocorrência sintética não encontrada: {ocorrencia_id}")
