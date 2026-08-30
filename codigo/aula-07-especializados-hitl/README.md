# Aula 7 — Agentes Especializados e Human-in-the-Loop (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Os nós do grafo da Aula 6 viram **agentes com papéis** — cada um com a sua
memória — e o fluxo **para e espera um humano** antes da ação sensível
(a tipificação). Para isso o estado é **persistido** (checkpoint) e o fluxo
sabe **retomar**, até de outro processo.

## Laboratório (offline, só a biblioteca padrão)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt    # só pytest

python main.py                     # roda -> PARA no breakpoint -> aprova -> conclui
python main.py PCDF-SIM-0002 rejeitar   # rejeita, volta ao Jurídico, corrige, conclui
python main_retomar.py iniciar     # roda até pausar e ENCERRA o processo
python main_retomar.py aprovar <checkpoint>   # processo NOVO carrega e conclui
python solucao_exercicios.py       # gabarito (ou: basico | intermediario | desafio)
pytest -q                          # 9 testes
```

## Estrutura

```
app/
├── memoria.py   # Memoria (bloco de notas append-only de UM agente) + Estado compartilhado (serializável)
├── agentes.py   # investigador -> analista -> juridico -> consolidador (cada um escreve UMA chave)
├── hitl.py      # PausaParaHumano (breakpoint) · Checkpoint (JSON) · Fluxo.iniciar / .retomar
└── bases_sinteticas.py
main.py · main_retomar.py · solucao_exercicios.py · tests/ · saida/ (checkpoints, gitignored)
```

## O fluxo

```
investigar -> analisar -> juridico -> [BREAKPOINT: aprovação humana] -> consolidar -> fim
                                          │
        rejeitar-com-nota ────────────────┘  (volta ao Jurídico com a nota; limite de ciclos)
        corrigir ─────────────────────────►  (a tipificação do humano prevalece)
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 7 |
|---|---|
| `agentes.py` | separação de responsabilidades — cada agente só escreve a sua chave |
| `memoria.py :: Memoria` | memória do agente: append-only, própria de cada um, vai no checkpoint |
| `hitl.py :: PausaParaHumano` | o breakpoint — o fluxo devolve o controle antes da ação sensível |
| `hitl.py :: Checkpoint` | persistência: o estado (e as memórias) no disco → retoma de outro processo |
| `hitl.py :: Fluxo.retomar` | aprovar / corrigir / rejeitar-com-nota (ciclo HITL, com limite) |

## Riscos em produção (discussão)

- **Human-in-the-loop ≠ human-on-the-loop.** Aqui o humano está *no circuito*:
  a execução para e não continua sem ele. "On the loop" (só monitorando) não dá
  a mesma garantia de responsabilidade.
- **Checkpoint com dados pessoais no disco.** Criptografia em repouso, controle
  de acesso, retenção definida (LGPD). O `saida/` do lab é só demonstração.
- **Fadiga de aprovação.** Se tudo pede aprovação, o operador carimba sem ler.
  O breakpoint tem que estar só onde realmente importa (a tipificação), e o
  painel de decisão tem que mostrar a memória dos agentes.
- **A tipificação é proposta, nunca imposta** — e a decisão do humano fica registrada.
