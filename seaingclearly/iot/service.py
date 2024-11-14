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
    """
    A service class that handles the connection, authentication, and interaction with 
    the SeaingServer, including WebSocket communication and image enhancement.

    Attributes:
        executor (ThreadPoolExecutor): Thread pool executor for asynchronous tasks.
        logger (logging.Logger): Logger for logging information and errors.
        client (SeaingAPIClient): Client for interacting with the SeaingAPI.
        device_info (dict): Information about the device, including UUID and other details.
        config (dict): Configuration for the service.
        ws (WebSocketApp): WebSocket connection for receiving image enhancement updates.
        enhanced_image_callback (Callable): Callback function for handling enhanced image data.
        session_id (UUID): Unique session identifier for the service.
    """
    
    executor = ThreadPoolExecutor(max_workers=5)
    
    def __init__(self):
        """
        Initializes the SeaingService object, sets up logging, device information, 
        and client, and logs the start of the service.
        """

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
        """
        Establishes a WebSocket connection to receive image enhancement updates.

        The WebSocket URL includes the session ID for identifying the connection.
        """

        ws_url = f"ws://localhost:5000/updates?session_id={self.session_id}"
        self.ws = websocket.WebSocketApp(ws_url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.executor.submit(self.ws.run_forever)

    def on_message(self, ws, message):
        """
        Handles incoming WebSocket messages. If the message contains an image, 
        it decodes the image and calls the callback function if set.

        Args:
            ws (WebSocketApp): The WebSocket instance.
            message (str): The incoming WebSocket message.
        """

        data = json.loads(message)

        if "image" in data:
            enhanced_image_base64 = data["image"]
            enhanced_image_bytes = base64.b64decode(enhanced_image_base64)

            # Call the callback function if it's set
            if self.enhanced_image_callback:
                self.enhanced_image_callback(enhanced_image_bytes)

    def on_open(self, ws):
        """
        Logs when the WebSocket connection is successfully opened.

        Args:
            ws (WebSocketApp): The WebSocket instance.
        """

        self.logger.info("WebSocket connection opened")

    def on_error(self, ws, error):
        """
        Logs any WebSocket errors that occur.

        Args:
            ws (WebSocketApp): The WebSocket instance.
            error (Exception): The error that occurred.
        """

        self.logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """
        Logs when the WebSocket connection is closed.

        Args:
            ws (WebSocketApp): The WebSocket instance.
            close_status_code (int): The status code of the closure.
            close_msg (str): The close message.
        """

        self.logger.info("WebSocket connection closed")

    def authenticate(self):
        """
        Authenticates the service with the SeaingServer. If authentication fails,
        it raises an exception.

        Raises:
            Exception: If authentication fails or if connection errors occur.
        """

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
        """
        Uploads an image for enhancement to the SeaingServer.

        Args:
            img_bytes (bytes): The image data to be enhanced.

        Raises:
            ReAuthException: If re-authentication is required.
            Exception: If other errors occur during image enhancement.
        """

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
        """
        Retrieves available options from the SeaingAPI.

        Returns:
            dict: The available options from the API.
        """

        return self.client.get(SeaingAPIClient.Endpoints.OPTIONS)

    def setConfig(self, config: dict) -> dict:
        """
        Sets the configuration for the SeaingService.

        Args:
            config (dict): The configuration to be applied.
        """

        self.executor.submit(self._setConfig, config)
    
    def _setConfig(self, config: dict) -> dict:
        """
        Sends the configuration to the SeaingServer.

        Args:
            config (dict): The configuration to be set.

        Returns:
            dict: The response from the SeaingServer.
        """

        self.config = config

        response = self.client.post(
            SeaingAPIClient.Endpoints.CONFIG,
            json={"config": config},
        )
        return response
    
    def _reqChallenge(self) -> dict:
        """
        Requests a challenge from the SeaingServer to begin the authentication process.

        Returns:
            dict: The response containing the challenge.
        """

        return self.client.post(
            SeaingAPIClient.Endpoints.CHALLENGE,
            json={
                "device_info": self.device_info,
            },
        )

    def _reqAuthenticate(self, challenge_code: str) -> dict:
        """
        Sends the challenge code to the SeaingServer to complete authentication.

        Args:
            challenge_code (str): The hashed challenge code.

        Returns:
            dict: The response from the SeaingServer.
        """
        
        return self.client.post(
            SeaingAPIClient.Endpoints.AUTHENTICATE,
            json={"device_info": self.device_info, "challenge_code": challenge_code},
        )
