# Broker MQTT (mosquitto) para o laboratório

O `mosquitto.conf` **exige autenticação** (`allow_anonymous false`) — de propósito:
um barramento sem auth deixa qualquer processo publicar eventos falsos.

## Criar o arquivo de senha (uma vez)

```bash
# gera mosquitto/passwd com o usuário 'sigma'
docker run --rm -v "$(pwd)/mosquitto:/m" eclipse-mosquitto:2 \
  mosquitto_passwd -c -b /m/passwd sigma TROQUE_ESTA_SENHA
```

No PowerShell:

```powershell
docker run --rm -v "${PWD}/mosquitto:/m" eclipse-mosquitto:2 `
  mosquitto_passwd -c -b /m/passwd sigma TROQUE_ESTA_SENHA
```

Depois preencha `MQTT_USER=sigma` e `MQTT_PASSWORD=TROQUE_ESTA_SENHA` no `.env`.

## Subir / derrubar

```bash
docker compose up -d
docker compose logs -f mosquitto
docker compose down
```

`mosquitto/passwd` está no `.gitignore` — não versione senhas.
