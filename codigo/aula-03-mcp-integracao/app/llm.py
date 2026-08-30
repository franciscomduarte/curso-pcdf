"""O LLM que decide QUAL ferramenta chamar.

Mesma ideia das aulas anteriores: interface primeiro.

  LLMConsultor (Protocol)
    ├── MockConsultor   -> plano roteirizado, offline, determinístico
    └── OpenAIConsultor -> function calling da OpenAI (opcional)

O plano é uma lista de passos. Cada passo é ou uma chamada de ferramenta
{"ferramenta": ..., "argumentos": {...}} ou o encerramento
{"resposta_final": "..."}.
"""

from __future__ import annotations

import os
from typing import Protocol

from .esquema import FerramentaSpec


class LLMConsultor(Protocol):
    def proximo_passo(self, contexto: str, ferramentas: list[FerramentaSpec],
                      observacoes: list[str]) -> dict: ...


class MockConsultor:
    """Roteiro fixo: para uma ocorrência de furto com placa citada, consulta o
    veículo e ocorrências similares; depois encerra."""

    def proximo_passo(self, contexto: str, ferramentas, observacoes) -> dict:
        tem = {f.nome for f in ferramentas}
        ja_chamou = " ".join(observacoes)
        c = contexto.lower()

        if ("consultar_veiculo" in tem and _placa(contexto)
                and "consultar_veiculo" not in ja_chamou):
            return {"pensamento": "Há uma placa no relato. Vou consultá-la.",
                    "ferramenta": "consultar_veiculo",
                    "argumentos": {"placa": _placa(contexto)}}
        if ("consultar_ocorrencias_similares" in tem
                and "consultar_ocorrencias_similares" not in ja_chamou):
            return {"pensamento": "Vou ver se há padrão na região.",
                    "ferramenta": "consultar_ocorrencias_similares",
                    "argumentos": {"natureza": _natureza(c), "regiao": _regiao(contexto), "dias": 15}}
        return {"pensamento": "Já tenho contexto suficiente para o enriquecimento.",
                "resposta_final": _sintetizar(observacoes)}


class OpenAIConsultor:
    """Usa function calling da OpenAI. Requer OPENAI_API_KEY. Ilustrativo:
    a forma exata da API muda entre versões — confira a doc vigente."""

    def __init__(self, modelo: str | None = None) -> None:
        from openai import OpenAI

        self._client = OpenAI()
        self._modelo = modelo or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def proximo_passo(self, contexto, ferramentas, observacoes) -> dict:
        tools = [{
            "type": "function",
            "name": f.nome,
            "description": f.descricao,
            "parameters": {
                "type": "object",
                "properties": {p.nome: {"type": "string"} for p in f.parametros},
                "required": [p.nome for p in f.parametros if p.obrigatorio],
            },
        } for f in ferramentas]
        historico = "\n".join(f"- {o}" for o in observacoes) or "(nada ainda)"
        resp = self._client.responses.create(
            model=self._modelo,
            tools=tools,
            input=[
                {"role": "system", "content":
                 "Você apoia a triagem. Use as ferramentas para enriquecer a ocorrência. "
                 "Quando tiver o suficiente, responda em texto o enriquecimento."},
                {"role": "user", "content": f"Ocorrência:\n{contexto}\n\nJá consultado:\n{historico}"},
            ],
        )
        for item in resp.output:
            if getattr(item, "type", "") == "function_call":
                import json
                return {"ferramenta": item.name, "argumentos": json.loads(item.arguments)}
        return {"resposta_final": resp.output_text}


# --- heurísticas do MockConsultor -----------------------------------------
import re


def _placa(texto: str) -> str | None:
    m = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)
    return m.group(0) if m else None


def _natureza(c: str) -> str:
    for n, gs in [("Furto", ("furt", "subtra")), ("Roubo", ("roubo", "assalto")),
                  ("Estelionato", ("pix", "golpe", "estelionato"))]:
        if any(g in c for g in gs):
            return n
    return "Furto"


def _regiao(texto: str) -> str:
    for r in ("Asa Norte", "Asa Sul", "Taguatinga", "Ceilândia", "Guará", "Lago Sul"):
        if r.lower() in texto.lower():
            return r
    return "Asa Norte"


def _sintetizar(observacoes: list[str]) -> str:
    if not observacoes:
        return "Sem consultas — nada a acrescentar à triagem."
    return "Enriquecimento para a triagem humana: " + " | ".join(observacoes)


def consultor_padrao() -> LLMConsultor:
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if chave and chave != "coloque_sua_chave_aqui":
        return OpenAIConsultor()
    return MockConsultor()
