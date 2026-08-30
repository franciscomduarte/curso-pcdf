# Aula 1 — Agente extrator de ocorrências (SIGMA)

> **Todos os dados deste laboratório são fictícios e destinados exclusivamente
> ao treinamento.** Nenhum nome, endereço, placa ou fato é real.

Primeiro agente da Unidade 8: recebe o texto livre de um boletim de ocorrência
sintético e devolve um objeto **estruturado e validado** (`Ocorrencia`).

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # opcional — só se for usar a OpenAI de verdade
```

**Sem `OPENAI_API_KEY`**, tudo roda offline com o `MockExtrator` (heurística
determinística). Com a chave no `.env`, o mesmo código usa a OpenAI.

```bash
python main.py                     # extrai 1 ocorrência (nível básico)
python main.py PCDF-SIM-0003       # escolhe qual
python main_lote.py                # processa as 5 + relatório consolidado (avançado)
python solucao_exercicios.py       # gabarito dos laboratórios
pytest -q                          # testes (rodam sem chave)
```

## Estrutura

```
app/
├── esquema.py          # Pydantic: Ocorrencia, NaturezaOcorrencia, Pessoa, Veiculo
├── dados_sinteticos.py # 5 ocorrências fictícias
├── llm.py              # ExtratorLLM (Protocol) · MockExtrator · OpenAIExtrator
├── agente_extrator.py  # percepção → ação → observação + retry com backoff
├── classificador.py    # natureza + sinal de "revisar com humano" (lab intermediário)
└── relatorio.py        # consolidação por natureza/região (desafio avançado)
main.py · main_lote.py · solucao_exercicios.py · tests/
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 1 |
|---|---|
| `esquema.py` | saída estruturada como contrato; validação falha cedo |
| `llm.py` | o LLM atrás de uma interface — mock e produção intercambiáveis |
| `agente_extrator.py` | ciclo mínimo do agente; robustez (retries, timeout lógico) |
| `classificador.py` | manter o humano no circuito: sinalizar baixa confiança |
| `relatorio.py` | de um caso para muitos; agregação para apoio à análise |

## Riscos em produção (discussão)

- **Indirect prompt injection**: o texto do boletim é entrada não confiável. Instruções
  escondidas no relato podem tentar desviar o modelo — nunca dê ao extrator poder de ação.
- **Excessive agency**: este agente só lê e estrutura. Não consulta sistemas nem decide nada.
- **Dados**: aqui são sintéticos. Com dados reais valem LGPD, minimização, controle de
  acesso, retenção e auditoria.
- **A saída é rascunho para triagem** — não é decisão sobre autoria, indiciamento ou prisão.
