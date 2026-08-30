"""Testes do motor de grafo — rodam offline, só com a stdlib."""

from __future__ import annotations

import pytest

from app.bases_sinteticas import OCORRENCIAS
from app.estado import Estado
from app.grafo import END, START, Grafo, GrafoInvalido
from app.sigma_grafo import construir


def executar(oc_id):
    return construir().compilar().executar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))


def test_grafo_valido_compila():
    construir().validar()   # não levanta


def test_no_sem_aresta_de_saida_e_invalido():
    g = Grafo().no("x", lambda e: e)
    g.aresta(START, "x")
    with pytest.raises(GrafoInvalido):
        g.validar()


def test_aresta_para_no_inexistente_e_invalida():
    g = Grafo().no("x", lambda e: e)
    g.aresta(START, "x").aresta("x", "fantasma")
    with pytest.raises(GrafoInvalido):
        g.validar()


def test_caminho_furto_simples_passa_pelo_ciclo_uma_vez():
    e = executar("PCDF-SIM-0009")
    # 1ª consulta por região (Asa Sul) não acha nada -> volta -> 2ª busca ampla acha
    assert e.caminho.count("consultar") == 2
    assert e.caminho[-1] == END
    assert e.classificacao["natureza"] == "Furto"


def test_caminho_roubo_com_placa_nao_precisa_do_ciclo():
    e = executar("PCDF-SIM-0002")
    assert e.caminho.count("consultar") == 1     # veículo consta alerta -> enriquecimento útil
    assert e.classificacao["natureza"] == "Roubo"
    assert "consultar" not in e.caminho[e.caminho.index("revisar") + 1:]  # não voltou


def test_relato_confuso_desvia_para_o_humano():
    e = executar("PCDF-SIM-0011")
    assert e.caminho == ["extrair", "classificar", "encaminhar_humano", END]
    assert any("triagem humana" in p for p in e.pendencias)


def test_ciclo_sem_saida_para_na_trava():
    g = Grafo().no("a", lambda e: e).no("b", lambda e: e)
    g.aresta(START, "a").aresta("a", "b").aresta("b", "a")
    e = g.compilar(max_passos=6).executar(Estado(id="x", texto="..."))
    assert e.passos == 6
    assert any("interrompido" in p for p in e.pendencias)


def test_tem_ciclo_detecta_arestas_estaticas():
    g = Grafo().no("a", lambda e: e).no("b", lambda e: e)
    g.aresta(START, "a").aresta("a", "b").aresta("b", "a")
    assert g.tem_ciclo() is True

    g2 = Grafo().no("a", lambda e: e).no("b", lambda e: e)
    g2.aresta(START, "a").aresta("a", "b").aresta("b", END)
    assert g2.tem_ciclo() is False


def test_roteador_condicional_recebe_estado_atualizado():
    # o nó 'classificar' roda ANTES do roteador rota_pos_classificar
    e = executar("PCDF-SIM-0011")   # confuso -> o roteador só sabe disso via e.campos
    assert e.campos["confuso"] is True


def test_roteador_que_devolve_no_inexistente_falha_em_runtime():
    g = Grafo().no("a", lambda e: e)
    g.aresta(START, "a")
    g.aresta_condicional("a", lambda e: "fantasma")
    with pytest.raises(GrafoInvalido):
        g.compilar().executar(Estado(id="x", texto="..."))
