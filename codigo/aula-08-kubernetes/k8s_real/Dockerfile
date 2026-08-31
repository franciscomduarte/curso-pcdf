# Imagem do agente Jurídico — só biblioteca padrão, imagem base enxuta.
FROM python:3.12-slim

WORKDIR /app
COPY app/ ./app/
COPY k8s_real/servidor.py ./k8s_real/servidor.py

# Sem root: menor privilégio dentro do próprio container (CIS Kubernetes Benchmark 5.2).
RUN useradd --no-create-home --shell /usr/sbin/nologin sigma
USER sigma

EXPOSE 8080
CMD ["python", "k8s_real/servidor.py"]
