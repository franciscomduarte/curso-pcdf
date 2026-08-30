"""BarramentoMQTT — o mesmo pub/sub, agora sobre um broker MQTT.

Requer `paho-mqtt` (requirements-opcionais.txt) e um broker rodando
(`docker compose up -d`, ver docker-compose.yml).

Mapeamento:
  EnvelopeA2A.topico  ->  tópico MQTT  "sigma/<topico com '.' -> '/'>"
  EnvelopeA2A         ->  payload JSON (UTF-8)
  filtro 'ocorrencia.*' -> 'sigma/ocorrencia/+'
  filtro '#' / '*'      -> 'sigma/#'

Os agentes NÃO mudam: `ao_receber(env)` continua igual.
"""

from __future__ import annotations

import json
import logging
import os

from .mensagem import EnvelopeA2A
from .transporte import Assinante

logger = logging.getLogger("sigma.a2a.mqtt")

_PREFIXO = "sigma"


def _para_mqtt(topico: str) -> str:
    return f"{_PREFIXO}/" + topico.replace(".", "/")


def _de_mqtt(topico_mqtt: str) -> str:
    return topico_mqtt.removeprefix(f"{_PREFIXO}/").replace("/", ".")


def _filtro_mqtt(filtro: str) -> str:
    if filtro in ("#", "*"):
        return f"{_PREFIXO}/#"
    return f"{_PREFIXO}/" + filtro.replace(".", "/").replace("*", "+")


class BarramentoMQTT:
    def __init__(self, host: str | None = None, port: int | None = None,
                 client_id: str = "sigma") -> None:
        import paho.mqtt.client as mqtt  # import tardio

        self._host = host or os.getenv("MQTT_HOST", "localhost")
        self._port = port or int(os.getenv("MQTT_PORT", "1883"))
        self._cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

        usuario, senha = os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWORD")
        if usuario:
            self._cli.username_pw_set(usuario, senha)

        self._assinantes: list[tuple[str, Assinante]] = []
        self._cli.on_message = self._on_message

    # -- ciclo de vida --
    def conectar(self) -> None:
        self._cli.connect(self._host, self._port, keepalive=30)
        self._cli.loop_start()

    def desconectar(self) -> None:
        self._cli.loop_stop()
        self._cli.disconnect()

    # -- API de transporte --
    def assinar(self, filtro_topico: str, callback: Assinante) -> None:
        import fnmatch

        self._assinantes.append((filtro_topico, callback))
        self._cli.subscribe(_filtro_mqtt(filtro_topico), qos=1)
        # fnmatch importado só para deixar claro que o roteamento fino é local
        _ = fnmatch

    def publicar(self, envelope: EnvelopeA2A) -> None:
        self._cli.publish(
            _para_mqtt(envelope.topico),
            envelope.model_dump_json(),
            qos=1,
        )

    # -- interno --
    def _on_message(self, _cli, _userdata, msg) -> None:
        import fnmatch

        try:
            env = EnvelopeA2A.model_validate_json(msg.payload)
        except Exception as exc:  # payload inválido no tópico -> descarta e loga
            logger.warning("payload inválido em %s: %s", msg.topic, exc)
            return
        topico = _de_mqtt(msg.topic)
        for filtro, callback in self._assinantes:
            alvo = "*" if filtro == "#" else filtro
            if fnmatch.fnmatch(topico, alvo):
                callback(env)
