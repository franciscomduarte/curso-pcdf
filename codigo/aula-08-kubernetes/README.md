# Aula 8 — Arquitetura Distribuída e Deploy com Kubernetes (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Os quatro agentes da Aula 7 (Investigador, Analista, Jurídico, Consolidador)
rodavam num processo só. Aqui cada um vira um `Deployment` + `Service` num
cluster — real ou simulado — e o checkpoint HITL da Aula 7 sai do disco de
um processo para um store compartilhado entre réplicas.

## Como rodar (offline, só biblioteca padrão)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                     # sobe o cluster mínimo, roda o SIGMA nele
python main_falha.py               # mata um pod — self-healing e indisponibilidade
python solucao_exercicios.py       # gabarito dos laboratórios (+ rolling update)
python solucao_exercicios.py extras # exercícios extras (se sobrar tempo)
pytest -q                          # 17 testes
```

## Estrutura

```
app/
├── cluster.py       # motor mínimo: ConfigMap, Pod, Deployment, Service, Cluster
├── memoria.py        # Memoria + Estado (igual à Aula 7)
├── agentes.py         # investigador/analista/juridico/consolidador (+ config)
├── store.py           # StoreCompartilhado (o checkpoint da Aula 7, fora do pod)
└── fluxo.py            # o SIGMA rodando via Services, com breakpoint HITL
main.py · main_falha.py · solucao_exercicios.py · tests/
k8s_real/               # servidor HTTP real + Dockerfile + manifestos      [opcional]
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 8 |
|---|---|
| `cluster.py :: Deployment` | N réplicas de uma imagem; `reconciliar()` = self-healing |
| `cluster.py :: Service` | nome estável + round-robin — quem chama não sabe qual pod atendeu |
| `cluster.py :: ConfigMap` | configuração fora do código — mesma imagem, comportamento diferente |
| `store.py :: StoreCompartilhado` | por que o checkpoint da Aula 7 não pode morar na memória de um pod |
| `solucao_exercicios.py :: rolling_update` | trocar o Deployment por trás de um Service sem downtime |
| `k8s_real/` | os mesmos 3 recursos, como manifestos reais (`apps/v1`/`v1`) |

## Riscos em produção (discussão)

- **Secrets em ConfigMap**: ConfigMap não é criptografado nem tem controle de
  acesso separado — credenciais vão em `Secret`, nunca em `ConfigMap`.
- **Sem `NetworkPolicy`**: por padrão, qualquer pod do cluster pode chamar
  qualquer Service — least privilege também vale na rede.
- **Sem limites de recurso**: um pod sem `resources.limits` pode consumir o
  node inteiro — o "consumo ilimitado" da Aula 4, agora em nível de infra.
- **Imagem sem verificação de origem**: puxar de um registro não confiável é
  a mesma lógica de risco de um servidor MCP não confiável (Aula 3).
