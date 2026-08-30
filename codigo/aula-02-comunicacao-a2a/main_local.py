"""Laboratório principal — pub/sub em memória (roda offline, sem broker).

    python main_local.py

Monta o barramento, liga o Auditor e o Classificador, e o Extrator publica as
5 ocorrências sintéticas. Ninguém chama ninguém diretamente: tudo por eventos.
"""

from __future__ import annotations

import logging

from app.agentes import AgenteAuditor, AgenteClassificador, AgenteExtrator
from app.mensagem import EnvelopeA2A, Performativa
from app.ocorrencias import AVISO_DADOS, OCORRENCIAS_BRUTAS
from app.transporte import BarramentoLocal, ServicoLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def demo_pubsub() -> AgenteAuditor:
    print("\n=== PUB/SUB (assíncrono) ===")
    barramento = BarramentoLocal()
    auditor = AgenteAuditor()
    classificador = AgenteClassificador(barramento)

    barramento.assinar("#", auditor.ao_receber)                    # audita tudo
    barramento.assinar("ocorrencia.extraida", classificador.ao_receber)

    resultados: list[EnvelopeA2A] = []
    barramento.assinar("ocorrencia.classificada", resultados.append)

    AgenteExtrator(OCORRENCIAS_BRUTAS).publicar_todas(barramento)

    print(f"\nEnvelopes entregues: {barramento.entregues}")
    print("Classificações:")
    for env in resultados:
        c = env.conteudo
        marca = "REVISAR" if c["revisao_humana_obrigatoria"] else "ok"
        print(f"  {c['id']}: {c['natureza']:<12} prioridade={c['prioridade']:<6} [{marca}]")
    return auditor


def demo_request_response() -> None:
    print("\n=== REQUEST/RESPONSE (síncrono) ===")
    servico = ServicoLocal()
    classificador = AgenteClassificador(BarramentoLocal())
    servico.registrar("classificador", classificador.responder)

    pedido = EnvelopeA2A.pedir(
        remetente="triagem",
        topico="classificar",
        conteudo={"id": "PCDF-SIM-0002", "natureza": "Roubo",
                  "data_fato": "2026-08-03", "local": "Taguatinga"},
        responder_a="classificar.resposta",
    )
    resposta = servico.chamar("classificador", pedido)
    print(f"  {pedido.resumo()}")
    print(f"  {resposta.resumo()}  ->  {resposta.conteudo}")
    assert resposta.performativa is Performativa.CONFIRM


def main() -> None:
    print(f"* {AVISO_DADOS}")
    demo_request_response()
    auditor = demo_pubsub()
    print("\n=== TRILHA DE AUDITORIA ===")
    print(auditor.imprimir_trilha())


if __name__ == "__main__":
    main()
