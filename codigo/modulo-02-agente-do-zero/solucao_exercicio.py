"""
GABARITO do exercício do Módulo 2 (uso do professor).

Resolve os três itens do enunciado (ver README.md):
  1) Criar uma nova ferramenta e registrá-la.
  2) Roteirizar o MockLLM para uma nova tarefa que use essa ferramenta.
  3) Deixar o loop mais robusto: detectar quando o agente repete a MESMA ação
     (sintoma clássico de loop) e parar antes de estourar max_passos.

Roda com:  python solucao_exercicio.py
"""
from __future__ import annotations

import json

from agente_do_zero import Agente, Ferramenta, FERRAMENTAS


# --- Item 1: nova ferramenta -----------------------------------------------
def celsius_para_fahrenheit(celsius: str) -> str:
    return str(round(float(celsius) * 9 / 5 + 32, 2))


FERRAMENTAS_EXT = FERRAMENTAS + [
    Ferramenta("c_para_f", "Converte Celsius em Fahrenheit. Args: {'celsius': str}",
               celsius_para_fahrenheit),
]


# --- Item 2: MockLLM roteirizado para a nova tarefa ------------------------
class MockLLMConversao:
    def completar(self, mensagens: list[dict]) -> str:
        n = len([m for m in mensagens if m["role"] == "tool"])
        if n == 0:
            return json.dumps({
                "pensamento": "Preciso converter 37°C para Fahrenheit.",
                "acao": {"ferramenta": "c_para_f", "args": {"celsius": "37"}},
            }, ensure_ascii=False)
        return json.dumps({
            "pensamento": "Tenho o valor convertido.",
            "resposta_final": "37°C equivalem a 98,6°F.",
        }, ensure_ascii=False)


# --- Item 3: agente com detecção de ação repetida --------------------------
class AgenteRobusto(Agente):
    def executar(self, tarefa: str, verboso: bool = True) -> str:
        mensagens = [
            {"role": "system", "content": self._sistema()},
            {"role": "user", "content": tarefa},
        ]
        ultima_acao = None

        for passo in range(1, self.max_passos + 1):
            bruto = self.llm.completar(mensagens)
            dados = json.loads(bruto)

            if verboso:
                print(f"\n--- passo {passo} ---")
                print("pensamento:", dados.get("pensamento"))

            if "resposta_final" in dados:
                return dados["resposta_final"]

            acao = dados["acao"]
            assinatura = (acao["ferramenta"], json.dumps(acao["args"], sort_keys=True))
            if assinatura == ultima_acao:  # <-- melhoria pedida no item 3
                return ("[parada] Ação repetida detectada "
                        f"({acao['ferramenta']}). Provável loop.")
            ultima_acao = assinatura

            nome = acao["ferramenta"]
            obs = (self.registro[nome].funcao(**acao["args"])
                   if nome in self.registro else f"Ferramenta desconhecida: {nome}")
            if verboso:
                print(f"acao: {nome}({acao['args']}) -> {obs}")

            mensagens.append({"role": "assistant", "content": bruto})
            mensagens.append({"role": "tool", "content": obs})

        return "[parada] Limite de passos atingido."


if __name__ == "__main__":
    agente = AgenteRobusto(llm=MockLLMConversao(), ferramentas=FERRAMENTAS_EXT)
    tarefa = "Converta 37°C para Fahrenheit."
    print("TAREFA:", tarefa)
    print("\n=== RESPOSTA FINAL ===")
    print(agente.executar(tarefa))
