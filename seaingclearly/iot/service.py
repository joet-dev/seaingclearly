import hashlib
import json
import logging
import os
import uuid
from requests.exceptions import ConnectionError


from seaingclearly.iot.client import SeaingAPIClient, ReAuthException
from concurrent.futures import ThreadPoolExecutor

import websocket
import base64

from .util import DeviceInfo

from dotenv import load_dotenv

load_dotenv()

UUID_NAMESPACE = os.environ.get("UUID_NAMESPACE")
API_SECRET = os.environ.get("API_SECRET")

class SeaingService:
    executor = ThreadPoolExecutor(max_workers=5)
    
    def __init__(self):
        self.logger = logging.getLogger("SeaingService")
        self.client = SeaingAPIClient()

        self.device_info = DeviceInfo(uuid.UUID(UUID_NAMESPACE)).to_dict()
        self.config = None
        self.ws = None 
        self.enhanced_image_callback = None
        self.session_id = uuid.uuid4()

        self.logger.info("Starting Seaing Service")
        self.logger.info("Device: %s", json.dumps(self.device_info))


    def _connect_to_websocket(self):
        ws_url = f"ws://localhost:5000/updates?session_id={self.session_id}"
        self.ws = websocket.WebSocketApp(ws_url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.executor.submit(self.ws.run_forever)

    def on_message(self, ws, message):
        """Handle incoming messages from the WebSocket."""
        data = json.loads(message)

        if "image" in data:
            enhanced_image_base64 = data["image"]
            enhanced_image_bytes = base64.b64decode(enhanced_image_base64)

            # Call the callback function if it's set
            if self.enhanced_image_callback:
                self.enhanced_image_callback(enhanced_image_bytes)

    def on_open(self, ws):
        self.logger.info("WebSocket connection opened")

    def on_error(self, ws, error):
        self.logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info("WebSocket connection closed")

    def authenticate(self):
        try: 
            challenge_res: dict = self._reqChallenge()
        except ConnectionError:
            raise Exception("Unable to connect to SeaingServer")
        
        challenge = challenge_res["challenge"]

        raw_str:str = challenge + API_SECRET
        challenge_code = hashlib.sha256(raw_str.encode()).hexdigest()

        try: 
            self._reqAuthenticate(challenge_code)
        except Exception as e:
            self.logger.error(f"Failed to authenticate: {e}")
            raise Exception("Failed to authenticate")
        
        self._connect_to_websocket()

    def enhanceImage(self, img_bytes):
        try: 
            self.client.upload(img_bytes, self.session_id)
        except ReAuthException:
            self.logger.info("Re-authenticating")
            self.authenticate()
            self.setConfig(self.config)
            return self.enhanceImage(img_bytes)

        except Exception as e:
            self.logger.exception(e)

    def getOptions(self) -> dict:
        return self.client.get(SeaingAPIClient.Endpoints.OPTIONS)

    def setConfig(self, config: dict) -> dict:
        self.executor.submit(self._setConfig, config)
    
    def _setConfig(self, config: dict) -> dict:
        self.config = config

        response = self.client.post(
            SeaingAPIClient.Endpoints.CONFIG,
            json={"config": config},
        )
        return response
    
    def _reqChallenge(self) -> dict:
        return self.client.post(
            SeaingAPIClient.Endpoints.CHALLENGE,
            json={
                "device_info": self.device_info,
            },
        )

    def _reqAuthenticate(self, challenge_code: str) -> dict:
        return self.client.post(
            SeaingAPIClient.Endpoints.AUTHENTICATE,
            json={"device_info": self.device_info, "challenge_code": challenge_code},
        )
