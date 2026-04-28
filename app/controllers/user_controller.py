from flask import Blueprint, request, jsonify
from models.user import User

user_bp = Blueprint("user_controller", __name__, url_prefix="/users")

_users_db = []
_current_id = 1


def _is_invalid_user_data(data):
    """
    Verifica se os dados fornecidos para criar/atualizar um usuário são inválidos ou incompletos.
    
    Args:
        data (dict): Dicionário contendo os dados do usuário.
        
    Returns:
        bool: True se os dados forem inválidos, False caso contrário.
    """
    return (
        not data
        or not data.get("name")
        or not data.get("email")
        or not data.get("password")
    )


def _serialize_user(user: User):
    """
    Converte uma entidade User em um dicionário serializável em JSON, ocultando a senha.
    
    Args:
        user (User): Objeto do tipo User.
        
    Returns:
        dict: Representação em dicionário do usuário.
    """
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "balance": user.get_balance,
    }


@user_bp.route("", methods=["POST"])
def create_user():
    """
    Cria um novo usuário na aplicação.
    
    Recebe um JSON com name, email e password. Retorna o usuário criado com status 201.
    """
    global _current_id

    data = request.get_json()

    if _is_invalid_user_data(data):
        return jsonify({"error": "Invalid or missing required fields"}), 400

    user = User(
        id=_current_id,
        name=data["name"],
        email=data["email"],
        password=data["password"],
    )
    _users_db.append(user)
    _current_id += 1
    return jsonify(_serialize_user(user)), 201


@user_bp.route("", methods=["GET"])
def get_users():
    """
    Retorna uma lista contendo todos os usuários cadastrados.
    """
    return jsonify([_serialize_user(u) for u in _users_db]), 200


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Busca e retorna um usuário específico pelo seu ID.
    
    Args:
        user_id (int): O ID do usuário a ser buscado.
    """
    user = next((u for u in _users_db if u.id == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(_serialize_user(user)), 200


@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Atualiza as informações de um usuário existente.
    
    Args:
        user_id (int): O ID do usuário a ser atualizado.
    """
    user = next((u for u in _users_db if u.id == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if data.get("name"):
        user.name = data["name"]
    if data.get("email"):
        user.email = data["email"]
    if data.get("password"):
        user.password = data["password"]

    return jsonify(_serialize_user(user)), 200


@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Remove um usuário do sistema pelo seu ID.
    
    Args:
        user_id (int): O ID do usuário a ser deletado.
    """
    global _users_db
    user = next((u for u in _users_db if u.id == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    _users_db = [u for u in _users_db if u.id != user_id]
    return jsonify({"message": "User deleted successfully"}), 200
