from flask import Blueprint, request, jsonify
from ..database import get_connection
from datetime import date

estoque_bp = Blueprint("estoque", __name__)


def row_to_dict(row):
    d = dict(row)
    d["estoque_baixo"] = d["quantidade"] <= d["quantidade_minima"]
    return d


@estoque_bp.route("/", methods=["GET"])
def listar_estoque():
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
    """).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows]), 200


@estoque_bp.route("/alertas", methods=["GET"])
def alertas_estoque():
    hoje = date.today().isoformat()
    limite_vencimento = date.today().replace(day=date.today().day).isoformat()

    conn = get_connection()
    rows = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
        WHERE e.quantidade <= e.quantidade_minima OR e.data_validade <= date('now', '+30 days')
    """).fetchall()
    conn.close()

    alertas = []
    for row in rows:
        item = row_to_dict(row)
        dias = (date.fromisoformat(item["data_validade"]) - date.today()).days
        if dias < 0:
            item["vencido"] = True
        elif dias <= 30:
            item["proximo_vencimento"] = True
            item["dias_para_vencer"] = dias
        alertas.append(item)

    return jsonify(alertas), 200


@estoque_bp.route("/<int:medicamento_id>", methods=["GET"])
def buscar_estoque(medicamento_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
        WHERE e.medicamento_id = ?
    """, (medicamento_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Estoque não encontrado para este medicamento."}), 404
    return jsonify(row_to_dict(row)), 200


@estoque_bp.route("/", methods=["POST"])
def registrar_estoque():
    data = request.get_json()
    campos = ["medicamento_id", "quantidade", "lote", "data_validade"]
    for campo in campos:
        if campo not in data:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório."}), 400

    conn = get_connection()
    med = conn.execute("SELECT id FROM medicamentos WHERE id = ?", (data["medicamento_id"],)).fetchone()
    if not med:
        conn.close()
        return jsonify({"erro": "Medicamento não encontrado."}), 404

    existente = conn.execute("SELECT id FROM estoque WHERE medicamento_id = ?", (data["medicamento_id"],)).fetchone()
    if existente:
        conn.close()
        return jsonify({"erro": "Estoque já registrado. Use PUT para atualizar."}), 409

    try:
        date.fromisoformat(data["data_validade"])
    except ValueError:
        conn.close()
        return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD."}), 400

    if data["quantidade"] < 0:
        conn.close()
        return jsonify({"erro": "A quantidade não pode ser negativa."}), 400

    cursor = conn.execute(
        """INSERT INTO estoque (medicamento_id, quantidade, quantidade_minima, lote, data_validade)
           VALUES (?, ?, ?, ?, ?)""",
        (data["medicamento_id"], data["quantidade"],
         data.get("quantidade_minima", 10), data["lote"], data["data_validade"])
    )
    conn.commit()
    novo = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
        WHERE e.id = ?
    """, (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(novo)), 201


@estoque_bp.route("/<int:medicamento_id>", methods=["PUT"])
def atualizar_estoque(medicamento_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM estoque WHERE medicamento_id = ?", (medicamento_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"erro": "Estoque não encontrado."}), 404

    data = request.get_json()
    atual = dict(row)

    if "data_validade" in data:
        try:
            date.fromisoformat(data["data_validade"])
        except ValueError:
            conn.close()
            return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD."}), 400

    if "quantidade" in data and data["quantidade"] < 0:
        conn.close()
        return jsonify({"erro": "A quantidade não pode ser negativa."}), 400

    conn.execute(
        """UPDATE estoque SET quantidade=?, quantidade_minima=?, lote=?, data_validade=?,
           atualizado_em=datetime('now') WHERE medicamento_id=?""",
        (data.get("quantidade", atual["quantidade"]),
         data.get("quantidade_minima", atual["quantidade_minima"]),
         data.get("lote", atual["lote"]),
         data.get("data_validade", atual["data_validade"]),
         medicamento_id)
    )
    conn.commit()
    atualizado = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
        WHERE e.medicamento_id = ?
    """, (medicamento_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(atualizado)), 200


@estoque_bp.route("/<int:medicamento_id>/movimentar", methods=["PATCH"])
def movimentar_estoque(medicamento_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM estoque WHERE medicamento_id = ?", (medicamento_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"erro": "Estoque não encontrado."}), 404

    data = request.get_json()
    if "tipo" not in data or "quantidade" not in data:
        conn.close()
        return jsonify({"erro": "Informe 'tipo' (entrada/saida) e 'quantidade'."}), 400

    tipo = data["tipo"].lower()
    qtd = data["quantidade"]
    quantidade_atual = row["quantidade"]

    if qtd <= 0:
        conn.close()
        return jsonify({"erro": "A quantidade deve ser maior que zero."}), 400

    if tipo == "entrada":
        nova_qtd = quantidade_atual + qtd
    elif tipo == "saida":
        if qtd > quantidade_atual:
            conn.close()
            return jsonify({"erro": "Quantidade insuficiente em estoque."}), 400
        nova_qtd = quantidade_atual - qtd
    else:
        conn.close()
        return jsonify({"erro": "Tipo inválido. Use 'entrada' ou 'saida'."}), 400

    conn.execute(
        "UPDATE estoque SET quantidade=?, atualizado_em=datetime('now') WHERE medicamento_id=?",
        (nova_qtd, medicamento_id)
    )
    conn.commit()
    atualizado = conn.execute("""
        SELECT e.*, m.nome AS medicamento_nome
        FROM estoque e JOIN medicamentos m ON e.medicamento_id = m.id
        WHERE e.medicamento_id = ?
    """, (medicamento_id,)).fetchone()
    conn.close()
    return jsonify({
        "mensagem": f"{tipo.capitalize()} de {qtd} unidade(s) registrada com sucesso.",
        "estoque_atual": row_to_dict(atualizado)
    }), 200
