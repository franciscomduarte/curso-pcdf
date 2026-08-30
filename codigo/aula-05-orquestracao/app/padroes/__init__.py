"""Os cinco padrões de orquestração, sobre os mesmos especialistas."""

from .blackboard import orquestrar as blackboard
from .broker import orquestrar as broker
from .debate import orquestrar as debate
from .pipeline import orquestrar as pipeline
from .supervisor import orquestrar as supervisor

__all__ = ["pipeline", "supervisor", "broker", "blackboard", "debate"]
