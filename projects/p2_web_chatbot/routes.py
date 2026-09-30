import uuid

from flask import Blueprint, render_template, request, jsonify, session
from .logic import generate_response

bp = Blueprint("p2", __name__, template_folder="templates")

# Per-visitor chat history, keyed by the session id the hub app assigns.
_histories = {}


@bp.route("/")
def index():
    return render_template("p2/index.html")


@bp.route("/chatbot", methods=["POST"])
def chatbot():
    sid = session.setdefault("sid", uuid.uuid4().hex)
    user_input = (request.get_json(silent=True) or {}).get("message", "")
    response, history = generate_response(user_input, _histories.get(sid, []))
    _histories[sid] = history
    return jsonify({"response": response})
