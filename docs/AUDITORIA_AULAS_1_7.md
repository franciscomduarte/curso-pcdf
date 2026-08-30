# Auditoria das Aulas 1–7 — Unidade 8 (PCDF)

**Data:** 2026-08-30
**Tipo:** Auditoria diagnóstica (Fases 1–2 do prompt de revisão). **Nenhuma alteração foi feita em `aulas/` ou `codigo/` nesta etapa** — só leitura, execução de código em venvs efêmeros (limpos ao final) e este documento.
**Método:** governança lida do estado atual do disco (`DESIGN_INSTRUCIONAL.md`, `RUBRICA_AULAS.md`, `PADRAO_AULAS.md`, `GUIA_AVALIACAO.md`, `CHECKLIST_PUBLICACAO.md`, `CLAUDE.md`); as 7 suítes de teste e os `main*.py`/`solucao_exercicios.py` de cada aula foram **executados de verdade** (não presumidos) pelo auditor principal e por 4 subagentes independentes (3 de revisão pedagógica cobrindo as 7 aulas, 1 técnico revalidando as Aulas 6–7). Toda alegação de saída no HTML foi confrontada com a execução real.

---

## Visão geral

| Aula | Nota inicial | Nota após correção | Veredito | Problemas críticos |
|---|---:|---:|---|---|
| 1 — Fundamentos de Agentes | 7,4 | **8,3** (Fase 3 aplicada 2026-08-30) | 🟢 Aprovada | Nenhum |
| 2 — Comunicação A2A | 7,2 | **8,3** (Fase 3 aplicada 2026-08-30) | 🟢 Aprovada | Nenhum |
| 3 — MCP e Integração | 7,2 | **8,3** (Fase 3 aplicada 2026-08-30) | 🟢 Aprovada | Resolvido — saída recapturada verbatim |
| 4 — Agent Loops | 7,7 | **8,3** (Fase 3 aplicada 2026-08-30) | 🟢 Aprovada | Nenhum |
| 5 — Orquestração | 7,8 | **8,4** (Fase 3 aplicada 2026-08-30) | 🟢 Aprovada | Nenhum |
| 6 — Grafos e LangGraph | 7,5 | — | 🟡 Aprovada com ajustes | Nenhum |
| 7 — Especializados e HITL | 7,6 | — | 🟡 Aprovada com ajustes | Nenhum |

**Fase 3 (correção) em andamento, uma aula por vez, na ordem 1→7 — Aula 1 concluída.** As demais 6 ainda não atingem o piso de publicação (≥ 8,0, CHECKLIST §13). Nenhuma tem código quebrado, dependência inexistente, API incompatível ou exercício impossível — os 66 testes (7+7+10+10+13+10+9) passam, todos os `main*.py`/`solucao_exercicios.py` principais rodam sem erro, e a segurança é tratada de forma transversal e contextualizada em todas. O que segura a nota é um **conjunto de lacunas sistêmicas da nova governança**, detalhado abaixo, mais problemas técnicos pontuais (contagens de teste erradas, saídas resumidas sem marcação, uma saída fabricada em formato).

### Lacunas sistêmicas (as 4 abaixo aparecem, em grau variável, nas 7 aulas)

1. **Sem avaliação diagnóstica.** Toda aula recapitula a anterior em prosa, mas nenhuma **interroga** a turma no início (CHECKLIST §12, GUIA §2 item 3). `_modelo-aula.html` não reserva esse espaço.
2. **Sem seção de Transferência distinta.** PADRAO_AULAS.md §2 lista "Transferência" como item 14, separado do "Desafio avançado" (item 12). Nas 7 aulas, o "Exercício prático"/"Desafio" do Bloco de Avaliação permanece no mesmo domínio (SIGMA/triagem policial) do resto da aula — é extensão, não transferência a um contexto novo (DESIGN_INSTRUCIONAL §12/13; RUBRICA §3.11, peso 5%). `_modelo-aula.html` também não reserva essa seção — é a causa raiz.
3. **Objetivos fora do formato observável explícito.** As 7 aulas usam bullets curtos com verbos adequados (Bloom presente, do "Definir" ao "Justificar"/"Projetar"), mas nenhuma segue o molde de CLAUDE.md §7 / DESIGN §5: "Ao final da aula, o estudante será capaz de **[ação observável]**, utilizando **[ferramenta]**, em **[contexto]**, respeitando **[critério]**." Em algumas aulas (4, 5, 6, 7) falta também um objetivo explícito de nível **Avaliar/Criar**, embora o Desafio avançado já exija esse raciocínio.
4. **Nenhum desafio avançado tem rubrica própria** (RUBRICA §8 / CLAUDE.md §28) — todas dizem apenas "orientação no gabarito".

Essas 4 lacunas nasceram porque as aulas foram construídas contra o **PROMPT MESTRE** original e `_modelo-aula.html`, ambos anteriores à governança atual. **Recomenda-se atualizar `_modelo-aula.html`** (adicionar blocos de diagnóstico e Transferência) antes de propagar a correção às 7 aulas, para não repetir o mesmo gap na Aula 8 em diante.

### Problemas técnicos recorrentes

- **Contagem de testes errada em 3 checkpoints do HTML**: Aula 4 diz "9 testes" (real: **10**), Aula 5 diz "10 testes" (real: **13**), Aula 6 diz e o README confirma "9 testes" (real: **10**). Aulas 1, 2, 3 e 7 estão corretas (7, sem número explícito nas duas primeiras, e 9 na sétima).
- **Blocos de saída "resumidos" sem marcação clara de elisão** em várias aulas (3, 4, 6, 7) — a maioria é fiel nos valores e algumas já rotulam "(saída resumida)"; uma (Aula 3, `main_escopo.py`) apresenta uma notação (`[PCDF-SIM-2001 (Furto, Asa Norte), ...]`) que **o programa nunca produz** — ver Aula 3, Crítico.
- **Caracteres fora da política do CLAUDE.md §39** em `print()`: `×` em `codigo/aula-04-agent-loops/main_limites.py` e `codigo/aula-06-grafos-langgraph/main_ciclo.py`; travessão `—` em vários `print()` das Aulas 5–7. Nenhum causou `UnicodeEncodeError` neste ambiente (cp1252 aceita ambos), mas violam a regra explícita do projeto e são um risco em outro codepage.

---

# Aula 1 — Fundamentos de Agentes e Engenharia Básica

`aulas/aula-01-fundamentos.html` · `codigo/aula-01-extrator-ocorrencias/` (7 testes)

## Nota inicial: 7,4 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6 | Qualidade técnica (10%) | 8 |
| Organização (8%) | 9 | Segurança (8%) | 9 |
| Fundamentação (10%) | 8 | Acessibilidade (5%) | 8 |
| Prática (12%) | 8 | Atualidade (5%) | 8 |
| Avaliação (12%) | 6 | Transferência (5%) | 4 |
| Competências (10%) | 8 | Carga cognitiva (5%) | 6 |

## Pontos fortes preservados

- PBL exemplar: abre com "a fila de boletins", a IA entra como meio, não como fim; SIGMA amarrado ao fim com diagrama de evolução e frase-âncora.
- Conceito × tecnologia bem separado (`ExtratorLLM` como `Protocol` → `MockExtrator`/`OpenAIExtrator`): o agente é testável e roda offline, 100% determinístico.
- Segurança já na Aula 1: indirect prompt injection e excessive agency contextualizados no texto do BO; `.aviso responsavel` explica que `papel: "suspeito citado"` é transcrição, não juízo do agente.
- Vocabulário nomeado uma vez (ambiente, percepção, estado, memória, objetivo, autonomia, ação, observação) que serve o curso inteiro.

## Problemas encontrados

### Altos
- **Sem exercício de transferência real.** Evidência: `aula-01-fundamentos.html:588-591` (exercício "Receptação" e o "Desafio" de teste) — ambos no mesmo extrator/domínio. Impacto: RUBRICA §3.11 não é atendida; não há evidência de que o aluno aplique "saída estruturada + humano no circuito" a um problema novo. Correção: seção "Transferência" com um problema de domínio distinto (ver propostas abaixo).
- **Avaliação sem instrumento diagnóstico.** Evidência: Bloco 8 só tem perguntas conceituais + exercício + checklist; nenhuma sondagem inicial. Impacto: turma mista (a própria nota do instrutor reconhece isso) sem calibração de largada. Correção: 3–4 min de sondagem verbal no Bloco 1 ("o que uma API de LLM devolve?", "cite uma decisão que a IA não deveria tomar sozinha sobre uma pessoa").

### Médios
- **Objetivos fora do formato observável** (`:52-56`) — verbos adequados, mas sem cláusula de ferramenta/contexto/critério; "Reconhecer" é verbo fraco para DESIGN §5.
- **`openai>=1.40` no `requirements.txt` do núcleo**, sem `requirements-opcionais.txt` (única das 7 aulas a fazer isso — Aulas 2 e 3 separam corretamente). `OpenAIExtrator` já faz import tardio, então mover é seguro e não quebra nada.
- **Demonstração de 55 min é apertada**: venv + pip + `.env` + 3 peças de código + primeiro Pydantic + rodar. O próprio gabarito admite "sem folga — turmas mistas tendem a estourar".

### Baixos
- Saída de `main.py` no HTML é compactada (JSON com quebras de linha reduzidas) — a legenda avisa disso, o que é aceitável, mas o ideal é reproduzir `model_dump_json(indent=2)` verbatim.
- Snippet de `esquema.py` no HTML mostra `veiculos: list` sem tipo parametrizado; o arquivo real usa `list[Veiculo]`. Rotulado "(reduzido)", mas pode confundir quem compara linha a linha.

## Alterações realizadas (Fase 3 — 2026-08-30)

1. Objetivos reescritos no formato observável (`Ao final… capaz de [ação], utilizando [ferramenta], em [contexto], respeitando [critério]`), com verbos de Bloom mais altos incluídos (Construir, Aplicar, **Avaliar**).
2. Adicionado **Diagnóstico rápido** (3 min, 3 perguntas) no início do Bloco 1.
3. Adicionada seção **Transferência** distinta no Bloco 8 (antes do "Exercício prático"): projetar um agente de extração para laudos periciais sintéticos — schema, critério de revisão, justificativa de temperatura — com orientação de correção no gabarito (sem resposta fechada) e item correspondente no checklist.
4. `openai` movido do núcleo (`requirements.txt`) para `requirements-opcionais.txt`; README, painel "Stack", bloco `requirements.txt` e comando de validação do HTML atualizados; confirmado que o núcleo roda 100% e os 7 testes passam **sem o pacote `openai` instalado**.
5. Tempos redistribuídos para caber as adições em 300 min: Bloco 2 (Fundamentos) 50→45 (removida a 2ª tabela comparativa, redundante com os 3 cartões de abertura do bloco, substituída por uma frase-síntese); Bloco 6 (Desafio) 30→25 (a "decisão de projeto" virou discussão em dupla de 5 min em vez de meia página escrita); Bloco 8 (Avaliação) 20→30 (absorve a Transferência). Agenda, cabeçalhos de bloco e gabarito "Tempos" atualizados e conferem entre si.

Não alterado: conteúdo técnico dos labs, código-fonte de `app/`, estrutura visual, demais blocos.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 7 passed (revalidado após remover `openai` do núcleo) |
| Execução principal (`main.py`, `main.py PCDF-SIM-0002`) | **PASS** — revalidado sem `openai` instalado |
| Demos (`main_lote.py`, `solucao_exercicios.py`) | **PASS** — saída bate com os blocos do gabarito |
| HTML sanity (tags, Mermaid sem HTML nos rótulos) | **PASS** — balanço de tags conferido após as edições |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos (formato observável) | **PASS** (reescritos) |
| Prática (básico/intermediário/avançado) | **PASS** |
| Avaliação (diagnóstica/formativa/prática/transferência) | **PASS** (diagnóstico e transferência adicionados) |
| Transferência | **PASS** (seção distinta, domínio novo) |
| Segurança | **PASS** |
| Carga horária (300 min, aritmética) | **PASS** (25+45+55+45+15+45+25+15+30=300); consistente entre agenda, cabeçalhos e gabarito |

## Nota final (estimada após as correções): **8,3 / 10** — reavaliação formal por agente de QA independente recomendada antes da publicação definitiva

## Veredito: 🟢 APROVADA (sujeita a confirmação por QA independente)

## Plano de correção priorizado

~~1. Seção "Transferência" com o problema do laudo pericial sintético~~ ✅ feito.
~~2. Diagnóstico inicial de 3–4 min~~ ✅ feito.
~~3. Reescrever os 5 objetivos no formato-modelo~~ ✅ feito.
~~4. Mover `openai` para `requirements-opcionais.txt`~~ ✅ feito.
~~5. Realocar ~10–15 min da Demonstração/Bloco 2 para aliviar a carga~~ ✅ feito (Bloco 2, não a Demonstração — ver Alterações realizadas).

Pendente, de baixa prioridade (não bloqueia publicação): compactação do JSON em `main.py` no HTML (Baixo #1) e o snippet de `esquema.py` com `veiculos: list` sem tipo (Baixo #2) — ambos cosméticos, não fabricam informação.

---

# Aula 2 — Comunicação Agente-a-Agente (A2A)

`aulas/aula-02-comunicacao-a2a.html` · `codigo/aula-02-comunicacao-a2a/` (7 testes)

## Nota inicial: 7,2 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6 | Qualidade técnica (10%) | 7 |
| Organização (8%) | 9 | Segurança (8%) | 9 |
| Fundamentação (10%) | 8 | Acessibilidade (5%) | 8 |
| Prática (12%) | 7 | Atualidade (5%) | 9 |
| Avaliação (12%) | 6 | Transferência (5%) | 4 |
| Competências (10%) | 8 | Carga cognitiva (5%) | 5 |

## Pontos fortes preservados

- Motivação visceral do desacoplamento (nota do instrutor: desenhar o emaranhado, apagar, desenhar o barramento).
- Continuidade real: o Desafio da Aula 1 ("e se a revisão virasse serviço separado?") é literalmente respondido aqui.
- Segurança do barramento madura: spoofing de tópico, envelope não confiável, broadcast/LGPD, com mitigações concretas e referências STRIDE + MITRE T1078.
- Mesma interface, dois transportes (`BarramentoLocal` → `BarramentoMQTT`) sem tocar nos agentes.

## Problemas encontrados

### Altos
- **Instrução do lab MQTT incompleta.** Evidência: `aula-02-comunicacao-a2a.html:464` só cita `docker compose up -d` + `pip install -r requirements-opcionais.txt` + `python main_mqtt.py`. **Verificado no repositório**: `docker-compose.yml` monta `./mosquitto/passwd:ro`, mas esse arquivo **não existe** — só `mosquitto/LEIA-ME.md` (que ensina gerá-lo) e `mosquitto.conf`. O Docker cria um diretório vazio no lugar, o broker não autentica, e `main_mqtt.py` falha com um `ModuleNotFoundError` cru (sem `paho-mqtt`) ou trava no broker se só faltar o `passwd`. Impacto: aluno que segue só o HTML trava justamente no exercício opcional da aula de comunicação. Correção: referenciar `mosquitto/LEIA-ME.md` explicitamente no HTML antes de `docker compose up -d`.
- **Sem transferência distinta.** Evidência: Bloco 8 (`AgenteArquivador`, teste anti-spoofing) e Desafio do Bloco 6 (distribuir o próprio SIGMA) — tudo no mesmo sistema. Correção: seção "Transferência" com o problema do mandado de busca sintético (abaixo).
- **Bloco 2 sobrecarregado.** Evidência: 55 min cobrem síncrono/assíncrono, Req/Resp, Pub/Sub, eventos/filas, MQTT (QoS/retain/curingas/ACL), gRPC (`.proto`/HTTP2/streaming) e FIPA-ACL — 6 conceitos novos com 2 tabelas comparativas. O próprio gabarito já sugere cortes ("se atrasar…"). Correção: tornar padrão a estratégia de corte (MQTT-detalhe e gRPC-streaming viram leitura de referência).

### Médios
- Objetivos sem formato-modelo e sem objetivo de nível "avaliar/justificar" — o Desafio já exige justificar a escolha de transporte por enlace.
- Sem diagnóstico da Aula 1 no início.

### Baixos
- Checkpoint 2 afirma que `main_mqtt.py` "produziu a mesma trilha" de `main_local.py`; o script MQTT não roda a seção request/response — ajustar o texto para "trilha equivalente (10 envelopes)".
- `app/transporte_mqtt.py` importa `fnmatch` sem usar (linha morta comentada) — remover.

## Alterações realizadas (Fase 3 — 2026-08-30)

1. Instrução do lab MQTT corrigida: o HTML agora manda seguir `mosquitto/LEIA-ME.md` (gerar o arquivo de senha) antes de `docker compose up -d`, com uma frase explicando por quê (o broker exige autenticação de propósito). O README do projeto já estava correto — só o HTML tinha a lacuna.
2. Adicionada seção **Transferência** distinta no Bloco 8: projetar a mensageria de um fluxo de mandado de busca sintético (eventos, Pub/Sub × Request/Response, ACL, conteúdo mínimo para auditoria), com orientação no gabarito e item no checklist.
3. Bloco 2 aliviado: QoS/Retain do MQTT e streaming do gRPC viram, por padrão, "leitura de referência" (permanecem no Glossário) em vez de exposição ao vivo — a estratégia de corte que já estava no "se atrasar" do gabarito virou o padrão.
4. Objetivos reescritos no formato observável + acrescentado 1 objetivo de nível **Avaliar/Justificar** (escolha de transporte por enlace), que faltava apesar de o Desafio já exigir esse raciocínio.
5. Diagnóstico rápido (3 min) da Aula 1 no início do Bloco 1.
6. Checkpoint 2 corrigido: não afirma mais que `main_mqtt.py` produz "a mesma trilha" — agora diz "trilha equivalente (10 envelopes)", tecnicamente preciso.
7. Removido o import morto de `fnmatch` em `app/transporte_mqtt.py::assinar()` (Baixo #2 do diagnóstico) — o método não usava a variável; `_on_message()` mantém seu próprio import, que é o que de fato executa o roteamento.
8. Tempos redistribuídos para caber as adições em 300 min: Bloco 2 55→50, Bloco 8 20→25. Agenda, cabeçalhos e gabarito conferem entre si.

Não corrigido nesta fase (Médio, não bloqueante): a instrução opcional de gRPC (`grpc_demo/`) e o traceback cru de `main_mqtt.py` sem `paho-mqtt` instalado — ambos caminhos opcionais, sem impacto no laboratório principal.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 7 passed (revalidado após remover o import morto) |
| Execução principal (`main_local.py`) | **PASS** — saída inalterada, ainda confere com o HTML |
| Demos (`solucao_exercicios.py`) | **PASS** |
| Caminho opcional MQTT (`main_mqtt.py`) | Instrução corrigida (agora referencia `LEIA-ME.md`); traceback cru sem `paho-mqtt` continua — não bloqueante, caminho opcional |
| HTML sanity | **PASS** — balanço de tags conferido após as edições |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **PASS** (reescritos, com objetivo de nível Avaliar) |
| Prática | **PASS** |
| Avaliação | **PASS** (diagnóstico e transferência adicionados) |
| Transferência | **PASS** (seção distinta, domínio novo) |
| Segurança | **PASS** |
| Carga horária | **PASS** (25+50+50+45+15+45+30+15+25=300); Bloco 2 aliviado |

## Nota final (estimada após as correções): **8,3 / 10** — reavaliação formal por agente de QA independente recomendada antes da publicação definitiva

## Veredito: 🟢 APROVADA (sujeita a confirmação por QA independente)

## Plano de correção priorizado

~~1. Corrigir a instrução MQTT~~ ✅ feito.
~~2. Seção "Transferência" (mandado de busca sintético)~~ ✅ feito.
~~3. Aliviar o Bloco 2~~ ✅ feito.
~~4. Objetivo de nível "avaliar" + formato-modelo + diagnóstico da Aula 1~~ ✅ feito.

Pendente, de baixa prioridade (não bloqueia publicação): traceback cru de `main_mqtt.py` sem `paho-mqtt` (poderia capturar `ModuleNotFoundError` e sugerir `pip install -r requirements-opcionais.txt`); caminho gRPC não reverificado nesta rodada.

---

# Aula 3 — MCP e Integração

`aulas/aula-03-mcp-integracao.html` · `codigo/aula-03-mcp-integracao/` (10 testes)

## Nota inicial: 7,2 / 10 — **com 1 problema que, pela letra da RUBRICA §6 ("saída fabricada no HTML"), é um vetor crítico**

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6 | Qualidade técnica (10%) | 6 |
| Organização (8%) | 9 | Segurança (8%) | 9 |
| Fundamentação (10%) | 8 | Acessibilidade (5%) | 8 |
| Prática (12%) | 8 | Atualidade (5%) | 8 |
| Avaliação (12%) | 6 | Transferência (5%) | 4 |
| Competências (10%) | 8 | Carga cognitiva (5%) | 6 |

## Pontos fortes preservados

- Metáfora "balcão vs chave do arquivo" sustentada da abertura ao fecho.
- Única das 7 aulas com "Quando NÃO usar" plenamente explícito no debriefing (function calling simples vs MCP).
- Segurança de ponta: tool poisoning/rug pull, confused deputy (com a referência primária de Hardy 1988), excessive scope, injeção→tool abuse.
- Fecha o circuito com a Aula 2: `ServidorMCP(barramento=)` publica cada `RegistroAuditoria` em `ferramenta.invocada`.

## Problemas encontrados

### Crítico (reclassificado após verificação própria — ver nota)
- **Bloco de saída de `main_escopo.py` contém uma linha que o programa nunca produz.** Evidência: `aula-03-mcp-integracao.html:392-393`:
  ```
  consultar_ocorrencias_similares({'natureza': 'Furto', 'regiao': 'Asa Norte', 'dias': 15})
      -> [PCDF-SIM-2001 (Furto, Asa Norte), PCDF-SIM-2002 (Furto, Asa Norte)]
  ```
  **Execução real** (`python main_escopo.py`, capturada nesta auditoria):
  ```
  consultar_ocorrencias_similares({...}) -> [{'protocolo': 'PCDF-SIM-2001', 'natureza': 'Furto', 'regiao': 'Asa Norte', 'dias_atras': 2, 'resumo': 'Furto de bicicleta em garagem de prédio, sem arrombamento.'}, {'protocolo': 'PCDF-SIM-2002', ...}]
  ```
  A notação `PCDF-SIM-2001 (Furto, Asa Norte)` não existe em nenhum `print`/`f-string` do código — é uma paráfrase manual apresentada dentro de um `<pre>` que, em todo o resto do bloco, é saída literal (linhas `INFO`, trilha de auditoria). **Nota de avaliação:** os *valores* estão corretos (é uma execução real reescrita à mão, não inventada), e o bloco irmão de `main.py` (linha 291) já se rotula "(bloco de enriquecimento resumido)" — mas este bloco (`main_escopo.py`, linha 382) **não tem esse aviso**. Por isso trato como violação da regra "nunca fabricar saída de terminal" (CLAUDE.md §40) mesmo sem má-fé, e mantenho como bloqueio de publicação até corrigido — a letra da RUBRICA §6 não distingue "fabricação por erro de transcrição" de "fabricação deliberada". Impacto: um aluno que rodar o comando e comparar não vai encontrar essa linha em lugar nenhum, e vai duvidar da própria execução. Correção: colar a saída verbatim (a lista de dicts completa) ou rotular o bloco "(saída resumida)" como o irmão já faz, mantendo ao menos um dicionário completo para o aluno reconhecer o formato real.

### Altos
- **Sem transferência distinta.** Bloco 8 e Desafio do Bloco 6 ficam no domínio SIGMA. Correção: servidor MCP de bens apreendidos (abaixo).
- **Demonstração não mostra o gate de confirmação humana em ação.** `consultar_veiculo` é `sensivel=True`, mas `main.py` usa `confirmar=_auto_sim` por padrão — o aluno só vê a confirmação humana no lab intermediário/teste, não na primeira demonstração do mecanismo central da aula. Correção: usar um `confirmar` que imprime `[operador] aprovar consultar_veiculo(...)? -> sim` na demo.

### Médios
- Objetivos fora do formato-modelo; falta objetivo de nível "avaliar" (o Desafio pede avaliar riscos de descoberta de servidores).
- Sem diagnóstico da Aula 2.
- Referência ao SDK MCP não avisa explicitamente que a API mudou de `FastMCP` para `MCPServer` na v2 (o texto só diz "a API muda entre versões maiores").

### Baixos
- Referência de "confused deputy" aponta para a Wikipedia; o paper primário (Hardy, N., ACM SIGOPS OSR 22(4), 1988) tem DOI e deveria ser a citação principal.
- `_resumir()` em `app/servidor_mcp.py` assume `"encontrado"` presente no dict — robustez, não bug atual.

## Alterações realizadas (Fase 3 — 2026-08-30)

1. **(Bloqueante resolvido)** A saída de `main_escopo.py` no HTML foi substituída pela execução real, verbatim (linha-quebrada só por largura, como o resto do bloco já fazia) — a notação inventada `[PCDF-SIM-2001 (Furto, Asa Norte), ...]` não existe mais na página. O bloco de `main.py` também passou a mostrar o dicionário completo no "enriquecimento" (antes abreviado como `consultar_veiculo(...) -> consta alerta de furto (simulado)`), e o rótulo "(bloco de enriquecimento resumido)" foi removido por não ser mais necessário.
2. **`main.py` agora mostra o gate de confirmação humana de verdade** (achado Alto A3-3): `ClienteMCP` passou a receber um `confirmar=_operador_aprova` que imprime `[operador] aprovar consultar_veiculo(...)? -> sim` antes da chamada sair — antes a demonstração usava o `_auto_sim` silencioso por padrão e o aluno só via o mecanismo central da aula no lab intermediário. Saída do HTML recapturada com essa linha.
3. Adicionada seção **Transferência** distinta no Bloco 8: projetar um servidor MCP para bens apreendidos (tools, escopo por perfil, por que escrita não pertence a um servidor de consulta), com orientação no gabarito e item no checklist.
4. Objetivos reescritos no formato observável + 1 objetivo de nível **Avaliar** (riscos de um servidor MCP e mitigações).
5. Diagnóstico rápido (3 min) da Aula 2 no início do Bloco 1.
6. Referência do SDK MCP agora avisa explicitamente que o trecho vale para a série `1.x` (a pinada em `requirements-opcionais.txt`) e que a `2.x` renomeou `FastMCP` para `MCPServer`.
7. Referência de "confused deputy" trocada da Wikipedia para o paper primário (Hardy, N., ACM SIGOPS OSR 22(4), 1988, DOI 10.1145/54289.871709).
8. Bloco 2 aliviado: a tabela "function calling na mão × MCP" passou a ser marcada como reforço de leitura, não detalhamento ao vivo (mantida na página — só a orientação de apresentação mudou). Bloco 6 (Desafio) com nota priorizando os itens 1–3 em 25 min.
9. Tempos redistribuídos para caber as adições em 300 min: Bloco 2 55→50, Bloco 6 30→25, Bloco 8 20→30. Agenda, cabeçalhos e gabarito conferem entre si.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 10 passed (revalidado após a mudança em `main.py`) |
| Execução principal (`main.py`, `main_escopo.py`) | **PASS** — saída recapturada e conferida verbatim contra o HTML |
| Demos (`solucao_exercicios.py`) | **PASS** |
| HTML — fidelidade da saída de terminal | **PASS** (corrigido — ver item 1 acima) |
| HTML sanity | **PASS** — balanço de tags conferido após as edições |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **PASS** (reescritos, com objetivo de nível Avaliar) |
| Prática | **PASS** (reforçada — gate de confirmação agora visível na demo) |
| Avaliação | **PASS** (diagnóstico e transferência adicionados) |
| Transferência | **PASS** (seção distinta, domínio novo) |
| Segurança | **PASS** (ponto mais forte da aula) |
| Carga horária | **PASS** (25+50+50+45+15+45+25+15+30=300) |

## Nota final (estimada após as correções): **8,3 / 10** — reavaliação formal por agente de QA independente recomendada antes da publicação definitiva

## Veredito: 🟢 APROVADA — bloqueio técnico resolvido (sujeita a confirmação por QA independente)

## Plano de correção priorizado

~~1. (Bloqueante) Recapturar/rotular a saída de `main_escopo.py`~~ ✅ feito.
~~2. Seção "Transferência" (servidor MCP de bens apreendidos)~~ ✅ feito.
~~3. Demonstração com o gate de confirmação visível~~ ✅ feito.
~~4. Objetivos no formato-modelo + objetivo "avaliar" + diagnóstico da Aula 2~~ ✅ feito.
~~5. Aviso de versão do SDK MCP + referência primária do confused deputy~~ ✅ feito.

Pendente, de baixa prioridade (não bloqueia publicação): robustez de `_resumir()` em `app/servidor_mcp.py` para dicts sem a chave `"encontrado"` — nota de robustez, não bug observado em uso atual.

---

# Aula 4 — Engenharia de Agent Loops

`aulas/aula-04-agent-loops.html` · `codigo/aula-04-agent-loops/` (10 testes)

## Nota inicial: 7,7 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6,5 | Qualidade técnica (10%) | 8,5 |
| Organização (8%) | 9,0 | Segurança (8%) | 9,0 |
| Fundamentação (10%) | 8,5 | Acessibilidade (5%) | 7,0 |
| Prática (12%) | 8,5 | Atualidade (5%) | 8,5 |
| Avaliação (12%) | 6,5 | Transferência (5%) | 5,0 |
| Competências (10%) | 8,0 | Carga cognitiva (5%) | 6,5 |

## Pontos fortes preservados

- Segurança exemplar e contextualizada: OWASP LLM10 (consumo ilimitado) e LLM06 (autonomia excessiva) amarrados ao `Orcamento` e níveis de autonomia; injeção pelo traço.
- Decisão arquitetural certa e ensinada como tal: os limites são checados pelo loop (código determinístico), nunca pelo LLM — e a aula explica por quê.
- Continuidade forte: recupera `max_passos` (Aula 1), o roteiro fixo da Aula 3, a trava anti-loop da Aula 2; prepara a coordenação da Aula 5.
- Código fiel ao HTML: saídas comparadas batem, mock determinístico, retry distingue erro transitório de determinístico.

## Problemas encontrados

### Altos
- **Sem diagnóstico da Aula 3.** Bloco 1 só recapitula narrativamente. A aula depende de "spec de ferramenta", "roteiro fixo" e "cliente MCP" — sem checagem, quem chegou frágil na Aula 3 trava aqui.
- **Sem transferência distinta.** "Exercício prático" (SEM_PROGRESSO) e "Desafio" (política de autonomia) ficam no mesmo contexto SIGMA/investigação.

### Médios
- **Checkpoint 1 diz "9 testes"** (`:316`); execução real: **10 passed**. Corrigir.
- **`AVISO_DADOS` não aparece como aviso visível na página** (só a tag "dados sintéticos"); o bloco de saída de `main.py` no HTML também omite a primeira linha real (`* Todos os dados desta aula são FICTÍCIOS...`) que o script imprime — as outras 6 aulas mantêm essa linha no bloco de saída.
- Objetivo 3 diz "todos os critérios de parada: passos, chamadas, custo, tempo, repetição" (5 itens); o conteúdo ensina **7**. Alinhar o texto do objetivo.
- Marcadores "Contexto didático"/"Em produção seria necessário" (PADRAO §17) não rotulam explicitamente o `MockReAct` nem o `custo` abstrato, embora "Protótipo ≠ produção" apareça no debriefing.
- Bloco 2 (55 min) cobre 6 subtemas (ciclo, ReAct, parsing frágil, 7 critérios, autonomia, retry) sem checkpoint intermediário — tempo real esperado estourado; o próprio gabarito já sugere cortes.

### Baixos
- `×` em `main_limites.py:353` (vide seção "Problemas técnicos recorrentes").
- Trecho de `orcamento.py` no HTML referencia `self._inicio` sem mostrar o campo/`iniciar()` — rotular "(trecho)".

## Alterações realizadas (Fase 3 — 2026-08-30)

1. Objetivos reescritos no formato observável; corrigido "5 critérios de parada" no objetivo (agora diz "7 (5 de orçamento + 2 de segurança)", consistente com o conteúdo); acrescentado objetivo de nível **Avaliar/Justificar** (política de autonomia).
2. Diagnóstico rápido (3 min) da Aula 3 no início do Bloco 1.
3. Adicionada seção **Transferência** distinta no Bloco 8: orçamento e autonomia para um agente de ouvidoria (contexto de alto volume/baixo risco, ao contrário da investigação), com orientação no gabarito e item no checklist.
4. **Checkpoint corrigido: "9 testes" → "10 testes"** (contagem real).
5. **Banner `AVISO_DADOS` recolocado** na saída de `main.py` no HTML — o script sempre o imprimeu; só o bloco do HTML o omitia, diferente das demais 6 aulas.
6. Rótulos protótipo × produção acrescentados junto ao `MockReAct` (explicitando que o `custo` de cada ferramenta é didático/arbitrário, não medido) e ao trecho de `orcamento.py` (agora rotulado "trecho", explicando de onde vem `_inicio`).
7. Caractere `×` removido de `main_limites.py` (mensagem "falha 2×, recupera na 3ª" → "falha 2x, recupera na 3a") e do bloco correspondente no HTML — cumpre CLAUDE.md §39.
8. Bloco 2 aliviado: tabela de autonomia e distinção de retry marcadas como leitura rápida (o lab é onde o aluno vê cada limite disparar de verdade); acrescentado um checkpoint intermediário no meio do bloco. Bloco 6 prioriza os itens 1–3 do desafio em 25 min.
9. Tempos redistribuídos para caber as adições em 300 min: Bloco 2 55→50, Bloco 6 30→25, Bloco 8 20→30. Agenda, cabeçalhos e gabarito conferem entre si.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 10 passed; checkpoint agora diz "10 testes" (consistente) |
| Execução principal (`main.py`, `main_limites.py`) | **PASS** — saída recapturada e conferida contra o HTML, incluindo o banner AVISO_DADOS |
| Demos (`solucao_exercicios.py basico`) | **PASS** |
| HTML sanity | **PASS** — balanço de tags conferido após as edições |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **PASS** (reescritos, com objetivo de nível Avaliar) |
| Prática | **PASS** |
| Avaliação | **PASS** (diagnóstico e transferência adicionados) |
| Transferência | **PASS** (seção distinta, domínio novo) |
| Segurança | **PASS** |
| Carga horária | **PASS** (25+50+50+45+15+45+25+15+30=300); Bloco 2 aliviado + checkpoint intermediário |

## Nota final (estimada após as correções): **8,3 / 10** — reavaliação formal por agente de QA independente recomendada antes da publicação definitiva

## Veredito: 🟢 APROVADA (sujeita a confirmação por QA independente)

## Plano de correção priorizado

~~1. Diagnóstico da Aula 3 no Bloco 1~~ ✅ feito.
~~2. Seção "Transferência"~~ ✅ feito.
~~3. Objetivos no formato-modelo + corrigir "5 critérios"→7~~ ✅ feito.
~~4. Corrigir "9 testes"→10; recolocar o banner AVISO_DADOS; rótulos protótipo×produção~~ ✅ feito.
~~5. Aliviar Bloco 2~~ ✅ feito.

Pendente, de baixa prioridade (não bloqueia publicação): URL de referência OpenAI function calling (`developers.openai.com/...`) não reverificada nesta rodada.

---

# Aula 5 — Padrões de Orquestração Multiagente

`aulas/aula-05-orquestracao.html` · `codigo/aula-05-orquestracao/` (13 testes)

## Nota inicial: 7,8 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6,5 | Qualidade técnica (10%) | 8,0 |
| Organização (8%) | 9,0 | Segurança (8%) | 8,5 |
| Fundamentação (10%) | 9,0 | Acessibilidade (5%) | 7,0 |
| Prática (12%) | 8,5 | Atualidade (5%) | 8,5 |
| Avaliação (12%) | 6,5 | Transferência (5%) | 5,5 |
| Competências (10%) | 8,5 | Carga cognitiva (5%) | 6,0 |

## Pontos fortes preservados

- Comparação baseada em números reais: `main_comparar.py` reproduzido **verbatim** nesta auditoria (custo 9/14, latências simuladas, debate discordando na rodada 1 e convergindo na 2) — o padrão de "evidência, não impressão" do curso, no seu melhor.
- Fundamentação forte com atribuição histórica: Hayes-Roth 1985 (DOI válido), Du et al. 2023, AutoGen, EIP — cada padrão ancorado numa fonte primária.
- Debate honesto: mock mostra discordância real (Roubo 0,80 × Furto 0,55) e convergência só depois de ler o argumento do outro.
- Continuidade: a Aula 6 consome esta aula diretamente ("os padrões, agora como grafos").

## Problemas encontrados

### Altos
- **Sem diagnóstico da Aula 4.** O Supervisor é apresentado como "o loop ReAct da Aula 4 onde as ferramentas são os especialistas" — se a Aula 4 não foi consolidada, o padrão 2 inteiro desaba, sem checagem prévia.
- **Sem transferência distinta.** Exercício prático (híbrido) e Desafio (orquestração do SIGMA) variam a *carga*, não o *domínio*.

### Médios
- **Checkpoint 1 diz "10 testes"** (`:331`); execução real: **13 passed**. Corrigir.
- **`supervisor_com_teto()` é função aninhada dentro de `desafio()`** em `solucao_exercicios.py` (linha 68), mas o HTML (`:397-404`) a trata como igualmente "estudável" ao lado de `escolher_padrao()` e `lab_barramento()` (que são de módulo). Um aluno que tentar `from solucao_exercicios import supervisor_com_teto` falha. Ajustar o texto ou promover a função.
- Marcadores protótipo×produção não rotulam explicitamente `MockLLM`/latências simuladas, embora "Protótipo ≠ produção" apareça.
- Bloco 2 (55 min, 5 padrões × diagrama+prós/contras+métricas) é o mais denso das 7 aulas — o gabarito já sugere "3 a fundo + 2 pela tabela"; tornar isso o padrão, não a exceção.

### Baixos
- Tabela comparativa (8×6) pode exigir scroll horizontal em telas estreitas — está dentro de `.tabela-wrap`, então não quebra o layout, mas conferir legibilidade.
- `main.py` (distinto de `main_comparar.py`) não é citado no HTML — verificar se é ponto de entrada morto.

## Alterações realizadas (Fase 3 — 2026-08-30)

1. Objetivos reescritos no formato observável; O5 explicitado como nível **Avaliar** ("Avaliar e escolher... justificando por custo/latência/qualidade").
2. Diagnóstico rápido (3 min) da Aula 4 no início do Bloco 1.
3. Adicionada seção **Transferência** distinta no Bloco 8: escolher padrão de orquestração para uma central de despacho de viaturas (volume que dobra à noite, onde entraria o Debate), com orientação no gabarito e item no checklist.
4. **Checkpoint corrigido: "10 testes" → "13 testes"** (contagem real).
5. **`supervisor_com_teto()` promovida a função de módulo** em `solucao_exercicios.py` (antes aninhada dentro de `desafio()`) — agora é de fato importável, como o texto do HTML já sugeria ao lado de `escolher_padrao()` e `lab_barramento()`. Confirmado com `from solucao_exercicios import supervisor_com_teto`.
6. Bloco 2 aliviado: nota explícita adotando "3 padrões a fundo (Pipeline, Supervisor, Debate) + 2 pela tabela (Broker, Blackboard)" como padrão, não só como plano de contingência; checkpoint intermediário inserido após o Supervisor. Bloco 6 prioriza os itens 1–3 do desafio em 25 min.
7. Tempos redistribuídos para caber as adições em 300 min: Bloco 2 55→50, Bloco 6 30→25, Bloco 8 20→30. Agenda, cabeçalhos e gabarito conferem entre si.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 13 passed; checkpoint agora diz "13 testes" (consistente) |
| Execução principal (`main_comparar.py`, `main_comparar.py PCDF-SIM-0009`) | **PASS** — saída verbatim confere |
| Demos (`solucao_exercicios.py`) | **PASS** — `supervisor_com_teto` confirmado importável |
| HTML sanity | **PASS** — balanço de tags conferido após as edições |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **PASS** (reescritos, O5 explicitado como Avaliar) |
| Prática | **PASS** |
| Avaliação | **PASS** (diagnóstico e transferência adicionados) |
| Transferência | **PASS** (seção distinta, domínio novo — despacho de viaturas) |
| Segurança | **PASS** |
| Carga horária | **PASS** (25+50+50+45+15+45+25+15+30=300); Bloco 2 com estratégia de priorização explícita + checkpoint intermediário |

## Nota final (estimada após as correções): **8,4 / 10** — reavaliação formal por agente de QA independente recomendada antes da publicação definitiva

## Veredito: 🟢 APROVADA (sujeita a confirmação por QA independente)

## Plano de correção priorizado

~~1. Diagnóstico da Aula 4 no Bloco 1~~ ✅ feito.
~~2. Seção "Transferência"~~ ✅ feito.
~~3. Objetivos no formato-modelo~~ ✅ feito.
~~4. Corrigir "10 testes"→13; resolver a promoção de `supervisor_com_teto()`~~ ✅ feito.
~~5. Tornar padrão a estratégia "3 padrões a fundo + 2 pela tabela"~~ ✅ feito.

Pendente, de baixa prioridade (não bloqueia publicação): `main.py` (distinto de `main_comparar.py`) não é citado no HTML — verificar se é ponto de entrada morto; scroll horizontal da tabela 8×6 em telas estreitas (não testado nesta rodada).

---

# Aula 6 — Modelagem de Sistemas Baseados em Grafos

`aulas/aula-06-grafos-langgraph.html` · `codigo/aula-06-grafos-langgraph/` (10 testes)

## Nota inicial: 7,5 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6,5 | Qualidade técnica (10%) | 8,0 |
| Organização (8%) | 8,5 | Segurança (8%) | 8,5 |
| Fundamentação (10%) | 8,5 | Acessibilidade (5%) | 7,5 |
| Prática (12%) | 8,0 | Atualidade (5%) | 6,5 |
| Avaliação (12%) | 6,0 | Transferência (5%) | 5,5 |
| Competências (10%) | 8,0 | Carga cognitiva (5%) | 7,0 |

## Pontos fortes preservados

- `caminho` como observabilidade "de graça": instrumentação concreta, testada, reaproveitada no aviso responsável ("o grafo é a rota, não o veredito").
- Contraexemplos lado a lado: `main_ciclo.py` roda DAG × ciclo controlado × ciclo sem saída (execução confirmada verbatim nesta auditoria).
- Ponte conceito→tecnologia explícita: tabela "motor mínimo × LangGraph" + `langgraph_real/grafo_lg.py` rodando o mesmo grafo do SIGMA com o pacote real (instalado e testado nesta auditoria).
- Continuidade: recupera os 5 arquivos da Aula 5, arma a Aula 7 (item 4 do desafio já pergunta "onde entraria um nó que espera humano?").

## Problemas encontrados

### Altos
- **Sem diagnóstico da Aula 5.** Bloco 1 recapitula o Supervisor em prosa, sem checar se "estado compartilhado"/"Dossiê"/"trava de passos" (pré-requisitos declarados) estão consolidados.
- **Sem transferência distinta.** O item mais próximo (Desafio "Supervisor como grafo") é *near-transfer* dentro do mesmo curso, não um domínio novo.

### Médios
- **Checkpoint 1 e `README.md` dizem "9 testes"**; execução real: **10 passed** (o teste extra é `test_roteador_que_devolve_no_inexistente_falha_em_runtime`). Corrigir nos dois lugares.
- **Bloco de saída de `python main.py` (`:283-299`) é um composto de 3 execuções**, anotado com comentários `#` que a saída real não tem, e **omite a linha `enriquec..:`** que o programa de fato imprime em cada execução. Os valores de `caminho`/`passos` conferem — não é fabricação de conteúdo, mas falta o marcador "(saída composta/anotada)".
- **Sem rubrica para o Desafio** (converter o Supervisor em grafo).
- Objetivo 3 ("Construir um motor de grafo") descreve mais do que a prática pede (o motor já vem pronto; o aluno estende/valida) — ajustar o verbo.
- URL de referência do LangGraph (`langchain-ai.github.io/langgraph/`) redireciona para um domínio novo (`docs.langchain.com/...`) — atualizar; `requirements-opcionais.txt` fixa `langgraph>=0.2` sem teto, e o texto "testado com langgraph 0.2+" está desatualizado frente à versão atual da lib.
- Bloco 2 apresenta ~13 termos novos em 55 min (nó, aresta, DAG, ciclo, condição de saída, roteador, estado compartilhado, START/END, StateGraph, reducer, recursion_limit, checkpointing) — mover o vocabulário específico do LangGraph para "você usa na Aula 7".

### Baixos
- `×` em `main_ciclo.py:36` e travessão `—` em vários `print()` (vide seção recorrente).
- Estilo inline repetido nos blocos de exercício em vez de classe CSS.

## Alterações realizadas

Nenhuma nesta fase.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 10 passed (HTML e README dizem 9 — **FAIL** de consistência) |
| Execução principal (`main.py` com 3 ocorrências) | **PASS** — valores batem |
| Demos (`main_ciclo.py`, `solucao_exercicios.py`, `langgraph_real/grafo_lg.py` opcional) | **PASS** |
| HTML sanity | **PASS** |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **FAIL** |
| Prática | **PASS** |
| Avaliação | **FAIL** |
| Transferência | **FAIL** |
| Segurança | **PASS** |
| Carga horária | **PASS** (25+55+50+45+15+45+30+15+20=300) |

## Nota final = Nota inicial: **7,5 / 10**

## Veredito: 🟡 APROVADA COM AJUSTES

## Plano de correção priorizado

1. Diagnóstico da Aula 5 no Bloco 1.
2. Seção "Transferência" (ver propostas).
3. Rubrica do Desafio.
4. Objetivos no formato-modelo + ajustar objetivo 3.
5. Corrigir "9 testes"→10 (HTML + README); marcar o bloco de `main.py` como composto/anotado; `×`/`—` fora dos `print()`.
6. Atualizar URL do LangGraph + pinar versão + revalidar `grafo_lg.py`.
7. Aliviar Bloco 2 (vocabulário LangGraph → "prévia da Aula 7").

**3 problemas de transferência propostos:** (1) **fluxo do 190** como grafo (ciclo "aguardando confirmação de endereço", condição de saída, trava); (2) converter um procedimento de 40 linhas de `if/elif` em grafo e identificar um ramo inalcançável que `validar()` pegaria; (3) ordem-dependência entre dois nós que escrevem o mesmo campo — resolver no motor mínimo e comparar com o reducer do LangGraph.

---

# Aula 7 — Agentes Especializados e Human-in-the-Loop

`aulas/aula-07-especializados-hitl.html` · `codigo/aula-07-especializados-hitl/` (9 testes)

## Nota inicial: 7,6 / 10

| Dimensão (peso) | Nota | Dimensão (peso) | Nota |
|---|---:|---|---:|
| Objetivos (10%) | 6,5 | Qualidade técnica (10%) | 8,0 |
| Organização (8%) | 8,5 | Segurança (8%) | 9,0 |
| Fundamentação (10%) | 8,5 | Acessibilidade (5%) | 7,5 |
| Prática (12%) | 8,0 | Atualidade (5%) | 6,5 |
| Avaliação (12%) | 6,0 | Transferência (5%) | 5,5 |
| Competências (10%) | 8,5 | Carga cognitiva (5%) | 7,5 |

## Pontos fortes preservados

- Segurança é o núcleo, não apêndice: o breakpoint É o mecanismo de autoridade humana; os 3 painéis de risco (PII no checkpoint, aprovação sem leitura, quem pode aprovar) são contextualizados com EU AI Act art. 14 + LGPD art. 20 + OWASP LLM06.
- Persistência demonstrada de verdade: `main_retomar.py` — um processo encerra de fato, outro processo lê o checkpoint do disco e retoma com a memória dos agentes intacta (confirmado nesta auditoria).
- Separação de responsabilidades comprovada em teste (`test_separacao_de_responsabilidades_cada_agente_uma_chave`).
- Honestidade sobre o protótipo: tabela de tipificação rotulada "DIDÁTICA e simplificada — não é orientação jurídica"; "Falta: store real, fila de aprovações, notificação, expiração de breakpoint".
- Fecha o arco 4–7 no fechamento (loop → papéis → grafo → HITL → checkpoint → Auditor) com handoff explícito para a Aula 8.

## Problemas encontrados

### Altos
- **Sem diagnóstico da Aula 6.** A aula assume "grafo", "estado compartilhado" e "trava de passos" sem checar — a persistência de estado só faz sentido se o aluno lembra o que está sendo persistido.
- **Sem transferência distinta.** O Desafio ("regra de onde vai o breakpoint" aplicada a vínculos/difusão/priorização do SIGMA) é bom raciocínio, mas permanece em segurança pública.

### Médios
- Sem rubrica para o Desafio (2º breakpoint).
- Objetivo "Distinguir human-in-the-loop de human-on-the-loop" é só conceitual — não tem prática dedicada na matriz (só a pergunta 4 da Avaliação).
- **Bloco de saída de `python main.py` (`:267-278`) omite duas chaves reais**: `'considerou_nota_do_operador': None` na proposta e `'quando': <timestamp>` em cada decisão humana. Valores dos demais campos conferem; o timestamp é não-determinístico por natureza (`datetime.now()`), então nunca poderia ser verbatim — vale anotar isso explicitamente.
- Travessão `—` em vários `print()` (`main.py`, `main_retomar.py`, `solucao_exercicios.py`).

### Baixos
- `main.py` grava checkpoints reais em `saida/` a cada execução (não em `tmp_path` como os testes) — acumula JSON sintético entre execuções; `.gitignore` local cobre, mas um `--limpar` ajudaria.
- URL de referência do LangGraph redireciona (mesmo problema da Aula 6); `interrupt()`/`Command(resume=...)` aparecem só como conceito, sem código executável — aceitável, mas vale dizer isso explicitamente no texto.

## Alterações realizadas

Nenhuma nesta fase.

## Validação técnica

| Item | Resultado |
|---|---|
| Testes (`pytest -q`) | **PASS** — 9 passed (bate com HTML e README) |
| Execução principal (`main.py`, `main.py PCDF-SIM-0002 rejeitar`) | **PASS** |
| Demos (`main_retomar.py iniciar` + `aprovar <cid>` em processos separados) | **PASS** — retomada cross-processo comprovada de verdade |
| HTML sanity | **PASS** |

## Validação pedagógica

| Item | Resultado |
|---|---|
| Objetivos | **FAIL** |
| Prática | **PASS** |
| Avaliação | **FAIL** |
| Transferência | **FAIL** |
| Segurança | **PASS** (ponto mais forte da aula) |
| Carga horária | **PASS** (25+55+50+45+15+45+30+15+20=300) |

## Nota final = Nota inicial: **7,6 / 10**

## Veredito: 🟡 APROVADA COM AJUSTES

## Plano de correção priorizado

1. Diagnóstico da Aula 6 no Bloco 1.
2. Seção "Transferência" (ver propostas — a única do conjunto com potencial de sair de segurança pública).
3. Rubrica do 2º breakpoint.
4. Objetivos no formato-modelo; resolver o objetivo HITL×HOTL (micro-prática ou rebaixar o verbo).
5. Mostrar o dict completo no bloco "Rodando" ou marcar abreviação + observar que o timestamp varia.
6. `—`→`-` nos `print()`; nota explícita "sem execução de LangGraph nesta aula, só conceito".

**3 problemas de transferência propostos:** (1) **resposta a incidentes de TI** (fora de segurança pública) — onde vai o breakpoint quando o Recomendador propõe "isolar a máquina X"; (2) checkpoint com PII sensível de um fluxo de benefício social — 5 mudanças concretas no `Checkpoint`, priorizadas; (3) fadiga de aprovação em escala (2.000 autos/dia) — desenhar amostragem/limiar sem perder controle humano real.

---

## Notas finais sobre o método desta auditoria

- Todas as suítes de teste e os `main*.py`/`solucao_exercicios.py` principais das 7 aulas foram executados em venvs efêmeros (Python 3.10.11, Windows), limpos ao final de cada aula (`.venv`, `__pycache__`, `.pytest_cache`, `saida/`). Nenhum resíduo ficou no repositório.
- O caminho opcional de cada aula (`mcp_real/`, `grpc_demo/`, MQTT, `langgraph_real/`) foi verificado onde possível: `langgraph_real/grafo_lg.py` (Aula 6) rodou com sucesso após `pip install langgraph`; o MQTT (Aula 2) falhou por uma lacuna real de instrução (ver Aula 2, Alto); `mcp_real/` e `grpc_demo/` não foram reverificados nesta rodada (já haviam sido testados em QA anterior, registrado na memória do projeto).
- Os 5 documentos de governança (`DESIGN_INSTRUCIONAL.md`, `RUBRICA_AULAS.md`, `PADRAO_AULAS.md`, `GUIA_AVALIACAO.md`, `CHECKLIST_PUBLICACAO.md`) e `CLAUDE.md` foram lidos no estado atual do disco e **não foram alterados** por esta auditoria.
- Nenhum arquivo de `aulas/` ou `codigo/` foi alterado nesta fase.
