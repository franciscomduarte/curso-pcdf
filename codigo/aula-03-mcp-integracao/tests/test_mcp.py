"""Testes do MCP mínimo — rodam offline, só com pydantic."""

from __future__ import annotations

from app.agente_consultor import AgenteConsultor
from app.cliente_mcp import ClienteMCP
from app.esquema import ChamadaMCP
from app.llm import MockConsultor
from app.servidor_mcp import ServidorMCP


def test_descoberta_lista_ferramentas():
    cli = ClienteMCP(ServidorMCP())
    nomes = {s.nome for s in cli.conectar()}
    assert nomes == {"consultar_veiculo", "consultar_ocorrencias_similares", "buscar_documento"}


def test_chamada_valida_passa_pelo_servidor_e_audita():
    srv = ServidorMCP()
    cli = ClienteMCP(srv)
    cli.conectar()
    r = cli.chamar("consultar_veiculo", placa="ABC1D23")
    assert r.ok and r.resultado["situacao"].startswith("consta alerta")
    # listar + chamar registrados
    assert any(reg.ferramenta == "consultar_veiculo" and reg.permitido for reg in srv.auditoria)


def test_escopo_nega_e_registra():
    srv = ServidorMCP(escopo={"buscar_documento"})
    resp = srv.atender(ChamadaMCP(metodo="chamar_ferramenta",
                                  ferramenta="consultar_veiculo",
                                  argumentos={"placa": "ABC1D23"}, cliente="t"))
    assert not resp.ok and "escopo" in resp.erro
    assert any(not reg.permitido for reg in srv.auditoria)


def test_cliente_so_conhece_o_que_foi_listado():
    srv = ServidorMCP(escopo={"buscar_documento"})
    cli = ClienteMCP(srv)
    cli.conectar()
    r = cli.chamar("consultar_veiculo", placa="ABC1D23")
    assert not r.ok and "catálogo" in r.erro


def test_ferramenta_sensivel_exige_confirmacao():
    srv = ServidorMCP()
    cli = ClienteMCP(srv, confirmar=lambda nome, args: False)
    cli.conectar()
    r = cli.chamar("consultar_veiculo", placa="ABC1D23")
    assert not r.ok and "confirmada" in r.erro
    # não tocou o servidor
    assert not any(reg.ferramenta == "consultar_veiculo" for reg in srv.auditoria)


def test_ler_recurso_politica():
    cli = ClienteMCP(ServidorMCP())
    r = cli.ler_recurso("sigma://politica-de-uso")
    assert r.ok and "auditoria" in r.resultado.lower()


def test_agente_encadeia_consultas_e_encerra():
    srv = ServidorMCP()
    agente = AgenteConsultor(cliente=ClienteMCP(srv), llm=MockConsultor(), max_passos=5)
    texto = ("Furto de motocicleta Honda CG placa ABC1D23 em Taguatinga.")
    res = agente.enriquecer(texto)
    assert res.passos == 2                       # veículo + similares
    assert "consultar_veiculo" in res.observacoes[0]
    assert "consultar_ocorrencias_similares" in res.observacoes[1]
    assert res.enriquecimento.startswith("Enriquecimento")


def test_agente_respeita_max_passos():
    class LoopInfinito:
        def proximo_passo(self, contexto, ferramentas, observacoes):
            return {"ferramenta": "buscar_documento", "argumentos": {"termo": "x"}}

    srv = ServidorMCP()
    agente = AgenteConsultor(cliente=ClienteMCP(srv), llm=LoopInfinito(), max_passos=3)
    res = agente.enriquecer("qualquer coisa")
    assert res.passos == 3 and "Limite de passos" in res.enriquecimento


def test_conectar_e_idempotente_nao_duplica_auditoria():
    srv = ServidorMCP()
    cli = ClienteMCP(srv)
    cli.conectar()
    cli.conectar()
    cli.conectar()
    assert sum(1 for r in srv.auditoria if r.metodo == "listar_ferramentas") == 1


def test_servidor_publica_auditoria_no_barramento():
    from app.barramento import Auditor, Barramento

    bus, aud = Barramento(), Auditor()
    bus.assinar("#", aud.ao_receber)
    srv = ServidorMCP(escopo={"buscar_documento"}, barramento=bus)
    cli = ClienteMCP(srv)
    cli.conectar()
    cli.chamar("buscar_documento", termo="apreensão")
    srv.atender(ChamadaMCP(metodo="chamar_ferramenta", ferramenta="consultar_veiculo",
                           argumentos={"placa": "ABC1D23"}, cliente="x"))
    assert any(not e.dados["permitido"] for e in aud.trilha)   # o negado chegou
    assert any(e.dados["permitido"] for e in aud.trilha)
