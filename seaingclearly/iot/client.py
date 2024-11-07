# ensure that this is addaptable to allow for the use in raspberry pi applications.

from enum import Enum
import os
import logging

import requests

class ReAuthException(Exception):
    pass

API_HOST = os.environ.get("API_HOST")

class SeaingAPIClient:
    class Endpoints(Enum):
        ENHANCE = "/image/enhance"
        CHALLENGE = "/auth-challenge"
        AUTHENTICATE = "/authenticate"
        CONFIG = "/config"
        OPTIONS = "/options"

    def __init__(self):
        self.host = API_HOST
        self.logger = logging.getLogger("SeaingAPIClient")

        self.session = requests.Session() 

    def _constructUrl(self, endpoint: Endpoints):
        return f"{self.host}{endpoint.value}"
    
    def post(self, endpoint: Endpoints, json: dict):
        response = self.session.post(
            self._constructUrl(endpoint),
            json=json
        )

        if response.status_code == 200:
            self.logger.info(f"{endpoint.value} - {response.status_code}")
        else: 
            self.logger.error(f"{endpoint.value} - {response.status_code} - {response.json()}")
            raise Exception(f"Failed to post to {endpoint.value}")

        response_json = response.json()

        return response_json
    
    def get(self, endpoint: Endpoints):
        response = self.session.get(
            self._constructUrl(endpoint)
        )

        if 200 <= response.status_code < 300:
            self.logger.info(f"{endpoint.value} - {response.status_code}")
        else:
            self.logger.error(f"{endpoint.value} - {response.status_code} - {response.json()}")
            raise Exception(f"Failed to get from {endpoint.value}")

        response_json = response.json()

        return response_json


    def upload(self, img_bytes, session_id):
        files = { "file": ("image.jpg", img_bytes, "image/jpeg") }
        data = {
            "session_id": session_id  # Add session_id to the form data
        }

        response = self.session.post(
            self._constructUrl(SeaingAPIClient.Endpoints.ENHANCE),
            files=files,
            data=data
        )

        if response.status_code == 200:
            self.logger.info(f"{SeaingAPIClient.Endpoints.ENHANCE.value} - {response.status_code}")
        elif response.status_code == 401:
            raise ReAuthException("Unauthenticated")
        else:
            self.logger.error(f"{SeaingAPIClient.Endpoints.ENHANCE.value} - {response.status_code} - {response.json()}")
            raise Exception(f"Failed to upload to {SeaingAPIClient.Endpoints.ENHANCE.value}")
        
        
