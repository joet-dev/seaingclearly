# ensure that this is addaptable to allow for the use in raspberry pi applications. 

import platform
import socket
import requests

from enum import Enum
from numpy import ndarray, dtype, uint8


class SeaingAPIClient:
    class Endpoints(Enum): 
        ENHANCE = "/image/enhance"
        AUTHENTICATE = "/authenticate"

    def __init__(self, host:str):
        self.host = host

        self.device_name = platform.node()

    def upload_frame(self, name:str, jpeg: ndarray[any, dtype[uint8]]):

        image_bytes = jpeg.tobytes()
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}

        response = requests.post(self.url, data=jpeg.tostring(), headers={'Content-Type': 'image/jpeg'})

        print(response)

