"""Gabarito dos laboratórios da Aula 3.

    python solucao_exercicios.py
"""

from __future__ import annotations

from app.cliente_mcp import ClienteMCP
from app.esquema import ChamadaMCP, FerramentaSpec, ParametroSpec
from app.servidor_mcp import ServidorMCP
from app import ferramentas as F
from app.bases_sinteticas import VEICULOS


# ---------------------------------------------------------------------------
# LAB BÁSICO — nova ferramenta no servidor, cliente descobre sozinho
# ---------------------------------------------------------------------------
def _consultar_cor_predominante(regiao: str) -> dict:
    """Só um exemplo: conta cores de veículos citados na região (fictício)."""
    return {"regiao": regiao, "observacao": "exemplo — junte aqui a lógica real"}


def lab_basico() -> None:
    print("== LAB BÁSICO: registrar uma ferramenta nova ==")
    # registra no servidor (em produção isto estaria em ferramentas.py)
    F.ESPECIFICACOES["consultar_cor_predominante"] = FerramentaSpec(
        nome="consultar_cor_predominante",
        descricao="Exemplo didático. Args: regiao.",
        parametros=[ParametroSpec(nome="regiao")],
    )
    F.IMPLEMENTACOES["consultar_cor_predominante"] = _consultar_cor_predominante

    servidor = ServidorMCP()  # escopo = todas -> inclui a nova
    cliente = ClienteMCP(servidor)
    nomes = [s.nome for s in cliente.conectar()]
    print("  o cliente descobriu:", nomes)
    assert "consultar_cor_predominante" in nomes
    print("  chamada:", cliente.chamar("consultar_cor_predominante", regiao="Guará").resultado)

    # limpa para não afetar outros testes/execuções
    del F.ESPECIFICACOES["consultar_cor_predominante"]
    del F.IMPLEMENTACOES["consultar_cor_predominante"]


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — confirmação humana para ferramenta sensível
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: confirmação humana ==")
    servidor = ServidorMCP()

    negados = []

    def confirmar(nome, args):
        # simula o operador recusando a consulta de veículo
        if nome == "consultar_veiculo":
            negados.append((nome, args))
            return False
        return True

    cliente = ClienteMCP(servidor, confirmar=confirmar)
    cliente.conectar()
    r = cliente.chamar("consultar_veiculo", placa="ABC1D23")
    print(f"  consultar_veiculo -> ok={r.ok} erro={r.erro!r}")
    assert not r.ok and negados
    # a chamada nem chegou ao servidor: nada de veículo na trilha
    assert all("consultar_veiculo" not in l or "listar" in l for l in servidor.trilha().splitlines())
    print("  (a chamada foi barrada no cliente, antes de tocar o servidor)")


# ---------------------------------------------------------------------------
# DESAFIO — escopo negado, auditado
# ---------------------------------------------------------------------------
def desafio() -> None:
    print("\n== DESAFIO: escopo + auditoria ==")
    servidor = ServidorMCP(escopo={"buscar_documento"})
    resp = servidor.atender(ChamadaMCP(
        metodo="chamar_ferramenta", ferramenta="consultar_ocorrencias_similares",
        argumentos={"natureza": "Furto", "regiao": "Asa Norte"}, cliente="x",
    ))
    print(f"  fora do escopo -> ok={resp.ok} erro={resp.erro!r}")
    linha_neg = [l for l in servidor.trilha().splitlines() if l.startswith("[NEG]")]
    print(f"  registrado: {linha_neg}")
    assert linha_neg


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO (parte 2) — as consultas MCP chegam ao Auditor da Aula 2
# ---------------------------------------------------------------------------
def lab_barramento() -> None:
    print("\n== LAB INTERMEDIÁRIO (2): auditoria do MCP no barramento ==")
    from app.barramento import Auditor, Barramento

    barramento = Barramento()
    auditor = Auditor()
    barramento.assinar("ferramenta.invocada", auditor.ao_receber)

    # o servidor publica cada RegistroAuditoria no barramento
    servidor = ServidorMCP(escopo={"buscar_documento"}, barramento=barramento)
    cliente = ClienteMCP(servidor)
    cliente.conectar()
    cliente.chamar("buscar_documento", termo="apreensão")           # permitido
    servidor.atender(ChamadaMCP(metodo="chamar_ferramenta",         # negado
                                ferramenta="consultar_veiculo",
                                argumentos={"placa": "ABC1D23"}, cliente="x"))

    print(f"  o Auditor viu {len(auditor.trilha)} eventos:")
    for ev in auditor.trilha:
        print(f"    {ev.dados['metodo']} {ev.dados.get('ferramenta') or ''} "
              f"permitido={ev.dados['permitido']}")
    # tanto o permitido quanto o negado chegaram
    assert any(not e.dados["permitido"] for e in auditor.trilha)
    assert any(e.dados["permitido"] for e in auditor.trilha)


if __name__ == "__main__":
    lab_basico()
    lab_intermediario()
    lab_barramento()
    desafio()
