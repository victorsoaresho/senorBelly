from flask import Blueprint, request, jsonify
from app.models.debt import Debt
from datetime import datetime

debt_bp = Blueprint("debt_controller", __name__, url_prefix="/debts")

_debts_db = []
_current_id = 1


def _is_invalid_debt_data(data):
    """
    Verifica se os dados fornecidos para criar uma dívida são inválidos ou incompletos.

    Args:
        data (dict): Dicionário contendo os dados da dívida.

    Returns:
        bool: True se os dados forem inválidos, False caso contrário.
    """
    return (
        not data
        or not data.get("user_id")
        or not data.get("name")
        or not data.get("value")
        or not data.get("maturity_date")
    )


def _serialize_debt(debt: Debt):
    """
    Converte uma entidade Debt em um dicionário serializável em JSON, formatando a data de vencimento.

    Args:
        debt (Debt): Objeto do tipo Debt.

    Returns:
        dict: Representação em dicionário da dívida.
    """
    return {
        "id": debt.id,
        "user_id": debt.user_id,
        "name": debt.name,
        "value": debt.value,
        "maturity_date": debt.maturity_date.strftime("%Y-%m-%d"),
        "is_paid": debt.is_paid,
    }


@debt_bp.route("", methods=["POST"])
def create_debt():
    """
    Cria uma nova dívida na aplicação.

    Recebe um JSON contendo user_id, name, value e maturity_date.
    """
    global _current_id

    data = request.get_json()

    if _is_invalid_debt_data(data):
        return jsonify({"error": "Invalid or missing required fields"}), 400

    try:
        maturity_date = datetime.strptime(data["maturity_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    debt = Debt(
        id=_current_id,
        user_id=data["user_id"],
        name=data["name"],
        value=data["value"],
        maturity_date=maturity_date,
    )
    _debts_db.append(debt)
    _current_id += 1
    return jsonify(_serialize_debt(debt)), 201


@debt_bp.route("", methods=["GET"])
def get_debts():
    """
    Retorna uma lista contendo todas as dívidas cadastradas.
    """
    return jsonify([_serialize_debt(d) for d in _debts_db]), 200


@debt_bp.route("/<int:debt_id>", methods=["GET"])
def get_debt(debt_id):
    """
    Busca e retorna uma dívida específica pelo seu ID.

    Args:
        debt_id (int): O ID da dívida a ser buscada.
    """
    debt = next((d for d in _debts_db if d.id == debt_id), None)
    if not debt:
        return jsonify({"error": "Debt not found"}), 404
    return jsonify(_serialize_debt(debt)), 200


@debt_bp.route("/<int:debt_id>", methods=["PUT"])
def update_debt(debt_id):
    """
    Atualiza as informações de uma dívida existente (ex: marcar como paga, mudar valor).

    Args:
        debt_id (int): O ID da dívida a ser atualizada.
    """
    debt = next((d for d in _debts_db if d.id == debt_id), None)
    if not debt:
        return jsonify({"error": "Debt not found"}), 404

    data = request.get_json()
    if data.get("name"):
        debt.name = data["name"]
    if data.get("value") is not None:
        debt.value = data["value"]
    if data.get("maturity_date"):
        try:
            debt.maturity_date = datetime.strptime(
                data["maturity_date"], "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if data.get("is_paid") is not None:
        debt.is_paid = data["is_paid"]

    return jsonify(_serialize_debt(debt)), 200


@debt_bp.route("/<int:debt_id>", methods=["DELETE"])
def delete_debt(debt_id):
    """
    Remove uma dívida do sistema pelo seu ID.

    Args:
        debt_id (int): O ID da dívida a ser deletada.
    """
    global _debts_db
    debt = next((d for d in _debts_db if d.id == debt_id), None)
    if not debt:
        return jsonify({"error": "Debt not found"}), 404

    _debts_db = [d for d in _debts_db if d.id != debt_id]
    return jsonify({"message": "Debt deleted successfully"}), 200
