from dataclasses import dataclass, field


@dataclass
class User:
    """
    Entidade que representa um usuário no sistema.
    """

    id: int
    name: str
    email: str
    password: str
    _balance: float = field(default=0.0, init=False)

    @property
    def get_balance(self) -> float:
        """
        Retorna o saldo atual do usuário.
        """
        return self._balance

    def update_balance(self, amount: float) -> None:
        """
        Atualiza o saldo do usuário com o valor fornecido.

        Args:
            amount (float): O valor a ser adicionado (pode ser negativo para subtrair).
        """
        self._balance += amount
