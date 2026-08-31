"""Os agentes especializados — os quatro da Aula 7 (inalterados) e um quinto,
novo nesta aula: `revisor_dupla`.

  Investigador  -> fatos            (extrai campos, consulta bases)
  Analista      -> hipotese         (natureza provável + linha do tempo)
  Jurídico      -> tipificacao_proposta   (+ marca o que EXIGE decisão humana)
  Revisor       -> revisao          (só roda quando o roteador escala o caso)
  Consolidador  -> tipificacao_final + dossie   (só roda DEPOIS da aprovação)

Cada função continua recebendo `config` (o ConfigMap do Deployment que a
hospeda, desde a Aula 8) — nada nisso muda aqui.
"""

from __future__ import annotations

from .bases_sinteticas import TIPIFICACOES, consultar_veiculo, extrair_campos
from .memoria import Estado


def investigador(e: Estado, config: dict | None = None) -> Estado:
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


def analista(e: Estado, config: dict | None = None) -> Estado:
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


def juridico(e: Estado, config: dict | None = None) -> Estado:
    """`config["detalhe"]` controla o nível de fundamentação anotado — igual
    à Aula 8/9. `requer_decisao_humana` continua sempre `True`, por design
    (CLAUDE.md §19) — não é algo que um ConfigMap deveria poder desligar."""
    config = config or {}
    m = e.memoria_de("juridico")
    natureza = (e.hipotese or {}).get("natureza_provavel", "Furto")
    tip = TIPIFICACOES["com_ameaca"] if natureza == "Roubo" else TIPIFICACOES["sem_ameaca"]
    nota_humano = _ultima_nota_humano(e)
    fundamento = "presença de grave ameaça" if natureza == "Roubo" else "ausência de violência ou grave ameaça"
    proposta = {
        "artigo": tip["artigo"],
        "natureza": tip["natureza"],
        "fundamento": fundamento,
        "requer_decisao_humana": True,   # tipificação SEMPRE passa por um servidor
        "considerou_nota_do_operador": nota_humano,
    }
    if config.get("detalhe") == "verboso":
        proposta["fundamento_detalhado"] = (
            f"{fundamento}; hipótese do Analista: {(e.hipotese or {}).get('linha_do_tempo')}"
        )
    m.anotar(f"proposta [{config.get('detalhe', 'padrao')}]: {proposta['artigo']}"
             + (f" (revisada após nota: '{nota_humano}')" if nota_humano else ""))
    e.tipificacao_proposta = proposta
    e.guardar_memoria(m)
    return e


def revisor_dupla(e: Estado, config: dict | None = None) -> Estado:
    """Novo nesta aula. Só roda quando o roteador (`roteador.py`) escala o
    caso — natureza Roubo. Não decide nada sozinho: confere se os elementos
    de gravidade que justificaram a tipificação do Jurídico realmente
    aparecem nos fatos levantados pelo Investigador (uma segunda leitura
    independente, não uma reexecução do mesmo raciocínio). O resultado é
    só mais um insumo para o breakpoint humano — nunca substitui a decisão
    do servidor responsável."""
    m = e.memoria_de("revisor")
    proposta = e.tipificacao_proposta or {}
    campos = (e.fatos or {}).get("campos", {})
    concorda = bool(campos.get("grave_ameaca")) and proposta.get("natureza") == "Roubo"
    observacao = (
        "confirma: os fatos levantados pelo Investigador sustentam grave ameaça"
        if concorda else
        "diverge: a tipificação de Roubo não encontra correspondência clara nos fatos — atenção no breakpoint"
    )
    e.revisao = {"concorda": concorda, "observacao": observacao}
    m.anotar(f"revisão dupla: {observacao}")
    e.guardar_memoria(m)
    return e


def consolidador(e: Estado, config: dict | None = None) -> Estado:
    m = e.memoria_de("consolidador")
    if not e.tipificacao_final:
        raise RuntimeError("consolidador rodou sem tipificação aprovada — falha do fluxo")
    e.dossie = {
        "ocorrencia": e.id,
        "hipotese": e.hipotese,
        "tipificacao": e.tipificacao_final,
        "revisao_dupla": e.revisao,
        "decisoes_humanas": e.aprovacoes,
        "atendido_por": e.atendido_por,
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
