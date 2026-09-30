from flask import Blueprint, render_template, request, jsonify

from .logic import generate_caption, ALLOWED_MIME

bp = Blueprint("p1", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("p1/index.html")


@bp.route("/caption", methods=["POST"])
def caption():
    file = request.files.get("file")
    if file is None or file.mimetype not in ALLOWED_MIME:
        return jsonify({"error": "Please upload a JPEG, PNG or WebP image."}), 400
    return jsonify({"caption": generate_caption(file.read(), file.mimetype)})
