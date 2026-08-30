"""Gabarito dos laboratórios da Aula 5.

    python solucao_exercicios.py
"""

from __future__ import annotations

from app import padroes
from app.bases_sinteticas import OCORRENCIAS
from app.especialistas import REGISTRO, Dossie, SpecEspecialista
from app.llm import MockLLM
from app.metricas import Metricas


def _novo(oc_id="PCDF-SIM-0002"):
    return Dossie(id=oc_id, texto=OCORRENCIAS[oc_id])


# ---------------------------------------------------------------------------
# LAB BÁSICO — o mesmo especialista novo entra em vários padrões
# ---------------------------------------------------------------------------
def _sintetizador(d, m):
    d.resumo_final = f"{d.classificacao['natureza']} em {d.campos['local']} ({d.campos['data_fato']})"
    m.registrar(especialista=True, custo=1, latencia_ms=150)
    return d


def lab_basico() -> None:
    print("== LAB BÁSICO: acrescentar um especialista ==")
    REGISTRO["sintetizador"] = SpecEspecialista(
        "sintetizador", {"campos", "classificacao"}, "resumo_final", _sintetizador)
    from app.especialistas import ORDEM_PIPELINE
    ORDEM_PIPELINE.append("sintetizador")
    try:
        for nome, orq in (("pipeline", lambda d: padroes.pipeline(d)),
                          ("blackboard", lambda d: padroes.blackboard(d))):
            d, _ = orq(_novo())
            print(f"  {nome:<11} resumo_final = {getattr(d, 'resumo_final', None)!r}")
        print("  (blackboard nem precisou saber a ordem — só a metadata precisa/produz)")
    finally:
        ORDEM_PIPELINE.remove("sintetizador")
        del REGISTRO["sintetizador"]


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — escolher o padrão pela natureza da carga
# ---------------------------------------------------------------------------
def escolher_padrao(qtde_ocorrencias: int, ambigua: bool):
    if ambigua:
        return "debate + supervisor"
    if qtde_ocorrencias > 100:
        return "pipeline (previsível, barato, paraleliza por lote)"
    return "supervisor (adapta caso a caso, volume baixo)"


def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: qual padrão para qual carga ==")
    for q, amb in [(500, False), (10, False), (1, True)]:
        print(f"  {q:>3} ocorrências, ambígua={amb} -> {escolher_padrao(q, amb)}")


# ---------------------------------------------------------------------------
# DESAFIO — supervisor com orçamento (junta com a Aula 4)
# ---------------------------------------------------------------------------
def supervisor_com_teto(d: Dossie, llm, custo_max: int):
    m = Metricas(padrao="supervisor+teto")
    for _ in range(8):
        m.rodadas += 1
        if m.custo >= custo_max:
            d.pendencias.append(f"orçamento esgotado (custo {m.custo})")
            break
        proximo = llm.decidir(d)
        m.registrar(llm=1, custo=1)
        if proximo == "concluir":
            break
        d = REGISTRO[proximo].funcao(d, m)
    return d, m


def desafio() -> None:
    print("\n== DESAFIO: supervisor que respeita um teto de custo ==")
    d, m = supervisor_com_teto(_novo(), MockLLM(), custo_max=8)
    print(f"  {m.linha()}")
    print(f"  pendências: {d.pendencias}")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO (parte 2) — métricas de orquestração no barramento
# ---------------------------------------------------------------------------
def lab_barramento() -> None:
    print("\n== LAB INTERMEDIÁRIO (2): métricas de orquestração -> Auditor ==")
    from app.barramento import Auditor, Barramento

    bus, auditor = Barramento(), Auditor()
    bus.assinar("orquestracao.concluida", auditor.ao_receber)

    for nome, orq in (("pipeline", lambda: padroes.pipeline(_novo())),
                      ("supervisor", lambda: padroes.supervisor(_novo(), MockLLM()))):
        _, m = orq()
        bus.publicar("orquestracao.concluida", "orquestrador",
                     {"padrao": nome, "custo": m.custo, "latencia_ms": m.latencia_ms})

    for ev in auditor.trilha:
        print(f"    {ev.dados}")
    assert {e.dados["padrao"] for e in auditor.trilha} == {"pipeline", "supervisor"}


# ---------------------------------------------------------------------------
# EXERCÍCIO PRÁTICO (Bloco 8) — padrão híbrido: pipeline + debate no conflito
# ---------------------------------------------------------------------------
def hibrido(d: Dossie) -> tuple[Dossie, list[Metricas]]:
    d, m_pipe = padroes.pipeline(d)
    metricas = [m_pipe]
    conflito = (d.campos.get("tem_violencia") and d.classificacao["natureza"] == "Furto")
    if conflito:
        v, m_deb = padroes.debate("Furto ou Roubo?", d.texto, MockLLM())
        d.classificacao["natureza"] = v["veredito"]["resposta"]
        metricas.append(m_deb)
    return d, metricas


def exercicio_hibrido() -> None:
    print("\n== EXERCÍCIO PRÁTICO: padrão híbrido ==")
    # ocorrência sem conflito -> debate NÃO roda
    d, ms = hibrido(_novo("PCDF-SIM-0002"))
    print(f"  SIM-0002: natureza={d.classificacao['natureza']}, padrões usados={len(ms)}")
    assert len(ms) == 1   # o classificador já acerta Roubo; sem conflito


if __name__ == "__main__":
    lab_basico()
    lab_intermediario()
    lab_barramento()
    desafio()
    exercicio_hibrido()
