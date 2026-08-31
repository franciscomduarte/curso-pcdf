# Aula 9 — Auto-scaling, Observabilidade e Segurança (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

O cluster da Aula 8 sabia se curar (`reconciliar()`) mas não sabia responder
"quantas réplicas eu preciso agora?" nem "por que uma chamada está lenta ou
falhando?", e não tinha nenhum portão na entrada. A Aula 9 adiciona três peças
sobre o mesmo `Cluster`, sem reescrevê-lo: um autoscaler (`HPA`), métricas +
traço por investigação, e um `Gateway` com guardrail de entrada.

## Como rodar (offline, só biblioteca padrão)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                     # Gateway + guardrail + HPA + painel de métricas
python main_incidente.py           # diagnostique uma falha usando só painel + traço
python solucao_exercicios.py       # gabarito dos laboratórios (+ verificar_alertas)
python solucao_exercicios.py extras # exercícios extras (se sobrar tempo)
pytest -q                          # 37 testes
```

## Estrutura

```
app/
├── cluster.py          # o motor da Aula 8 + cronometragem por chamada
├── memoria.py           # Estado — atendido_por agora é {etapa, pod, duracao_ms}
├── agentes.py            # investigador/analista/juridico/consolidador (igual à Aula 8)
├── store.py               # StoreCompartilhado (igual à Aula 8)
├── fluxo.py                 # o SIGMA rodando via Services, medindo cada etapa
├── observabilidade.py        # Metricas (chamadas/falhas/latência/p95) + formatar_traco
├── autoscaler.py               # HPA — mesma fórmula do HPA real do Kubernetes
├── guardrail.py                 # padrão suspeito + limite de taxa por origem
└── gateway.py                    # guardrail + fluxo, um único ponto de entrada
main.py · main_incidente.py · solucao_exercicios.py · tests/
k8s_real/                          # HorizontalPodAutoscaler real (manifesto)   [opcional]
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 9 |
|---|---|
| `autoscaler.py :: avaliar` | reconciliação contínua aplicada a uma métrica de carga, não a uma contagem fixa |
| `observabilidade.py :: Metricas` | chamadas/falhas/latência média/p95 por Service — a base de um painel real |
| `observabilidade.py :: formatar_traco` | o traço de UMA investigação através dos pods que a atenderam |
| `guardrail.py :: validar_entrada` | injeção de prompt (Aula 1) barrada na borda, antes do fluxo |
| `guardrail.py :: permitir` | limite de taxa por origem — "consumo ilimitado" (Aula 4/8) aplicado à entrada |
| `gateway.py :: Gateway` | guardrail + fluxo atrás de um único ponto de entrada |
| `main_incidente.py` | diagnóstico de uma falha usando só o que um operador real teria: painel + traço |
| `k8s_real/hpa.yaml` | o mesmo autoscaler, como manifesto `autoscaling/v2` real |

## Sobre as durações capturadas neste README/HTML

As latências em `latencia_media_ms`/`latencia_p95_ms` medem tempo de CPU real
(`time.perf_counter()`), não uma chamada de rede simulada — como todo o
cluster roda em memória, os valores ficam sempre frações de milissegundo e
**variam ligeiramente a cada execução** (dependem da máquina e do que mais
está rodando nela). O que é estável — e o que a aula avalia — é a ordem de
grandeza, o fato de nunca serem negativos, e a estrutura do painel. Em
produção, cada chamada teria uma rede real por trás e latências bem maiores.

## Riscos em produção (discussão)

- **HPA sem estabilização (`stabilizationWindowSeconds`)**: escalar para baixo
  imediatamente após um pico pode gerar oscilação ("flapping") se a carga for
  instável — o Kubernetes real tem uma janela de estabilização por padrão.
- **Guardrail baseado em substring**: `validar_entrada` é um filtro didático
  (comparação literal, case-insensitive) — detecção de prompt injection em
  produção exige defesa em profundidade (instrução de sistema + filtro +
  validação de saída), nunca um único regex.
- **Sem autenticação no Gateway**: qualquer "origem" é uma string livre — em
  produção, a origem viria de autenticação real (mTLS, API key, JWT), não de
  um parâmetro informado pelo chamador.
- **Métricas em memória**: `Metricas` não sobrevive a um restart nem é
  compartilhada entre processos — um Prometheus real persiste e agrega entre
  réplicas, do mesmo jeito que o `StoreCompartilhado` (Aula 8) tirou o
  checkpoint da memória de um pod.
