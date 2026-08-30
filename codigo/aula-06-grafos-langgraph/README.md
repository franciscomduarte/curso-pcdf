# Aula 6 — Modelagem de Sistemas Baseados em Grafos (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Os cinco padrões da Aula 5 viram um **grafo de execução explícito**: nós (etapas),
arestas (transições), estado compartilhado, arestas condicionais e um ciclo.

## Laboratório (offline, só a biblioteca padrão)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt    # só pytest

python main.py                     # roda o grafo do SIGMA (PCDF-SIM-0009 dispara o ciclo)
python main.py PCDF-SIM-0002
python main.py PCDF-SIM-0011       # relato confuso -> desvio para o humano
python main_ciclo.py               # DAG × ciclo condicional × ciclo sem saída (trava)
python solucao_exercicios.py       # gabarito (ou: basico | intermediario | desafio)
pytest -q                          # 9 testes
```

## LangGraph de verdade (opcional)

```bash
pip install -r requirements-opcionais.txt
python langgraph_real/grafo_lg.py
```

## Estrutura

```
app/
├── estado.py        # Estado — o objeto que trafega por todos os nós (+ caminho, passos)
├── grafo.py         # No, Aresta, Grafo, GrafoCompilado — o motor mínimo + validação + tem_ciclo
├── nos.py           # as funções-nó do SIGMA + os roteadores das arestas condicionais
├── sigma_grafo.py   # monta o grafo: START -> extrair -> classificar -> ... -> END
└── bases_sinteticas.py
main.py · main_ciclo.py · solucao_exercicios.py · tests/ · langgraph_real/
```

## O grafo do SIGMA

```
START -> extrair -> classificar
classificar --(relato confuso?)--> encaminhar_humano -> END
            --(senão)------------> consultar -> revisar
revisar --(enriquecimento vazio e tentativas < 2?)--> consultar   (CICLO)
        --(senão)-----------------------------------> END
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 6 |
|---|---|
| `grafo.py` | nó = função sobre o estado; aresta estática vs condicional; START/END |
| `grafo.py :: validar` | o grafo se verifica antes de rodar (nó sem saída, aresta para nó inexistente) |
| `grafo.py :: tem_ciclo` | DAG × ciclo — só nas arestas estáticas; o condicional depende do estado |
| `nos.py :: rota_pos_revisar` | a condição de saída do ciclo (junta com a trava da Aula 4) |
| `GrafoCompilado :: max_passos` | ciclo sem condição de saída só é seguro com a trava |

## Riscos em produção (discussão)

- **Ciclo sem condição de saída**: o roteador precisa de uma condição que
  *eventualmente* fica falsa; a trava de passos é a rede de segurança, não o plano.
- **Estado compartilhado mutável**: dois nós que escrevem o mesmo campo criam
  ordem-dependência. O LangGraph usa reducers; aqui a ordem é explícita.
- **Grafo grande sem observabilidade**: registre o `caminho` de cada execução —
  é o que permite entender por que uma ocorrência foi para um ramo.
