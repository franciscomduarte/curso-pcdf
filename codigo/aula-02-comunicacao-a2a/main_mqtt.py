"""O mesmo fluxo pub/sub, agora sobre MQTT.

Pré-requisitos:
    pip install -r requirements-opcionais.txt
    docker compose up -d          # sobe o broker mosquitto
    cp .env.example .env          # e ajuste MQTT_USER / MQTT_PASSWORD

    python main_mqtt.py

Os agentes são EXATAMENTE os mesmos de main_local.py — só o transporte muda.
"""

from __future__ import annotations

import logging
import time

from dotenv import load_dotenv

from app.agentes import AgenteAuditor, AgenteClassificador, AgenteExtrator
from app.ocorrencias import AVISO_DADOS, OCORRENCIAS_BRUTAS
from app.transporte_mqtt import BarramentoMQTT

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    barramento = BarramentoMQTT(client_id="sigma-demo")
    barramento.conectar()

    auditor = AgenteAuditor()
    classificador = AgenteClassificador(barramento)  # publica de volta no MQTT

    barramento.assinar("#", auditor.ao_receber)
    barramento.assinar("ocorrencia.extraida", classificador.ao_receber)
    time.sleep(0.5)  # deixa as assinaturas efetivarem no broker

    AgenteExtrator(OCORRENCIAS_BRUTAS).publicar_todas(barramento)
    time.sleep(1.0)  # espera o ida-e-volta assíncrono

    print(f"\nTrilha ({len(auditor.trilha)} envelopes):")
    print(auditor.imprimir_trilha())
    barramento.desconectar()


if __name__ == "__main__":
    main()
