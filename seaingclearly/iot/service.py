import hashlib
import json
import logging
import os
import uuid
from requests.exceptions import ConnectionError

from numpy import dtype, ndarray, uint8
import numpy as np

from seaingclearly.iot.client import SeaingAPIClient, ReAuthException

from .util import DeviceInfo

from dotenv import load_dotenv

load_dotenv()

UUID_NAMESPACE = os.environ.get("UUID_NAMESPACE")
API_SECRET = os.environ.get("API_SECRET")

class SeaingService:
    def __init__(self):
        self.logger = logging.getLogger("SeaingService")
        self.client = SeaingAPIClient()

        self.device_info = DeviceInfo(uuid.UUID(UUID_NAMESPACE)).to_dict()
        self.config = None

        self.logger.info("Starting Seaing Service")
        self.logger.info("Device: %s", json.dumps(self.device_info))

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

    def enhanceImage(self, img_bytes):
        try: 
            enhanced_img_bytes = self.client.upload(img_bytes)
        except ReAuthException:
            self.logger.info("Re-authenticating")
            self.authenticate()
            self.setConfig(self.config)
            return self.enhanceImage(img_bytes)

        except Exception as e:
            self.logger.exception(e)
            return None

        return enhanced_img_bytes

    def getOptions(self) -> dict:
        return self.client.get(SeaingAPIClient.Endpoints.OPTIONS)

    def setConfig(self, config: dict) -> dict:
        self.config = config

        return self.client.post(
            SeaingAPIClient.Endpoints.CONFIG,
            json={"config": config},
        )
    
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
