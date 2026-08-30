"""O LLM do loop ReAct.

  LLMReAct (Protocol)
    ├── MockReAct   -> plano REATIVO: ramifica conforme a observação
    └── OpenAIReAct -> function calling (opcional)

Cada passo devolve um dict:
  {"pensamento": "...", "acao": {"ferramenta": "...", "args": {...}}}
  ou
  {"pensamento": "...", "resposta_final": "..."}
"""

from __future__ import annotations

import os
import re
from typing import Protocol

from .ferramentas import Ferramenta


class LLMReAct(Protocol):
    def pensar(self, tarefa: str, ferramentas: list[Ferramenta],
               historico: list[dict]) -> dict: ...


class MockReAct:
    """Roteiro que REAGE à observação (diferente do roteiro fixo da Aula 3):

    - se há placa na tarefa -> consulta o veículo;
    - SE o veículo "consta alerta" -> busca o auto de apreensão;
      SENÃO -> pula essa parte;
    - consulta ocorrências similares na região;
    - monta a linha do tempo e encerra.
    """

    def pensar(self, tarefa: str, ferramentas, historico) -> dict:
        feito = {h["acao"]["ferramenta"] for h in historico if "acao" in h}
        obs = {h["acao"]["ferramenta"]: h.get("observacao") for h in historico if "acao" in h}
        placa = _placa(tarefa)
        regiao = _regiao(tarefa)

        if placa and "consultar_veiculo" not in feito:
            return {"pensamento": f"A tarefa cita a placa {placa}. Vou consultá-la.",
                    "acao": {"ferramenta": "consultar_veiculo", "args": {"placa": placa}}}

        veiculo_obs = str(obs.get("consultar_veiculo", ""))
        if "consta alerta" in veiculo_obs and "buscar_documento" not in feito:
            return {"pensamento": "O veículo consta alerta. Pode haver auto de apreensão.",
                    "acao": {"ferramenta": "buscar_documento", "args": {"assunto": "apreensão"}}}

        if regiao and "consultar_ocorrencias_similares" not in feito:
            return {"pensamento": "Vou ver se há furtos parecidos na região.",
                    "acao": {"ferramenta": "consultar_ocorrencias_similares",
                             "args": {"regiao": regiao, "natureza": "Furto"}}}

        if "montar_linha_tempo" not in feito:
            eventos = "\n".join(_resumo(h["acao"]["ferramenta"], h.get("observacao"))
                                for h in historico if "acao" in h)
            return {"pensamento": "Tenho o suficiente. Vou montar a linha do tempo.",
                    "acao": {"ferramenta": "montar_linha_tempo", "args": {"eventos": eventos}}}

        return {"pensamento": "Linha do tempo pronta.",
                "resposta_final": str(obs.get("montar_linha_tempo", "(sem síntese)"))}


class OpenAIReAct:
    """function calling da OpenAI. Ilustrativo — confira a doc vigente."""

    def __init__(self, modelo: str | None = None) -> None:
        from openai import OpenAI

        self._client = OpenAI()
        self._modelo = modelo or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def pensar(self, tarefa, ferramentas, historico) -> dict:
        tools = [{
            "type": "function", "name": f.nome, "description": f.descricao,
            "parameters": {"type": "object",
                           "properties": {}, "additionalProperties": True},
        } for f in ferramentas]
        linhas = [f"{h.get('pensamento','')} | {h.get('acao')} -> {h.get('observacao')}"
                  for h in historico]
        resp = self._client.responses.create(
            model=self._modelo, tools=tools,
            input=[{"role": "system", "content":
                    "Você é um agente ReAct. Pense, aja com uma ferramenta por vez, "
                    "observe, repita. Quando tiver a resposta, escreva-a em texto."},
                   {"role": "user", "content": f"Tarefa: {tarefa}\nHistórico:\n" + "\n".join(linhas)}],
        )
        for item in resp.output:
            if getattr(item, "type", "") == "function_call":
                import json
                return {"pensamento": "(via OpenAI)",
                        "acao": {"ferramenta": item.name, "args": json.loads(item.arguments)}}
        return {"pensamento": "(via OpenAI)", "resposta_final": resp.output_text}


# --- heurísticas do mock -------------------------------------------------
def _resumo(ferramenta: str, obs) -> str:
    """Transforma a observação crua numa nota curta para a linha do tempo."""
    if ferramenta == "consultar_veiculo" and isinstance(obs, dict):
        return f"- veículo {obs.get('marca_modelo', '?')}: {obs.get('situacao', 'sem dados')}"
    if ferramenta == "buscar_documento" and isinstance(obs, list) and obs:
        return f"- documento: {obs[0].get('trecho', '')}"
    if ferramenta == "consultar_ocorrencias_similares" and isinstance(obs, list):
        return f"- {len(obs)} ocorrência(s) similar(es) na região"
    return f"- {ferramenta}: {str(obs)[:80]}"


def _placa(texto: str) -> str | None:
    m = re.search(r"[A-Z]{3}\d[A-Z0-9]\d{2}", texto)
    return m.group(0) if m else None


def _regiao(texto: str) -> str | None:
    for r in ("Taguatinga", "Asa Norte", "Ceilândia", "Guará", "Gama"):
        if r.lower() in texto.lower():
            return r
    return None


def llm_padrao() -> LLMReAct:
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if chave and chave != "coloque_sua_chave_aqui":
        return OpenAIReAct()
    return MockReAct()
