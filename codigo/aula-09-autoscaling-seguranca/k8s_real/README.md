# HPA real, sobre o cluster da Aula 8

`hpa.yaml` é um manifesto `autoscaling/v2` real, que reaplica a mesma ideia de
`app/autoscaler.py::avaliar()` sobre os recursos reais construídos na Aula 8
(`codigo/aula-08-kubernetes/k8s_real/deployment.yaml` + `service.yaml` +
`configmap.yaml`) — a Aula 9 não duplica o Dockerfile/servidor HTTP, só
acrescenta o autoscaler sobre o que já existe.

> **Este manifesto não foi aplicado contra um cluster real nesta sessão** —
> requer um cluster com `metrics-server` instalado (não vem por padrão em
> `kind`/`minikube`), que não está disponível no ambiente onde este material
> foi gerado. A fórmula que ele delega ao Kubernetes (`ceil[réplicas ×
> (métrica_atual / métrica_alvo)]`) é a mesma que `app/autoscaler.py::avaliar()`
> implementa em Python e que os testes (`tests/test_autoscaler.py`) validam —
> o que fica sem verificação real aqui é só a integração com o
> `metrics-server` do Kubernetes, não a lógica.

## Passo a passo (requer Docker + kubectl + um cluster local com metrics-server)

```bash
# 1. montar o cluster e a imagem da Aula 8 (ver k8s_real/README.md de lá)
cd codigo/aula-08-kubernetes
docker build -f k8s_real/Dockerfile -t sigma/juridico:latest .
kind create cluster --name sigma
kind load docker-image sigma/juridico:latest --name sigma
kubectl apply -f k8s_real/configmap.yaml -f k8s_real/deployment.yaml -f k8s_real/service.yaml

# 2. instalar o metrics-server (necessário para qualquer HPA de CPU/memória)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 3. aplicar o autoscaler da Aula 9
cd ../aula-09-autoscaling-seguranca
kubectl apply -f k8s_real/hpa.yaml

# 4. observar
kubectl get hpa juridico-hpa --watch
kubectl describe hpa juridico-hpa
```

## Diferença importante para `app/autoscaler.py`

No motor mínimo, `avaliar()` recebe a carga já calculada (um float) e você
decide o que ela representa. No Kubernetes real, o HPA busca a métrica
sozinho — por padrão, uso de CPU relatado pelo `metrics-server`, coletado a
partir do `kubelet` de cada nó — e reavalia por padrão a cada 15s
(`--horizontal-pod-autoscaler-sync-period` no controller-manager), não a cada
chamada como no `main.py` da aula. Métricas customizadas (filas, latência)
exigem um adaptador adicional (Prometheus Adapter, KEDA), fora do escopo
desta aula.
