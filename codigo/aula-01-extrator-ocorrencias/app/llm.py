"""A interface do LLM e suas duas implementações.

Ideia central da Aula 1: o agente só conhece um método — `extrair(texto)`.
Podemos plugar um LLM falso (aula, sem chave) ou a OpenAI (produção) sem tocar
no resto do código.

  ExtratorLLM (Protocol)
    ├── MockExtrator    -> heurística determinística, roda offline
    └── OpenAIExtrator  -> OpenAI API, saída estruturada validada
"""

from __future__ import annotations

import os
import re
from typing import Protocol

from .esquema import NaturezaOcorrencia, Ocorrencia, Pessoa, Veiculo

INSTRUCAO_SISTEMA = (
    "Você apoia a triagem de boletins de ocorrência da Polícia Civil. "
    "Extraia SOMENTE o que está no texto, sem inferir autoria nem culpa. "
    "Se um campo não aparecer no texto, deixe-o vazio/nulo. "
    "Responda apenas no formato estruturado solicitado."
)


class ExtratorLLM(Protocol):
    """Contrato: recebe o texto livre da ocorrência, devolve uma Ocorrencia."""

    def extrair(self, texto: str) -> Ocorrencia: ...


# ---------------------------------------------------------------------------
# 1) MockExtrator — sem chave de API, resultado sempre igual
# ---------------------------------------------------------------------------
_PALAVRAS_NATUREZA = [
    (NaturezaOcorrencia.ROUBO, ("assalto", "anunciaram assalto", "mediante", "arma", "simulacro")),
    (NaturezaOcorrencia.FURTO, ("subtraíd", "furt", "sem arrombamento", "sem violência")),
    (NaturezaOcorrencia.AMEACA, ("ameaç", "intimidat", "mensagens intimidatórias")),
    (NaturezaOcorrencia.DANO, ("riscad", "furad", "danific", "picharam", "quebr")),
    (NaturezaOcorrencia.ESTELIONATO, ("pix", "anúncio falso", "golpe", "estelionato", "nunca foi entregue")),
    (NaturezaOcorrencia.LESAO_CORPORAL, ("agrediu", "lesão", "socos", "espancad")),
    (NaturezaOcorrencia.PERTURBACAO, ("som alto", "perturbação", "sossego")),
]

_REGIOES = (
    "Asa Norte", "Asa Sul", "Taguatinga", "Ceilândia", "Guará", "Lago Sul",
    "Lago Norte", "Gama", "Sobradinho", "Planaltina", "Samambaia", "Águas Claras",
)


def _classificar(texto: str) -> NaturezaOcorrencia:
    t = texto.lower()
    for natureza, gatilhos in _PALAVRAS_NATUREZA:
        if any(g in t for g in gatilhos):
            return natureza
    return NaturezaOcorrencia.OUTROS


def _data_iso(texto: str) -> str | None:
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if not m:
        return None
    dia, mes, ano = m.groups()
    return f"{ano}-{mes}-{dia}"


def _local(texto: str) -> str | None:
    for reg in _REGIOES:
        if reg.lower() in texto.lower():
            return reg
    return None


def _placas(texto: str) -> list[str]:
    return re.findall(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)


def _pessoas(texto: str) -> list[Pessoa]:
    pessoas: list[Pessoa] = []
    padroes = [
        (r"comunicante ([A-Z][a-záéíóúâ]+ [A-Z][a-záéíóúâ]+)", "comunicante"),
        (r"v[ií]tima ([A-Z][a-záéíóúâ]+ [A-Z][a-záéíóúâ]+)", "vítima"),
        (r"Sr\.? ([A-Z][a-záéíóúâ]+ [A-Z][a-záéíóúâ]+)", "comunicante"),
        (r"[Tt]estemunha:? o? ?[a-z]* ?([A-Z][a-záéíóúâ]+ [A-Z][a-záéíóúâ]+)", "testemunha"),
    ]
    vistos = set()
    for padrao, papel in padroes:
        for nome in re.findall(padrao, texto):
            if nome not in vistos:
                vistos.add(nome)
                pessoas.append(Pessoa(nome=nome, papel=papel))
    return pessoas


def _veiculos(texto: str) -> list[Veiculo]:
    veiculos: list[Veiculo] = []
    for marca in ("Honda CG", "Fiat Argo", "Fiat Uno", "VW Gol", "Honda Biz"):
        if marca.lower() in texto.lower():
            cor = ""
            m = re.search(marca + r"[^.,]*?(preta|branca|prata|vermelha|cinza)", texto, re.I)
            if m:
                cor = " " + m.group(1).lower()
            placas = _placas(texto)
            veiculos.append(Veiculo(descricao=marca + cor, placa=placas[0] if placas else None))
    return veiculos


def _objetos(texto: str) -> list[str]:
    catalogo = ("notebook", "bicicleta", "celular", "carteira", "mochila",
                "relógio", "documento", "cartão", "dinheiro")
    return [o for o in catalogo if o in texto.lower()]


class MockExtrator:
    """LLM falso: heurística por palavras-chave. Determinístico, offline."""

    def extrair(self, texto: str) -> Ocorrencia:
        natureza = _classificar(texto)
        primeira_frase = re.split(r"(?<=[.!?])\s+", texto.strip())[0]
        return Ocorrencia(
            natureza=natureza,
            data_fato=_data_iso(texto),
            local=_local(texto),
            pessoas=_pessoas(texto),
            veiculos=_veiculos(texto),
            objetos=_objetos(texto),
            resumo=primeira_frase[:240],
            entidades_relevantes=re.findall(r"'([^']+)'", texto),
        )


# ---------------------------------------------------------------------------
# 2) OpenAIExtrator — produção (requer OPENAI_API_KEY)
# ---------------------------------------------------------------------------
class OpenAIExtrator:
    """Usa a OpenAI com saída estruturada (Structured Outputs)."""

    def __init__(self, modelo: str | None = None) -> None:
        from openai import OpenAI  # import tardio: só quando realmente usado

        self._client = OpenAI()  # lê OPENAI_API_KEY do ambiente
        self._modelo = modelo or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def extrair(self, texto: str) -> Ocorrencia:
        # A Responses API com text_format devolve o objeto Pydantic já validado.
        # Confira na doc atual da OpenAI o método e o modelo recomendados.
        # Obs.: não passamos `temperature` — vários modelos recentes rejeitam o
        # parâmetro. Para extração, a consistência vem do schema e do prompt.
        resposta = self._client.responses.parse(
            model=self._modelo,
            input=[
                {"role": "system", "content": INSTRUCAO_SISTEMA},
                {"role": "user", "content": f"Boletim:\n\n{texto}"},
            ],
            text_format=Ocorrencia,
        )
        ocorrencia = resposta.output_parsed
        if ocorrencia is None:
            raise ValueError("A OpenAI não retornou uma Ocorrencia válida.")
        return ocorrencia


# ---------------------------------------------------------------------------
# Seleção automática
# ---------------------------------------------------------------------------
def extrator_padrao() -> ExtratorLLM:
    """OpenAIExtrator se houver OPENAI_API_KEY; senão, MockExtrator."""
    if os.getenv("OPENAI_API_KEY", "").strip() and os.getenv("OPENAI_API_KEY") != "coloque_sua_chave_aqui":
        return OpenAIExtrator()
    return MockExtrator()
