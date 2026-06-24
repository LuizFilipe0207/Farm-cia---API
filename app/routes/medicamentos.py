from flask import Blueprint, request, jsonify
from ..database import get_connection

medicamentos_bp = Blueprint("medicamentos", __name__)


def row_to_dict(row):
    return dict(row)


@medicamentos_bp.route("/", methods=["GET"])
def listar_medicamentos():
    nome = request.args.get("nome", "")
    categoria = request.args.get("categoria", "")
    requer_receita = request.args.get("requer_receita")

    conn = get_connection()
    query = "SELECT * FROM medicamentos WHERE 1=1"
    params = []

    if nome:
        query += " AND nome LIKE ?"
        params.append(f"%{nome}%")
    if categoria:
        query += " AND categoria LIKE ?"
        params.append(f"%{categoria}%")
    if requer_receita is not None:
        query += " AND requer_receita = ?"
        params.append(1 if requer_receita.lower() == "true" else 0)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows]), 200


@medicamentos_bp.route("/<int:id>", methods=["GET"])
def buscar_medicamento(id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Medicamento não encontrado."}), 404
    return jsonify(row_to_dict(row)), 200


@medicamentos_bp.route("/", methods=["POST"])
def criar_medicamento():
    data = request.get_json()
    campos = ["nome", "principio_ativo", "fabricante", "categoria", "preco"]
    for campo in campos:
        if campo not in data:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório."}), 400
    if data["preco"] <= 0:
        return jsonify({"erro": "O preço deve ser maior que zero."}), 400

    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO medicamentos (nome, principio_ativo, fabricante, categoria, requer_receita, preco)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (data["nome"], data["principio_ativo"], data["fabricante"],
         data["categoria"], int(data.get("requer_receita", False)), data["preco"])
    )
    conn.commit()
    novo = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(novo)), 201


@medicamentos_bp.route("/<int:id>", methods=["PUT"])
def atualizar_medicamento(id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"erro": "Medicamento não encontrado."}), 404

    data = request.get_json()
    if "preco" in data and data["preco"] <= 0:
        conn.close()
        return jsonify({"erro": "O preço deve ser maior que zero."}), 400

    atual = row_to_dict(row)
    conn.execute(
        """UPDATE medicamentos SET nome=?, principio_ativo=?, fabricante=?,
           categoria=?, requer_receita=?, preco=? WHERE id=?""",
        (data.get("nome", atual["nome"]),
         data.get("principio_ativo", atual["principio_ativo"]),
         data.get("fabricante", atual["fabricante"]),
         data.get("categoria", atual["categoria"]),
         int(data.get("requer_receita", atual["requer_receita"])),
         data.get("preco", atual["preco"]), id)
    )
    conn.commit()
    atualizado = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(atualizado)), 200


@medicamentos_bp.route("/<int:id>", methods=["DELETE"])
def deletar_medicamento(id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"erro": "Medicamento não encontrado."}), 404
    conn.execute("DELETE FROM medicamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Medicamento removido com sucesso."}), 200
