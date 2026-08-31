"""Testes dos exercícios extras da Aula 10."""

from __future__ import annotations

import app.roteador as roteador_mod
from app.memoria import Estado
from app.roteador import ETAPA_APROVACAO, ETAPA_REVISAO
from solucao_exercicios import decidir_apos_revisar, decidir_multi_sinal


# -- Extra 1: roteador multi-sinal --------------------------------------

def _estado(natureza="Furto", situacao_veiculo=None, local="Guará"):
    return Estado(
        id="X", texto="...",
        fatos={"campos": {"local": local}, "veiculo": {"situacao": situacao_veiculo} if situacao_veiculo else None},
        tipificacao_proposta={"natureza": natureza},
    )


def test_multi_sinal_roubo_escala():
    assert decidir_multi_sinal(_estado(natureza="Roubo")) == ETAPA_REVISAO


def test_multi_sinal_veiculo_alertado_escala_mesmo_sendo_furto():
    assert decidir_multi_sinal(_estado(natureza="Furto", situacao_veiculo="consta alerta")) == ETAPA_REVISAO


def test_multi_sinal_local_ausente_escala():
    assert decidir_multi_sinal(_estado(natureza="Furto", local=None)) == ETAPA_REVISAO


def test_multi_sinal_furto_simples_vai_direto():
    assert decidir_multi_sinal(_estado(natureza="Furto")) == ETAPA_APROVACAO


# -- Extra 2: aresta condicional na etapa 'revisar' --------------------

def test_decidir_apos_revisar_devolve_ao_juridico_na_divergencia():
    e = Estado(id="X", texto="...", revisao={"concorda": False},
               atendido_por=[{"etapa": "juridico"}, {"etapa": "revisar"}])
    assert decidir_apos_revisar(e) == "juridico"


def test_decidir_apos_revisar_para_apos_uma_reanalise():
    e = Estado(id="X", texto="...", revisao={"concorda": False},
               atendido_por=[{"etapa": "juridico"}, {"etapa": "revisar"},
                             {"etapa": "juridico"}, {"etapa": "revisar"}])
    assert decidir_apos_revisar(e) == ETAPA_APROVACAO   # trava de 1 volta impede loop


def test_decidir_apos_revisar_segue_quando_revisor_concorda():
    e = Estado(id="X", texto="...", revisao={"concorda": True},
               atendido_por=[{"etapa": "juridico"}, {"etapa": "revisar"}])
    assert decidir_apos_revisar(e) == ETAPA_APROVACAO


def test_extra2_nao_deixa_monkeypatch_vazar():
    """A função de gabarito restaura ROTEADORES_CONDICIONAIS; este teste
    confirma que a etapa 'revisar' segue estática por padrão."""
    assert "revisar" not in roteador_mod.ROTEADORES_CONDICIONAIS
