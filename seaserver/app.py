"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import copy
import hashlib
import os
import time
import json
import uuid
import base64
from concurrent.futures import ThreadPoolExecutor

import pyotp
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    jsonify,
    render_template,
    request,
    session,
)
import threading

from flask_sock import Sock
from flask_session import Session

from seaserver.processing import ImageEnhancer

load_dotenv()

API_SECRET = os.environ.get('API_SECRET')
UUID = os.environ.get('UUID_NAMESPACE')

app = Flask(__name__)
sockets = Sock(app)

app.secret_key = API_SECRET
UUID_NAMESPACE = uuid.UUID(UUID)


# Setup Session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session/"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "sc_"
Session(app)

executor = ThreadPoolExecutor()
img_enhancer = ImageEnhancer()


# In-Memory Storage for Challenge Codes and WebSocket Clients
challenge_storage = {}
clients = {}
clients_lock = threading.Lock()



# AUTH ROUTES

@app.route("/auth-challenge", methods=["POST"])
def request_challenge():
    """
    Endpoint to request a challenge code for authentication. 
    Device info is provided, and a challenge code is generated and returned.
    """

    device_info:dict = request.json.get("device_info")
    if not device_info:
        return jsonify({"error": "Device info is required"}), 400
    
    device_uuid:str = device_info.get("uuid")
    device_info_str:str = f"{device_info.get('device_name')}{device_info.get('mac_address')}"
    if str(uuid.uuid5(UUID_NAMESPACE, device_info_str)) != device_uuid: 
        return jsonify({"error": "Invalid UUID"}), 400

    challenge_code = pyotp.random_base32()
    challenge_storage[device_uuid] = {
        "challenge_code": challenge_code,
        "timestamp": time.time(),
    }

    session["authenticated"] = False

    return jsonify({"challenge": challenge_code}), 200


@app.route("/authenticate", methods=["POST"])
def verify_challenge():
    """
    Endpoint to verify the challenge code. The device info and modified code
    are provided for validation. If successful, the user is authenticated.
    """
     
    device_info: dict = request.json.get("device_info")
    modified_code: str = request.json.get("challenge_code")

    if not device_info or not modified_code:
        return jsonify({"error": "Device Info and modified code are required"}), 400

    device_uuid = device_info.get("uuid")
    challenge_data = challenge_storage.pop(device_uuid, None)
    if not challenge_data:
        return jsonify({"error": "Invalid device info or challenge code expired"}), 400

    if time.time() - challenge_data["timestamp"] > 300:
        return jsonify({"error": "Challenge code expired"}), 400

    challenge_code = challenge_data["challenge_code"]
    raw_str: str = challenge_code + API_SECRET
    expected_code = hashlib.sha256(raw_str.encode()).hexdigest()

    if modified_code != expected_code:
        return jsonify({"error": "Invalid modified code"}), 400

    session["authenticated"] = True
    session["device_info"] = device_info

    return jsonify({"message": "Authentication Successful"}), 200


def auth_check():
    """
    Helper function to check if the user is authenticated. If not, returns a 401 Unauthorized response.
    """

    if not session.get("authenticated"):
        abort(401)


# PROCESSOR

def process_image_task(image_bytes, image_type, config, session_id):
    """
    Background task for processing images using the ImageEnhancer.
    Once processed, the result is sent back to the WebSocket client.
    """

    try: 
        img_encoded, duration_info, errors = img_enhancer.processImg(image_bytes, image_type, config)

        if img_encoded is None: 
            print("Error processing image")
            return 
        
        image_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

        with clients_lock:
            print(f"Sending result to client {clients}")
            if session_id in clients:
                
                print("Client found")
                ws = clients[session_id]
                result_message = {
                    "message": "Image processed successfully",
                    "image": image_base64,
                    "duration": duration_info,
                    "errors": errors,
                }
                
                ws.send(json.dumps(result_message))
    
    except Exception as e:
        print(f"Error processing image: {e}")


# APP ROUTES

@app.route("/", methods=["GET"])
def index():
    """
    Route to serve the index page.
    """

    return render_template("index.html")


@sockets.route('/updates')
def updates_socket(ws):
    """
    WebSocket route for handling client connections. It allows real-time communication
    with clients for sending image processing updates.
    """

    session_id = request.args.get("session_id")
    if not session_id:
        ws.close()
        return

    clients[session_id] = ws
    
    print(f"Starting client {clients}")
    try:
        while True:
            print("socketing")
            message = ws.receive()
            if message is None:
                break

    finally:
        print(f"closing client {clients}")
        clients.pop(session_id, None)


@app.route("/image/enhance", methods=["POST"])
def enhance_image():
    """
    Route to handle image enhancement requests. The image is processed asynchronously,
    and updates are sent via WebSocket.
    """

    auth_check()

    config = session.get("config")

    if not config:
        return jsonify({"error": "Configuration not set"}), 400
    
    config_copy = copy.deepcopy(config)
    image_file = request.files.get("file")

    session_id = request.form.get("session_id")
    if not session_id:
        return jsonify({"error": "Session ID is required for WebSocket communication"}), 400

    if not image_file:
        return jsonify({"error": "Image file is required"}), 400
    
    image_bytes = image_file.read()
    image_type = image_file.content_type

    executor.submit(process_image_task, image_bytes, image_type, config_copy, session_id)

    return jsonify({"message": "Processing started"}), 202

@app.route("/config", methods=["POST"])
def config():
    """
    Route to set the image processing configuration. The configuration is stored in the session.
    """

    auth_check()

    config:dict = request.json.get("config")

    session["config"] = config

    return jsonify({"message": "Configuration set"})

@app.route("/options", methods=["GET"])
def options():
    """
    Route to get available image enhancement options. Returns a list of enhancements.
    """

    auth_check()

    enhancement_data = img_enhancer.getAvailableEnhancements()

    response = {"enhancements": enhancement_data}

    return jsonify(response), 200

@app.route("/logout", methods=["POST"])
def logout():
    """
    Route to logout the user by clearing the session.
    """

    auth_check()

    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# ERROR HANDLERS

@app.errorhandler(405)
def method_not_allowed(e):
    """
    Handle 405 Method Not Allowed errors.
    """

    return jsonify(
        {
            "error": "Method Not Allowed",
            "message": "The method is not allowed for the requested URL.",
        }
    ), 405


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 Not Found errors.
    """
     
    return jsonify(
        {
            "error": "Not Found",
            "message": "The requested URL was not found on the server.",
        }
    ), 404


@app.errorhandler(401)
def unauthorized(e):
    """
    Handle 401 Unauthorized errors.
    """

    return jsonify(
        {
            "error": "Unauthorized",
            "message": "You are not authorized to access this resource.",
        }
    ), 401



if __name__ == "__main__":    
    app.run(threaded=True, debug=True, host="localhost", port=5000)


