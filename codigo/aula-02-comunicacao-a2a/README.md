# Aula 2 — Comunicação Agente-a-Agente (A2A) · SIGMA

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Três agentes conversando: o **Extrator** publica o que encontrou, o **Classificador**
reage e o **Auditor** registra tudo. O mesmo fluxo aparece em três transportes —
barramento em memória, MQTT e gRPC — para comparar Request/Response × Pub/Sub.

## Laboratório principal (offline, sem nada além de pydantic)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main_local.py               # pub/sub + request/response em memória
python solucao_exercicios.py       # gabarito dos laboratórios
pytest -q                          # testes do núcleo A2A
```

## Caminho MQTT (pub/sub sobre broker)

```bash
pip install -r requirements-opcionais.txt
# 1x: criar o usuário do broker  (ver mosquitto/LEIA-ME.md)
docker compose up -d
cp .env.example .env               # ajuste MQTT_USER / MQTT_PASSWORD
python main_mqtt.py
docker compose down
```

## Caminho gRPC (request/response tipado)

```bash
pip install -r requirements-opcionais.txt
./grpc_demo/gerar.sh               # Windows: .\grpc_demo\gerar.ps1
python grpc_demo/servidor.py       # terminal 1
python grpc_demo/cliente.py        # terminal 2
```

## Estrutura

```
app/
├── mensagem.py         # EnvelopeA2A + Performativa (subconjunto FIPA-ACL)
├── transporte.py       # Transporte (Protocol) · BarramentoLocal · ServicoLocal
├── transporte_mqtt.py  # BarramentoMQTT (paho-mqtt)                    [opcional]
├── agentes.py          # AgenteExtrator / AgenteClassificador / AgenteAuditor
└── ocorrencias.py      # dados sintéticos + extrair()/classificar() determinísticos
grpc_demo/              # classificador.proto + servidor/cliente        [opcional]
main_local.py · main_mqtt.py · docker-compose.yml · solucao_exercicios.py · tests/
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 2 |
|---|---|
| `mensagem.py` | FIPA-ACL: a performativa dá *intenção* à mensagem; contrato validado |
| `transporte.py` | pub/sub desacopla produtor e consumidor; request/response acopla |
| `agentes.py` | acrescentar o Auditor não toca em ninguém — vantagem do barramento |
| `transporte_mqtt.py` | mesma interface, agora entre processos/máquinas via broker |
| `grpc_demo/` | contrato obrigatório (`.proto`), binário, síncrono, baixa latência |

## Riscos em produção (discussão)

- **Spoofing de tópico**: sem autenticação, qualquer processo publica `ocorrencia.classificada`
  falsa. Mitigação: broker com auth + ACL por tópico, TLS/mTLS, assinatura do envelope.
- **Envelope não confiável**: valide `conteudo` contra schema antes de agir (mesma lógica
  de prompt injection da Aula 1).
- **Broadcast vaza dados**: quem pode assinar `#`? Least privilege nos tópicos.
- **Entrega e ordem**: em memória é síncrono e ordenado; no MQTT há QoS, retentativa e
  possível reordenação — o desenho dos agentes precisa tolerar isso.
