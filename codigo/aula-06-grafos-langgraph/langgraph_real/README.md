# LangGraph de verdade

O mesmo grafo do SIGMA (`app/sigma_grafo.py`), agora com o pacote `langgraph`.

```bash
pip install -r ../requirements-opcionais.txt
python langgraph_real/grafo_lg.py
python langgraph_real/grafo_lg.py PCDF-SIM-0011
```

| Motor mínimo (`app/grafo.py`) | LangGraph |
|---|---|
| nó devolve o `Estado` inteiro | nó devolve só as chaves que mudou (merge automático) |
| `caminho` acumulado à mão | `Annotated[list, reducer]` — o reducer concatena |
| `aresta_condicional(no, roteador)` — roteador devolve o nome do nó | `add_conditional_edges(no, roteador, {rótulo: nó})` — roteador devolve um rótulo |
| `max_passos` no `compilar()` | `recursion_limit` no `invoke()` |
| sem execução paralela | ramos independentes rodam em paralelo; há checkpointing, streaming, human-in-the-loop |

A API do LangGraph muda entre versões menores — testado com `langgraph` 0.2+.
Se o import falhar, o conceito está inteiro no motor mínimo.
