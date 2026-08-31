# Aula 10 — Projeto Integrador e Estudo de Caso (SIGMA completo)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Este projeto não introduz uma tecnologia nova. Ele integra o que as Aulas 1–9
já construíram — papéis especializados (Aula 7), comunicação via Services
(Aula 8), auto-scaling/observabilidade/guardrail (Aula 9) — e fecha a única
lacuna estrutural que sobrou: as Aulas 7–9 sempre roteavam toda ocorrência
pela mesma sequência fixa de etapas. Aqui, uma **aresta condicional** (o
conceito de grafo da Aula 6) decide, dentro do próprio cluster distribuído,
se uma ocorrência precisa de uma revisão extra antes do breakpoint humano.

## Como rodar (offline, só biblioteca padrão)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                     # o SIGMA completo, roteamento + guardrail + HPA + painel
python main_estudo_caso.py         # a Operação Vetor — um lote misto, fim a fim
python solucao_exercicios.py       # gabarito dos laboratórios (+ relatório operacional)
pytest -q                          # 43 testes
```

## Estrutura

```
app/
├── cluster.py          # motor do cluster — Aula 8/9, sem mudança
├── observabilidade.py   # Metricas + traço — Aula 9, sem mudança
├── autoscaler.py          # HPA — Aula 9, sem mudança
├── guardrail.py             # filtro de injeção + limite de taxa — Aula 9, sem mudança
├── gateway.py                 # guardrail + fluxo, ponto único de entrada — Aula 9, sem mudança
├── store.py                     # checkpoint compartilhado — Aula 8, sem mudança
├── memoria.py                     # Estado — ganhou o campo `revisao`
├── agentes.py                       # os 4 agentes da Aula 7 + `revisor_dupla` (NOVO)
├── roteador.py                        # NOVO — a aresta condicional (Aula 6) que decide a rota
└── fluxo.py                             # adaptado: consulta o roteador depois do Jurídico
main.py · main_estudo_caso.py · solucao_exercicios.py · tests/
```

## O que cada peça demonstra

| Arquivo | O que integra |
|---|---|
| `roteador.py :: decidir_apos_juridico` | aresta condicional (Aula 6) decidindo a rota dentro do cluster distribuído (Aula 8/9) — a integração que faltava |
| `agentes.py :: revisor_dupla` | um quinto agente especializado (padrão da Aula 7), só chamado quando o roteador escala o caso |
| `fluxo.py :: _rodar` | uma linha a menos de dicionário fixo, uma linha a mais de decisão condicional — o resto do fluxo (Aula 7/8) não muda |
| `main_estudo_caso.py` | o estudo de caso da aula (Operação Vetor) rodando fim a fim: roteamento + guardrail + HPA + painel juntos |
| `solucao_exercicios.py :: gerar_relatorio_operacional` | síntese das três fontes de sinal da aula (métricas, roteamento, guardrail) — nenhuma sozinha conta a história inteira |

## Por que este projeto NÃO reimplementa as Aulas 1–5

MCP (Aula 3), os protocolos A2A (Aula 2) e os padrões de orquestração
(Aula 5) já têm demonstrações completas e testadas em suas próprias pastas
(`codigo/aula-02-comunicacao-a2a/`, `codigo/aula-03-mcp-integracao/`,
`codigo/aula-05-orquestracao/`). Reescrevê-los aqui seria repetição, não
integração — o valor desta aula está em conectar a peça que ainda estava
solta (grafo condicional + cluster distribuído), não em duplicar código já
testado. A aula (HTML) recupera essas cinco aulas pelo diagrama de
arquitetura e pelo estudo de caso, sem reimplementar o que elas já provam.

## Riscos em produção (discussão)

- **Monkeypatch de roteador em runtime** (`solucao_exercicios.py`, lab
  intermediário): útil para demonstrar extensibilidade em aula; em produção,
  uma nova aresta condicional deveria ser um novo deploy versionado, nunca
  uma alteração de dicionário em memória.
- **Critério de roteamento simples demais**: `decidir_apos_juridico` decide
  só pela `natureza` da tipificação. Um sistema real provavelmente
  combinaria múltiplos sinais (reincidência, valor envolvido, região) — o
  ponto pedagógico é o mecanismo (aresta condicional), não a régua de corte.
- **Revisor sem redundância própria**: como qualquer Deployment de 1
  réplica (Aula 8), se `revisor-deploy` cair, todo caso grave fica bloqueado
  até `reconciliar()` — só casos leves seguem passando, como o laboratório
  intermediário demonstra.
- Os riscos já discutidos nas Aulas 8/9 (Secret vs. ConfigMap, sem
  NetworkPolicy, HPA sem estabilização, guardrail por substring, Gateway sem
  autenticação) continuam valendo — nada disso foi resolvido nesta aula.
