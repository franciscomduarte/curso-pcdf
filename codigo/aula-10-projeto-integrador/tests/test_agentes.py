"""Testes do agente novo desta aula: revisor_dupla."""

from __future__ import annotations

from app.agentes import revisor_dupla
from app.memoria import Estado


def test_revisor_concorda_quando_fatos_sustentam_grave_ameaca():
    e = Estado(
        id="X", texto="...",
        fatos={"campos": {"grave_ameaca": True}},
        tipificacao_proposta={"natureza": "Roubo"},
    )
    e2 = revisor_dupla(e)
    assert e2.revisao["concorda"] is True
    assert "confirma" in e2.revisao["observacao"]


def test_revisor_diverge_quando_fatos_nao_sustentam_grave_ameaca():
    e = Estado(
        id="X", texto="...",
        fatos={"campos": {"grave_ameaca": False}},   # Jurídico disse Roubo, mas os fatos não sustentam
        tipificacao_proposta={"natureza": "Roubo"},
    )
    e2 = revisor_dupla(e)
    assert e2.revisao["concorda"] is False
    assert "diverge" in e2.revisao["observacao"]


def test_revisor_anota_na_propria_memoria():
    e = Estado(id="X", texto="...", fatos={"campos": {"grave_ameaca": True}},
               tipificacao_proposta={"natureza": "Roubo"})
    e2 = revisor_dupla(e)
    assert "revisor" in e2.memorias
    assert len(e2.memorias["revisor"]["notas"]) == 1
