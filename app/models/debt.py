from dataclasses import dataclass
from datetime import date


@dataclass
class Debt:
    """
    Entidade que representa uma dívida (Debt) associada a um usuário.
    """

    id: int
    user_id: int
    name: str
    value: float
    maturity_date: date
    is_paid: bool = False
