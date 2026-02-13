from flask import Blueprint, jsonify, send_file, request, current_app
from models.db import get_connection
import qrcode
import io
import base64
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

qr_bp = Blueprint("qr", __name__)

# Frontend URL for QR code target
FRONTEND_BASE = os.getenv('FRONTEND_URL', 'https://dunkin-demand-intelligence.vercel.app')


def log_qr_action(store_id, qr_code_id, action='view'):
    """Log QR code access for audit purposes"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            cur.execute('''
                INSERT INTO qr_access_log (qr_code_id, store_id, ip_address, user_agent, action)
                VALUES (%s, %s, %s, %s, %s)
            ''', (qr_code_id, store_id, ip_address, user_agent, action))
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging QR action: {e}")


def qr_code_exists(store_id):
    """Check if QR code already exists for store"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute('SELECT id, qr_data, qr_url FROM qr_codes WHERE store_id=%s', (store_id,))
            result = cur.fetchone()
        conn.close()
        return result
    except Exception as e:
        print(f"Error checking QR code: {e}")
        return None


def create_qr_with_header(url, store_id):
    """
    Create QR code with header text
    Returns: (PIL Image object)
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Create header image
    header_text = "Submit Waste for Today\nBy Scanning QR Code Below"
    header_height = 150
    header_width = qr_img.width
    
    # Create header with text
    header = Image.new('RGB', (header_width, header_height), color='white')
    draw = ImageDraw.Draw(header)
    
    # Try to use default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw header text
    text_y = 30
    for line in header_text.split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (header_width - text_width) // 2
        draw.text((text_x, text_y), line, fill='black', font=font)
        text_y += 50
    
    # Draw store info
    store_text = f"Store ID: {store_id}"
    bbox = draw.textbbox((0, 0), store_text, font=small_font)
    text_width = bbox[2] - bbox[0]
    text_x = (header_width - text_width) // 2
    draw.text((text_x, text_y - 20), store_text, fill='gray', font=small_font)
    
    # Combine header and QR code
    combined = Image.new('RGB', (header_width, header_height + qr_img.height), color='white')
    combined.paste(header, (0, 0))
    combined.paste(qr_img, (0, header_height))
    
    return combined


def store_qr_code(store_id, qr_data, qr_url):
    """Store QR code in database"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Insert or update QR code
            cur.execute('''
                INSERT INTO qr_codes (store_id, qr_data, qr_url, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON CONFLICT (store_id) DO UPDATE 
                SET qr_data = EXCLUDED.qr_data, 
                    qr_url = EXCLUDED.qr_url,
                    updated_at = NOW()
                RETURNING id;
            ''', (store_id, qr_data, qr_url))
            result = cur.fetchone()
            qr_code_id = result['id'] if result else None
            conn.commit()
        conn.close()
        return qr_code_id
    except Exception as e:
        print(f"Error storing QR code: {e}")
        return None


@qr_bp.route("/store/<int:store_id>", methods=["GET"])
def get_or_create_qr(store_id):
    """Get existing QR code or create if doesn't exist"""
    try:
        # Check if QR already exists
        existing = qr_code_exists(store_id)
        if existing:
            log_qr_action(store_id, existing['id'], 'view')
            return jsonify({
                "store_id": store_id,
                "qr_base64": existing['qr_data'],
                "qr_url": existing['qr_url'],
                "status": "existing"
            }), 200
        
        # Create new QR code
        url = f"{FRONTEND_BASE}/waste/submit?store_id={store_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Store in database
        qr_code_id = store_qr_code(store_id, qr_base64, url)
        
        if qr_code_id:
            log_qr_action(store_id, qr_code_id, 'view')
        
        return jsonify({
            "store_id": store_id,
            "qr_base64": qr_base64,
            "qr_url": url,
            "status": "created"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@qr_bp.route("/download/<int:store_id>", methods=["GET"])
def download_qr(store_id):
    """Download QR code as PNG image with header"""
    try:
        # Get QR code from database
        existing = qr_code_exists(store_id)
        if not existing:
            return jsonify({"error": "QR code not found - create one first"}), 404
        
        # Decode base64 QR
        qr_data = existing['qr_data']
        qr_bytes = base64.b64decode(qr_data)
        qr_img = Image.open(io.BytesIO(qr_bytes))
        
        # Create image with header
        combined = create_qr_with_header(existing['qr_url'], store_id)
        
        # Save to buffer
        buffer = io.BytesIO()
        combined.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Log download action
        log_qr_action(store_id, existing['id'], 'download')
        
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'waste_submission_qr_store_{store_id}.png'
        ), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@qr_bp.route("/download/<int:store_id>/simple", methods=["GET"])
def download_qr_simple(store_id):
    """Download QR code as PNG without header (simple version)"""
    try:
        # Get QR code from database
        existing = qr_code_exists(store_id)
        if not existing:
            return jsonify({"error": "QR code not found"}), 404
        
        # Decode and send base64 QR directly
        qr_data = existing['qr_data']
        qr_bytes = base64.b64decode(qr_data)
        buffer = io.BytesIO(qr_bytes)
        buffer.seek(0)
        
        # Log download
        log_qr_action(store_id, existing['id'], 'download')
        
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'waste_qr_store_{store_id}.png'
        ), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@qr_bp.route("/status/<int:store_id>", methods=["GET"])
def check_qr_status(store_id):
    """Check if QR code exists for store"""
    try:
        existing = qr_code_exists(store_id)
        if existing:
            return jsonify({
                "store_id": store_id,
                "exists": True,
                "created_at": existing.get('created_at', 'unknown'),
                "updated_at": existing.get('updated_at', 'unknown')
            }), 200
        else:
            return jsonify({
                "store_id": store_id,
                "exists": False
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@qr_bp.route("/regenerate/<int:store_id>", methods=["POST"])
def regenerate_qr(store_id):
    """Force regenerate QR code for a store"""
    try:
        # Always create new QR
        url = f"{FRONTEND_BASE}/waste/submit?store_id={store_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Update in database
        qr_code_id = store_qr_code(store_id, qr_base64, url)
        
        if qr_code_id:
            log_qr_action(store_id, qr_code_id, 'regenerate')
        
        return jsonify({
            "store_id": store_id,
            "qr_base64": qr_base64,
            "qr_url": url,
            "status": "regenerated",
            "message": "QR code regenerated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

