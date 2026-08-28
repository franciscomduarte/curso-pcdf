"""
Agente do zero — SEM framework.
Módulo 2 da disciplina de Sistemas Multiagentes.

Ideia central: um "agente" é apenas um LOOP em volta de um LLM:

        pensar  ->  agir (chamar ferramenta)  ->  observar  ->  repetir  ->  responder

Nenhuma mágica. Frameworks (LangGraph, CrewAI, etc.) só embrulham este loop.
Se o aluno entende ESTE arquivo, ele entende o que todos os frameworks escondem.

COMO RODAR (sem chave de API, usando um LLM falso e roteirizado):

        python agente_do_zero.py

Para usar um modelo REAL, veja a classe `OpenAILLM` no fim do arquivo.
"""
from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass
from typing import Callable, Protocol


# ---------------------------------------------------------------------------
# 1) FERRAMENTAS (tools)
# ---------------------------------------------------------------------------
# Uma ferramenta é só uma função Python + metadados. O agente decide QUANDO
# chamá-la; nós só a disponibilizamos.

# Avaliador aritmético seguro (NÃO use eval() sobre saída de LLM — isso é uma
# porta de injeção; discutiremos no Módulo 6 - Segurança).
_OPERADORES = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _avaliar(no: ast.AST) -> float:
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp):
        return _OPERADORES[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp):
        return _OPERADORES[type(no.op)](_avaliar(no.operand))
    raise ValueError("expressão não permitida")


def calcular(expressao: str) -> str:
    """Avalia uma expressão aritmética simples. Ex.: '219550 ** 0.5'."""
    return str(round(_avaliar(ast.parse(expressao, mode="eval").body), 2))


def buscar(consulta: str) -> str:
    """Busca 'falsa' numa base fixa — substitui uma API/RAG no exemplo."""
    base = {
        "população rio verde go": "219550",
        "população goiânia": "1494599",
        "capital de goiás": "Goiânia",
    }
    return base.get(consulta.strip().lower(), "Nenhum resultado encontrado.")


@dataclass
class Ferramenta:
    nome: str
    descricao: str
    funcao: Callable[..., str]


FERRAMENTAS = [
    Ferramenta("buscar", "Busca um fato. Args: {'consulta': str}", buscar),
    Ferramenta("calcular", "Avalia expressão aritmética. Args: {'expressao': str}", calcular),
]


# ---------------------------------------------------------------------------
# 2) O LLM (real ou falso) — sempre atrás da mesma interface
# ---------------------------------------------------------------------------
class LLM(Protocol):
    def completar(self, mensagens: list[dict]) -> str: ...


class MockLLM:
    """
    LLM FALSO e roteirizado. Não "pensa"; devolve respostas fixas conforme o
    estágio da conversa. Serve para rodar o loop sem custo e de forma
    determinística em aula. A tarefa roteirizada é:
        "Quantos habitantes tem Rio Verde (GO)? Qual a raiz quadrada disso?"
    """

    def completar(self, mensagens: list[dict]) -> str:
        observacoes = [m for m in mensagens if m["role"] == "tool"]
        n = len(observacoes)

        if n == 0:  # ainda não buscou nada
            return json.dumps({
                "pensamento": "Preciso da população de Rio Verde (GO). Vou buscar.",
                "acao": {"ferramenta": "buscar",
                         "args": {"consulta": "população Rio Verde GO"}},
            }, ensure_ascii=False)

        if n == 1:  # já tem o número, falta a conta
            return json.dumps({
                "pensamento": "Tenho 219550. Agora calculo a raiz quadrada.",
                "acao": {"ferramenta": "calcular",
                         "args": {"expressao": "219550 ** 0.5"}},
            }, ensure_ascii=False)

        return json.dumps({  # já tem tudo -> responde
            "pensamento": "Já tenho população e raiz. Posso responder.",
            "resposta_final": ("Rio Verde (GO) tem ~219.550 habitantes; "
                               "a raiz quadrada é ~468,56."),
        }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 3) O AGENTE — o loop
# ---------------------------------------------------------------------------
INSTRUCAO_SISTEMA = """Você é um agente que resolve tarefas em passos.
A cada passo responda APENAS um objeto JSON, em um destes dois formatos:

  Para usar uma ferramenta:
  {"pensamento": "...", "acao": {"ferramenta": "<nome>", "args": {...}}}

  Para dar a resposta final:
  {"pensamento": "...", "resposta_final": "..."}

Ferramentas disponíveis:
%s
Não escreva nada fora do JSON."""


class Agente:
    def __init__(self, llm: LLM, ferramentas: list[Ferramenta], max_passos: int = 6):
        self.llm = llm
        self.registro = {f.nome: f for f in ferramentas}
        self.max_passos = max_passos  # trava anti-loop (ponto de aula do M6)

    def _sistema(self) -> str:
        catalogo = "\n".join(f"- {f.nome}: {f.descricao}" for f in self.registro.values())
        return INSTRUCAO_SISTEMA % catalogo

    def executar(self, tarefa: str, verboso: bool = True) -> str:
        mensagens = [
            {"role": "system", "content": self._sistema()},
            {"role": "user", "content": tarefa},
        ]

        for passo in range(1, self.max_passos + 1):
            bruto = self.llm.completar(mensagens)

            # PARSING: frágil de propósito. No M6 trocamos por saída estruturada.
            try:
                dados = json.loads(bruto)
            except json.JSONDecodeError:
                return f"[erro] O modelo não devolveu JSON válido:\n{bruto}"

            if verboso:
                print(f"\n--- passo {passo} ---")
                print("pensamento:", dados.get("pensamento"))

            # Condição de parada: resposta final
            if "resposta_final" in dados:
                return dados["resposta_final"]

            # Senão, executa a ferramenta escolhida
            acao = dados["acao"]
            nome = acao["ferramenta"]
            if nome not in self.registro:
                observacao = f"Ferramenta desconhecida: {nome}"
            else:
                observacao = self.registro[nome].funcao(**acao["args"])

            if verboso:
                print(f"acao: {nome}({acao['args']}) -> {observacao}")

            mensagens.append({"role": "assistant", "content": bruto})
            mensagens.append({"role": "tool", "content": observacao})

        return "[parada] Limite de passos atingido sem resposta final."


# ---------------------------------------------------------------------------
# 4) EXECUÇÃO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agente = Agente(llm=MockLLM(), ferramentas=FERRAMENTAS)
    tarefa = "Quantos habitantes tem Rio Verde (GO)? Qual a raiz quadrada disso?"

    print("TAREFA:", tarefa)
    resultado = agente.executar(tarefa)
    print("\n=== RESPOSTA FINAL ===")
    print(resultado)


# ---------------------------------------------------------------------------
# 5) (OPCIONAL) LLM REAL — troque MockLLM() por OpenAILLM() no bloco acima.
#     Requer:  pip install openai   e   export OPENAI_API_KEY=...
# ---------------------------------------------------------------------------
class OpenAILLM:
    def __init__(self, modelo: str = "gpt-4o-mini"):
        from openai import OpenAI  # import tardio: só carrega se for usar
        self.cliente = OpenAI()
        self.modelo = modelo

    def completar(self, mensagens: list[dict]) -> str:
        # a API não conhece o papel "tool" solto; viramos as observações em 'user'
        msgs = [
            {"role": ("user" if m["role"] == "tool" else m["role"]),
             "content": (f"Observação da ferramenta: {m['content']}"
                         if m["role"] == "tool" else m["content"])}
            for m in mensagens
        ]
        r = self.cliente.chat.completions.create(
            model=self.modelo, messages=msgs,
            response_format={"type": "json_object"}, temperature=0,
        )
        return r.choices[0].message.content
