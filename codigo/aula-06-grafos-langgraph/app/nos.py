"""As funções-nó do grafo do SIGMA — e os roteadores das arestas condicionais.

Cada nó: recebe `Estado`, faz uma coisa, devolve `Estado`.
Cada roteador: recebe `Estado`, devolve o nome do próximo nó (ou END).
"""

from __future__ import annotations

from .bases_sinteticas import consultar_similares, consultar_veiculo, extrair_campos
from .estado import Estado
from .grafo import END

MAX_ENRIQUECER = 2   # trava do ciclo revisar -> consultar


# --- nós ---------------------------------------------------------------
def extrair(e: Estado) -> Estado:
    e.campos = extrair_campos(e.texto)
    return e


def classificar(e: Estado) -> Estado:
    natureza = "Roubo" if (e.campos or {}).get("tem_violencia") else "Furto"
    e.classificacao = {"natureza": natureza,
                       "prioridade": "alta" if natureza == "Roubo" else "normal"}
    return e


def consultar(e: Estado) -> Estado:
    c = e.campos or {}
    natureza = (e.classificacao or {}).get("natureza")
    achados = []
    if c.get("placa_citada"):
        achados.append(consultar_veiculo(c["placa_citada"]))
    # 1ª tentativa: só a mesma região. 2ª (no ciclo): busca ampla.
    ampla = e.tentativas_enriquecer >= 1
    achados.append({"similares": consultar_similares(c.get("local"), natureza, ampla=ampla),
                    "busca": "ampla" if ampla else "regiao"})
    e.enriquecimento = achados
    e.tentativas_enriquecer += 1
    return e


def _enriquecimento_util(enriquecimento: list | None) -> bool:
    for item in enriquecimento or []:
        if item.get("similares"):
            return True
        if str(item.get("situacao", "")).startswith("consta"):
            return True
    return False


def revisar(e: Estado) -> Estado:
    pend = []
    c = e.campos or {}
    if not c.get("data_fato") or not c.get("local"):
        pend.append("faltam data ou local")
    if not e.tem("enriquecimento"):
        pend.append("sem enriquecimento")
    elif not _enriquecimento_util(e.enriquecimento):
        pend.append("enriquecimento sem resultado")
    e.pendencias = pend
    e.revisado = True
    return e


def encaminhar_humano(e: Estado) -> Estado:
    e.pendencias.append("ENVIADO para triagem humana (relato confuso / dados faltando)")
    return e


# --- roteadores (arestas condicionais) -------------------------------
def rota_pos_classificar(e: Estado) -> str:
    """Relato confuso vai direto para o humano; o resto segue para enriquecer."""
    if (e.campos or {}).get("confuso"):
        return "encaminhar_humano"
    return "consultar"


def rota_pos_revisar(e: Estado) -> str:
    """CICLO: se o enriquecimento não trouxe nada e ainda há tentativas, volta
    para `consultar` (que na 2ª vez faz uma busca mais ampla). Senão, encerra."""
    sem_resultado = "enriquecimento sem resultado" in e.pendencias or "sem enriquecimento" in e.pendencias
    if sem_resultado and e.tentativas_enriquecer < MAX_ENRIQUECER:
        return "consultar"
    return END
