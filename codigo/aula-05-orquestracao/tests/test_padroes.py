"""Testes dos 5 padrões — rodam offline, só com pydantic."""

from __future__ import annotations

from app import padroes
from app.bases_sinteticas import OCORRENCIAS
from app.especialistas import Dossie
from app.llm import MockLLM

COMPLEXA = "PCDF-SIM-0002"   # com violência + placa
TRIVIAL = "PCDF-SIM-0009"    # furto simples, sem placa


def novo(oc_id):
    return Dossie(id=oc_id, texto=OCORRENCIAS[oc_id])


def test_todos_os_padroes_de_fluxo_produzem_dossie_completo_na_complexa():
    for orq in (lambda d: padroes.pipeline(d),
                lambda d: padroes.supervisor(d, MockLLM()),
                lambda d: padroes.broker(d),
                lambda d: padroes.blackboard(d)):
        d, m = orq(novo(COMPLEXA))
        assert d.campos and d.classificacao and d.enriquecimento
        assert d.classificacao["natureza"] == "Roubo"
        assert m.especialistas >= 4


def test_pipeline_e_deterministico_e_soma_tudo():
    d1, m1 = padroes.pipeline(novo(COMPLEXA))
    d2, m2 = padroes.pipeline(novo(COMPLEXA))
    assert m1.linha() == m2.linha()
    assert m1.especialistas == 4 and m1.rodadas == 4


def test_supervisor_adapta_pula_consultor_na_trivial():
    d, m = padroes.supervisor(novo(TRIVIAL), MockLLM())
    assert d.enriquecimento is None            # consultor não foi chamado
    assert d.classificacao["natureza"] == "Furto"
    # menos especialistas que na complexa
    d2, m2 = padroes.supervisor(novo(COMPLEXA), MockLLM())
    assert m.especialistas < m2.especialistas


def test_supervisor_custa_chamadas_de_llm_a_mais():
    _, m_pipe = padroes.pipeline(novo(COMPLEXA))
    _, m_sup = padroes.supervisor(novo(COMPLEXA), MockLLM())
    assert m_sup.llm > m_pipe.llm     # +1 por decisão


def test_broker_reordena_pedidos_fora_de_ordem():
    d, m = padroes.broker(novo(COMPLEXA), pedidos=["revisar", "classificar", "extrair", "enriquecer"])
    assert d.campos and d.classificacao and d.completo is not None
    assert not any("não pôde despachar" in p for p in d.pendencias)


def test_broker_sinaliza_dependencia_nao_satisfeita():
    d, m = padroes.broker(novo(COMPLEXA), pedidos=["revisar"])   # sem extrair/classificar antes
    assert any("não pôde despachar" in p for p in d.pendencias)


def test_blackboard_ordem_emergente_mesmo_resultado():
    d, m = padroes.blackboard(novo(COMPLEXA))
    assert d.campos and d.classificacao and d.enriquecimento
    assert m.rodadas <= 6


def test_blackboard_novo_especialista_entra_so_declarando_metadata():
    from app.especialistas import REGISTRO, SpecEspecialista

    def sintetizador(d, mm):
        d.resumo_final = f"{d.classificacao['natureza']} em {d.campos['local']}"
        mm.registrar(especialista=True, custo=1)
        return d

    REGISTRO["sintetizador"] = SpecEspecialista(
        "sintetizador", {"campos", "classificacao"}, "resumo_final", sintetizador)
    try:
        d, _ = padroes.blackboard(novo(COMPLEXA))
        assert getattr(d, "resumo_final", None) == "Roubo em Taguatinga"
    finally:
        del REGISTRO["sintetizador"]


def test_debate_converge_para_roubo_quando_ha_violencia():
    v, m = padroes.debate("Furto ou Roubo?", OCORRENCIAS[COMPLEXA], MockLLM())
    assert v["veredito"]["resposta"] == "Roubo"
    assert m.llm == 2 * 2 + 1        # 2 debatedores x 2 rodadas + juiz


def test_debate_furto_na_trivial():
    v, m = padroes.debate("Furto ou Roubo?", OCORRENCIAS[TRIVIAL], MockLLM())
    assert v["veredito"]["resposta"] == "Furto"


def test_debate_tem_discordancia_real_na_rodada_1():
    v, _ = padroes.debate("Furto ou Roubo?", OCORRENCIAS[COMPLEXA], MockLLM())
    r1 = v["por_rodada"][0]
    assert r1[0]["resposta"] != r1[1]["resposta"]        # promotor x defensor divergem
    assert v["por_rodada"][-1][0]["resposta"] == v["por_rodada"][-1][1]["resposta"]  # convergem


def test_metricas_de_orquestracao_chegam_ao_auditor():
    from app.barramento import Auditor, Barramento

    bus, aud = Barramento(), Auditor()
    bus.assinar("orquestracao.concluida", aud.ao_receber)
    _, m = padroes.pipeline(novo(COMPLEXA))
    bus.publicar("orquestracao.concluida", "orquestrador", {"padrao": "pipeline", "custo": m.custo})
    assert aud.trilha and aud.trilha[0].dados["padrao"] == "pipeline"


def test_hibrido_so_chama_debate_no_conflito():
    from solucao_exercicios import hibrido

    d, ms = hibrido(novo(COMPLEXA))
    assert len(ms) == 1 and d.classificacao["natureza"] == "Roubo"
