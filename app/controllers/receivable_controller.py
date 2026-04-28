from flask import Blueprint, request, jsonify
from models.receivable import Receivable
from datetime import datetime

receivable_bp = Blueprint("receivable_controller", __name__, url_prefix="/receivables")

_receivables_db = []
_current_id = 1


def _is_invalid_receivable_data(data):
    """
    Verifica se os dados fornecidos para criar um recebível são inválidos ou incompletos.
    
    Args:
        data (dict): Dicionário contendo os dados do recebível.
        
    Returns:
        bool: True se os dados forem inválidos, False caso contrário.
    """
    return (
        not data
        or not data.get("user_id")
        or not data.get("name")
        or not data.get("value")
        or not data.get("due_date")
    )


def _serialize_receivable(receivable: Receivable):
    """
    Converte uma entidade Receivable em um dicionário serializável em JSON, formatando a data de recebimento.
    
    Args:
        receivable (Receivable): Objeto do tipo Receivable.
        
    Returns:
        dict: Representação em dicionário do recebível.
    """
    return {
        "id": receivable.id,
        "user_id": receivable.user_id,
        "name": receivable.name,
        "value": receivable.value,
        "due_date": receivable.due_date.strftime("%Y-%m-%d"),
        "is_received": receivable.is_received,
    }


@receivable_bp.route("", methods=["POST"])
def create_receivable():
    """
    Cria um novo recebível na aplicação.
    
    Recebe um JSON contendo user_id, name, value e due_date.
    """
    global _current_id

    data = request.get_json()

    if _is_invalid_receivable_data(data):
        return jsonify({"error": "Invalid or missing required fields"}), 400

    try:
        due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    receivable = Receivable(
        id=_current_id,
        user_id=data["user_id"],
        name=data["name"],
        value=data["value"],
        due_date=due_date,
    )
    _receivables_db.append(receivable)
    _current_id += 1
    return jsonify(_serialize_receivable(receivable)), 201


@receivable_bp.route("", methods=["GET"])
def get_receivables():
    """
    Retorna uma lista contendo todos os recebíveis cadastrados.
    """
    return jsonify([_serialize_receivable(r) for r in _receivables_db]), 200


@receivable_bp.route("/<int:receivable_id>", methods=["GET"])
def get_receivable(receivable_id):
    """
    Busca e retorna um recebível específico pelo seu ID.
    
    Args:
        receivable_id (int): O ID do recebível a ser buscado.
    """
    receivable = next((r for r in _receivables_db if r.id == receivable_id), None)
    if not receivable:
        return jsonify({"error": "Receivable not found"}), 404
    return jsonify(_serialize_receivable(receivable)), 200


@receivable_bp.route("/<int:receivable_id>", methods=["PUT"])
def update_receivable(receivable_id):
    """
    Atualiza as informações de um recebível existente (ex: marcar como recebido, mudar valor).
    
    Args:
        receivable_id (int): O ID do recebível a ser atualizado.
    """
    receivable = next((r for r in _receivables_db if r.id == receivable_id), None)
    if not receivable:
        return jsonify({"error": "Receivable not found"}), 404

    data = request.get_json()
    if data.get("name"):
        receivable.name = data["name"]
    if data.get("value") is not None:
        receivable.value = data["value"]
    if data.get("due_date"):
        try:
            receivable.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if data.get("is_received") is not None:
        receivable.is_received = data["is_received"]

    return jsonify(_serialize_receivable(receivable)), 200


@receivable_bp.route("/<int:receivable_id>", methods=["DELETE"])
def delete_receivable(receivable_id):
    """
    Remove um recebível do sistema pelo seu ID.
    
    Args:
        receivable_id (int): O ID do recebível a ser deletado.
    """
    global _receivables_db
    receivable = next((r for r in _receivables_db if r.id == receivable_id), None)
    if not receivable:
        return jsonify({"error": "Receivable not found"}), 404

    _receivables_db = [r for r in _receivables_db if r.id != receivable_id]
    return jsonify({"message": "Receivable deleted successfully"}), 200
