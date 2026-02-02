from flask import Blueprint, jsonify
import qrcode
import io
import base64

qr_bp = Blueprint("qr", __name__)

@qr_bp.route("/store/<int:store_id>", methods=["GET"])
def generate_qr(store_id):
    url = f"https://dunkin-demand-intelligence-neil-barots-projects-55b3b305.vercel.app/waste/submit?store_id={store_id}"

    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        "store_id": store_id,
        "qr_base64": qr_base64,
        "target_url": url
    })
