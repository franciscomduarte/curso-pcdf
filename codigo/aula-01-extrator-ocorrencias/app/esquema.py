"""Esquema de saída do agente extrator.

O que este arquivo faz: define, com Pydantic, o formato exato que o agente deve
produzir. É o "contrato" da saída — o LLM é obrigado a preencher estes campos.

Por que assim: saída estruturada + validação nos dá type-safety e falha cedo
quando o modelo foge do formato (conceito da Aula 1; motiva a Aula 6).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class NaturezaOcorrencia(str, Enum):
    """Naturezas possíveis nesta versão didática do SIGMA."""

    FURTO = "Furto"
    ROUBO = "Roubo"
    AMEACA = "Ameaça"
    DANO = "Dano"
    ESTELIONATO = "Estelionato"
    LESAO_CORPORAL = "Lesão corporal"
    PERTURBACAO = "Perturbação do sossego"
    OUTROS = "Outros"


class Pessoa(BaseModel):
    nome: str = Field(description="Nome como aparece no texto (fictício).")
    papel: str = Field(
        description="Papel na ocorrência: vítima, comunicante, testemunha, "
        "suspeito citado, etc.",
    )


class Veiculo(BaseModel):
    descricao: str = Field(description="Marca/modelo/cor como no texto.")
    placa: str | None = Field(
        default=None, description="Placa fictícia, se mencionada."
    )


class Ocorrencia(BaseModel):
    """Campos estruturados extraídos de um boletim de ocorrência sintético."""

    natureza: NaturezaOcorrencia
    data_fato: str | None = Field(
        default=None, description="Data do fato no formato AAAA-MM-DD, se houver."
    )
    local: str | None = Field(
        default=None, description="Local do fato (região administrativa, via, ponto)."
    )
    pessoas: list[Pessoa] = Field(default_factory=list)
    veiculos: list[Veiculo] = Field(default_factory=list)
    objetos: list[str] = Field(
        default_factory=list,
        description="Objetos relevantes (subtraídos, apreendidos, danificados).",
    )
    resumo: str = Field(description="Resumo objetivo em 1–2 frases.")
    entidades_relevantes: list[str] = Field(
        default_factory=list,
        description="Outras entidades citadas: empresas, órgãos, apps, contas.",
    )

    def linha_relatorio(self) -> str:
        pes = ", ".join(f"{p.nome} ({p.papel})" for p in self.pessoas) or "—"
        return (
            f"[{self.natureza.value}] {self.local or 'local n/i'} | "
            f"{self.data_fato or 'data n/i'} | pessoas: {pes}"
        )
