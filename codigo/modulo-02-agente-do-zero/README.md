# Módulo 2 — Um agente do zero (sem framework)

> **Meta:** entender que um agente é um **loop** em volta de um LLM. Quando você
> vê isso, LangGraph e CrewAI deixam de ser mágica e viram conveniência.

## O que é um agente?

Um agente repete quatro coisas até terminar a tarefa:

```
pensar  ->  agir (chamar ferramenta)  ->  observar resultado  ->  repetir  ->  responder
```

O **LLM** decide *o que fazer*. O **nosso código** executa a ferramenta escolhida
e devolve o resultado para o LLM. Só isso.

## Como rodar

Não precisa de chave de API — usamos um LLM **falso e roteirizado** (`MockLLM`):

```bash
python agente_do_zero.py
```

Você verá o agente pensar, buscar a população, calcular a raiz e responder.

### Trocar por um modelo real (opcional)

No fim de `agente_do_zero.py` há a classe `OpenAILLM`. Para usá-la:

```bash
pip install openai
export OPENAI_API_KEY="sua-chave"
```

e troque `MockLLM()` por `OpenAILLM()` na função `__main__`.

## O que observar no código (roteiro de leitura)

1. **Ferramenta** é só função + descrição. O agente não "tem poderes"; ele só
   escolhe entre as funções que nós registramos.
2. O **LLM está atrás de uma interface** (`LLM`). Mock e modelo real são
   intercambiáveis — isso separa *lógica do agente* de *inteligência do modelo*.
3. O **loop** (`Agente.executar`) é o coração. Note o `max_passos`: sem essa
   trava, um agente confuso rodaria para sempre (e gastaria dinheiro).
4. O **parsing** do JSON é frágil de propósito. Guarde essa dúvida: *o que
   acontece se o modelo responder texto fora do formato?* Voltaremos a isso no
   Módulo 6.

## Exercício

Partindo de `agente_do_zero.py`:

1. **Nova ferramenta.** Crie uma ferramenta `c_para_f` que converte Celsius em
   Fahrenheit e registre-a na lista de ferramentas.
2. **Nova tarefa.** Escreva um `MockLLM` roteirizado para a tarefa
   *"Converta 37°C para Fahrenheit"*, usando sua ferramenta.
3. **Loop mais robusto.** Faça o agente **detectar quando repete a mesma ação**
   (mesma ferramenta + mesmos argumentos duas vezes seguidas) e parar, em vez de
   ir até `max_passos`. Por que isso é importante num sistema com vários agentes?

Gabarito em `solucao_exercicio.py` (rode `python solucao_exercicio.py`).

## Pergunta de discussão (abre o próximo módulo)

Este agente resolve tarefas em sequência, sozinho. **Em que situação valeria a
pena ter mais de um agente?** E em que situação isso só adicionaria custo e
confusão? — é exatamente o tema do Módulo 3.
