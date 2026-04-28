from dataclasses import dataclass
from datetime import date


@dataclass
class Receivable:
    """
    Entidade que representa um recebível (Receivable) associado a um usuário.
    """

    id: int
    user_id: int
    name: str
    value: float
    due_date: date
    is_received: bool = False
