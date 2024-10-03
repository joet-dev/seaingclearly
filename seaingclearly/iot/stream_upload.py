# ensure that this is addaptable to allow for the use in raspberry pi applications. 


import requests

from numpy import ndarray, dtype, uint8


class StreamUploader:
    def __init__(self):
        self.url = 'http://your-server-url/stream'

    def upload_frame(self, jpeg: ndarray[any, dtype[uint8]]):
        response = requests.post(self.url, data=jpeg.tostring(), headers={'Content-Type': 'image/jpeg'})

        print(response)

