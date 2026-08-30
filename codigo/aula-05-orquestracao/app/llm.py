"""O LLM que os padrões Supervisor e Debate precisam.

  LLMOrquestrador (Protocol)
    ├── MockLLM     -> decisões roteirizadas, offline, determinísticas
    └── OpenAILLM   -> opcional

- Supervisor: `decidir(dossie)` -> nome do próximo especialista ou "concluir".
- Debate:     `opinar(pergunta, contexto, rodada, outra_opiniao)` -> {resposta, razao, confianca}
              `julgar(pergunta, opinioes)` -> {resposta, justificativa}
"""

from __future__ import annotations

import os
from typing import Protocol

from .especialistas import Dossie


class LLMOrquestrador(Protocol):
    def decidir(self, d: Dossie) -> str: ...
    def opinar(self, pergunta: str, contexto: str, rodada: int,
               outra: dict | None, quem: int = 0) -> dict: ...
    def julgar(self, pergunta: str, opinioes: list[dict]) -> dict: ...


class MockLLM:
    # -- Supervisor --------------------------------------------------------
    def decidir(self, d: Dossie) -> str:
        if not d.tem("campos"):
            return "extrator"
        if not d.tem("classificacao"):
            return "classificador"
        # ADAPTATIVO: ocorrência trivial (sem placa, sem violência) pula o consultor
        c = d.campos or {}
        trivial = not c.get("placa_citada") and not c.get("tem_violencia")
        if not d.tem("enriquecimento") and not trivial:
            return "consultor"
        if not d.tem("revisado"):
            return "revisor"
        return "concluir"

    # -- Debate ---------------------------------------------------------------
    # Debater 0 = "promotor" (tende à tipificação mais grave); debater 1 =
    # "defensor" (tende à mais branda). Na rodada 1 divergem; na rodada 2 leem
    # o argumento do outro e a posição mais fraca pode ceder.
    def opinar(self, pergunta: str, contexto: str, rodada: int,
               outra: dict | None, quem: int = 0) -> dict:
        ctx = contexto.lower()
        violencia = any(g in ctx for g in ("assalto", "arma", "anunciaram", "simulacro"))

        if rodada == 1:
            if quem == 0:   # promotor
                if violencia:
                    return {"resposta": "Roubo", "confianca": 0.8,
                            "razao": "houve grave ameaça — 'anunciaram assalto', simulacro de arma."}
                return {"resposta": "Furto", "confianca": 0.7,
                        "razao": "subtração sem violência ou ameaça descrita."}
            # defensor
            if violencia:
                return {"resposta": "Furto", "confianca": 0.55,
                        "razao": "não houve lesão nem contato físico; caberia analisar furto."}
            return {"resposta": "Furto", "confianca": 0.8,
                    "razao": "nada no relato indica emprego de violência ou ameaça."}

        # rodada 2 — lê `outra` e reconsidera
        if quem == 1 and outra and outra["resposta"] == "Roubo" and outra["confianca"] >= 0.75 and violencia:
            return {"resposta": "Roubo", "confianca": 0.7,
                    "razao": "reconheço: a grave ameaça descrita configura roubo, não furto."}
        base = self.opinar(pergunta, contexto, 1, None, quem)
        return {**base, "razao": f"mantenho: {base['razao']}", "confianca": base["confianca"] + 0.05}

    def julgar(self, pergunta: str, opinioes: list[dict]) -> dict:
        from collections import Counter

        votos = Counter(o["resposta"] for o in opinioes)
        vencedor, n = votos.most_common(1)[0]
        return {"resposta": vencedor,
                "justificativa": f"{n}/{len(opinioes)} opiniões convergiram para '{vencedor}'."}


class OpenAILLM:
    def __init__(self, modelo: str | None = None) -> None:
        from openai import OpenAI

        self._c = OpenAI()
        self._m = modelo or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def _texto(self, prompt: str) -> str:
        r = self._c.responses.create(model=self._m, input=prompt)
        return r.output_text.strip()

    def decidir(self, d: Dossie) -> str:
        estado = {k: d.tem(k) for k in ("campos", "classificacao", "enriquecimento", "revisado")}
        p = ("Você coordena especialistas: extrator, classificador, consultor, revisor. "
             f"Estado atual (o que já existe): {estado}. Responda SÓ com o nome do próximo "
             "especialista a chamar, ou 'concluir'.")
        return self._texto(p).split()[0].strip("'\".")

    def opinar(self, pergunta, contexto, rodada, outra, quem=0):
        papel = "promotor (tende à tipificação mais grave)" if quem == 0 else "defensor (tende à mais branda)"
        p = f"Você é o {papel}.\nPergunta: {pergunta}\nContexto: {contexto}\nRodada {rodada}."
        if outra:
            p += f"\nOutra opinião: {outra}"
        p += "\nResponda em JSON: {\"resposta\": ..., \"razao\": ..., \"confianca\": 0..1}"
        import json
        try:
            return json.loads(self._texto(p))
        except Exception:
            return {"resposta": "indefinido", "razao": "parse falhou", "confianca": 0.0}

    def julgar(self, pergunta, opinioes):
        p = f"Pergunta: {pergunta}\nOpiniões: {opinioes}\nDecida em JSON: {{\"resposta\":...,\"justificativa\":...}}"
        import json
        try:
            return json.loads(self._texto(p))
        except Exception:
            return {"resposta": "indefinido", "justificativa": "parse falhou"}


def llm_padrao() -> LLMOrquestrador:
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if chave and chave != "coloque_sua_chave_aqui":
        return OpenAILLM()
    return MockLLM()
