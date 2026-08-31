# Kubernetes de verdade

O mesmo agente Jurídico (`app/agentes.py::juridico`), agora como um servidor
HTTP real (`servidor.py`, só biblioteca padrão) empacotado num container e
implantado com os recursos reais do Kubernetes — `Deployment`, `Service`,
`ConfigMap`.

> **Este caminho não foi executado contra um cluster real nesta sessão** —
> requer Docker e um cluster (kind, minikube ou Docker Desktop com
> Kubernetes ativado), que não estão disponíveis no ambiente onde este
> material foi gerado. `servidor.py` **foi** testado localmente (`python
> k8s_real/servidor.py` + `curl`, sem container) — o núcleo funciona; o que
> não foi verificado é o empacotamento e o deploy no cluster de verdade.
> Os manifestos usam `apps/v1`/`v1`, as versões estáveis atuais das APIs de
> `Deployment`/`Service`/`ConfigMap` desde o Kubernetes 1.9 (2018) — confira
> a documentação oficial (link no rodapé da aula) se estiver numa versão
> muito antiga ou muito nova do cluster.

## Passo a passo (requer Docker + kubectl + um cluster local)

```bash
# 1. construir a imagem
cd codigo/aula-08-kubernetes
docker build -f k8s_real/Dockerfile -t sigma/juridico:latest .

# 2. ter um cluster local (exemplo com kind: https://kind.sigs.k8s.io/)
kind create cluster --name sigma
kind load docker-image sigma/juridico:latest --name sigma

# 3. aplicar os manifestos
kubectl apply -f k8s_real/configmap.yaml
kubectl apply -f k8s_real/deployment.yaml
kubectl apply -f k8s_real/service.yaml

# 4. conferir
kubectl get pods -l app=sigma
kubectl get deployment juridico-deploy
kubectl rollout status deployment/juridico-deploy

# 5. chamar o Service de dentro do cluster (port-forward para testar de fora)
kubectl port-forward svc/juridico-svc 8080:8080
curl -X POST localhost:8080/juridico -H "Content-Type: application/json" \
     -d '{"id":"PCDF-SIM-0002","hipotese":{"natureza_provavel":"Roubo"}}'
```

## Testar `servidor.py` sozinho, sem Docker nem cluster

Isto **foi** executado nesta sessão — saída real:

```bash
python k8s_real/servidor.py &
curl -s localhost:8080/saude
curl -s -X POST localhost:8080/juridico -H "Content-Type: application/json" \
     -d '{"id":"PCDF-SIM-0002","hipotese":{"natureza_provavel":"Roubo"}}'
```

```text
{"status": "ok", "detalhe": "padrao"}
{"artigo": "Art. 157 do CP (roubo)", "natureza": "Roubo", "fundamento": "presença de grave ameaça", "requer_decisao_humana": true, "considerou_nota_do_operador": null}
```

## Diferença importante para o motor mínimo (`app/cluster.py`)

No motor mínimo, o "ConfigMap" é um dicionário lido a cada chamada — muda
em tempo real, sem reiniciar nada (equivalente a um ConfigMap montado como
**volume** no Kubernetes real, que também atualiza sem reiniciar o pod,
com um atraso de sincronização).

Aqui, `servidor.py` lê `DETALHE` de uma variável de ambiente — e variável
de ambiente só é lida quando o processo **inicia**. Para um `ConfigMap`
editado valer com esse padrão, é preciso reiniciar os pods (`kubectl
rollout restart deployment/juridico-deploy`). As duas formas são reais e
comuns; a escolha entre env var e volume monta o trade-off entre
simplicidade (env var) e atualização sem reinício (volume).

## Escalando e atualizando de verdade

```bash
kubectl scale deployment/juridico-deploy --replicas=4
kubectl set image deployment/juridico-deploy juridico=sigma/juridico:v2   # rolling update real
kubectl rollout status deployment/juridico-deploy
kubectl rollout undo deployment/juridico-deploy                          # desfaz, se algo der errado
```
