"""Testes que rodam sem chave de API (usam o MockExtrator)."""

from __future__ import annotations

from app.agente_extrator import AgenteExtrator
from app.classificador import classificar
from app.dados_sinteticos import OCORRENCIAS_BRUTAS, por_id
from app.esquema import NaturezaOcorrencia, Ocorrencia
from app.llm import MockExtrator
from app.relatorio import consolidar


def _extrair(ocorrencia_id: str) -> Ocorrencia:
    item = por_id(ocorrencia_id)
    return AgenteExtrator(llm=MockExtrator()).processar(item["id"], item["texto"])


def test_saida_valida_e_do_tipo_ocorrencia():
    oc = _extrair("PCDF-SIM-0001")
    assert isinstance(oc, Ocorrencia)
    assert oc.resumo


def test_classifica_furto_sem_arrombamento():
    oc = _extrair("PCDF-SIM-0001")
    assert oc.natureza == NaturezaOcorrencia.FURTO


def test_classifica_roubo_com_simulacro():
    oc = _extrair("PCDF-SIM-0002")
    assert oc.natureza == NaturezaOcorrencia.ROUBO


def test_extrai_data_local_e_placa():
    oc = _extrair("PCDF-SIM-0002")
    assert oc.data_fato == "2026-08-03"
    assert oc.local == "Taguatinga"
    assert any(v.placa == "ABC1D23" for v in oc.veiculos)


def test_estelionato_pix():
    oc = _extrair("PCDF-SIM-0005")
    assert oc.natureza == NaturezaOcorrencia.ESTELIONATO
    assert "LojaTechDF" in oc.entidades_relevantes


def test_consolidacao_conta_todas():
    llm = MockExtrator()
    ocs = [llm.extrair(i["texto"]) for i in OCORRENCIAS_BRUTAS]
    rel = consolidar(ocs)
    assert rel["total"] == len(OCORRENCIAS_BRUTAS)
    assert sum(rel["por_natureza"].values()) == len(OCORRENCIAS_BRUTAS)


def test_retry_propaga_erro_final():
    class SempreFalha:
        def extrair(self, texto: str) -> Ocorrencia:
            raise RuntimeError("simulando indisponibilidade")

    agente = AgenteExtrator(llm=SempreFalha(), tentativas=2, espera_base=0)
    try:
        agente.processar("X", "texto")
        assert False, "deveria ter levantado"
    except RuntimeError as exc:
        assert "falhou" in str(exc)
