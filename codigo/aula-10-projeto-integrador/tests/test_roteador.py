"""Testes da aresta condicional — a peça nova desta aula (Aula 6 + Aula 8/9)."""

from __future__ import annotations

from app.memoria import Estado
from app.roteador import ETAPA_APROVACAO, ETAPA_REVISAO, decidir_apos_juridico


def test_roubo_e_roteado_para_revisao():
    e = Estado(id="X", texto="...", tipificacao_proposta={"natureza": "Roubo"})
    assert decidir_apos_juridico(e) == ETAPA_REVISAO


def test_furto_vai_direto_para_aprovacao():
    e = Estado(id="X", texto="...", tipificacao_proposta={"natureza": "Furto"})
    assert decidir_apos_juridico(e) == ETAPA_APROVACAO


def test_sem_tipificacao_proposta_nao_quebra_e_vai_direto():
    e = Estado(id="X", texto="...")   # tipificacao_proposta é None
    assert decidir_apos_juridico(e) == ETAPA_APROVACAO
