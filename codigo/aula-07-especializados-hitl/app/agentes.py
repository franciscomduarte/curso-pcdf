"""Os quatro agentes especializados.

Separação de responsabilidades — cada agente só escreve a sua chave no Estado
e mantém a sua própria memória:

  Investigador  -> fatos            (extrai campos, consulta bases)
  Analista      -> hipotese         (natureza provável + linha do tempo)
  Jurídico      -> tipificacao_proposta   (+ marca o que EXIGE decisão humana)
  Consolidador  -> tipificacao_final + dossie   (só roda DEPOIS da aprovação)
"""

from __future__ import annotations

from .bases_sinteticas import TIPIFICACOES, consultar_veiculo, extrair_campos
from .memoria import Estado


def investigador(e: Estado) -> Estado:
    m = e.memoria_de("investigador")
    campos = extrair_campos(e.texto)
    m.anotar(f"campos extraídos: {sorted(k for k, v in campos.items() if v)}")
    veiculo = None
    if campos.get("placa_citada"):
        veiculo = consultar_veiculo(campos["placa_citada"])
        m.anotar(f"consulta de veículo {campos['placa_citada']}: {veiculo['situacao']}")
    e.fatos = {"campos": campos, "veiculo": veiculo}
    e.guardar_memoria(m)
    return e


def analista(e: Estado) -> Estado:
    m = e.memoria_de("analista")
    campos = (e.fatos or {}).get("campos", {})
    natureza = "Roubo" if campos.get("grave_ameaca") else "Furto"
    linha = [f"fato em {campos.get('data_fato') or 'data n/i'}, {campos.get('local') or 'local n/i'}"]
    if (e.fatos or {}).get("veiculo", {}) and e.fatos["veiculo"]["situacao"].startswith("consta"):
        linha.append("veículo citado consta alerta")
    m.anotar(f"hipótese: {natureza} (grave ameaça = {campos.get('grave_ameaca')})")
    e.hipotese = {"natureza_provavel": natureza, "linha_do_tempo": linha}
    e.guardar_memoria(m)
    return e


def juridico(e: Estado) -> Estado:
    m = e.memoria_de("juridico")
    natureza = (e.hipotese or {}).get("natureza_provavel", "Furto")
    tip = TIPIFICACOES["com_ameaca"] if natureza == "Roubo" else TIPIFICACOES["sem_ameaca"]
    nota_humano = _ultima_nota_humano(e)
    proposta = {
        "artigo": tip["artigo"],
        "natureza": tip["natureza"],
        "fundamento": "presença de grave ameaça" if natureza == "Roubo" else "ausência de violência ou grave ameaça",
        "requer_decisao_humana": True,   # tipificação SEMPRE passa por um servidor
        "considerou_nota_do_operador": nota_humano,
    }
    m.anotar(f"proposta: {proposta['artigo']}"
             + (f" (revisada após nota: '{nota_humano}')" if nota_humano else ""))
    e.tipificacao_proposta = proposta
    e.guardar_memoria(m)
    return e


def consolidador(e: Estado) -> Estado:
    m = e.memoria_de("consolidador")
    if not e.tipificacao_final:
        raise RuntimeError("consolidador rodou sem tipificação aprovada — falha do fluxo")
    e.dossie = {
        "ocorrencia": e.id,
        "hipotese": e.hipotese,
        "tipificacao": e.tipificacao_final,
        "decisoes_humanas": e.aprovacoes,
        "aviso": "Rascunho de triagem. A decisão final é do servidor responsável.",
    }
    m.anotar("dossiê consolidado com a tipificação aprovada pelo humano")
    e.guardar_memoria(m)
    return e


def _ultima_nota_humano(e: Estado) -> str | None:
    for d in reversed(e.aprovacoes):
        if d.get("nota"):
            return d["nota"]
    return None
