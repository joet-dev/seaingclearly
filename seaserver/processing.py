import cv2 
import numpy as np
from numpy import ndarray, uint8, dtype


def processImg(img_bytes, img_type, config:dict): 
    np_image = decodeImage(img_bytes, img_type)

    if np_image is None: 
        return None
    
    if config.get("white_balance"):
        np_image = applyWhiteBalance(np_image)

    img_encoded = encodeImage(np_image, img_type)
    
    return img_encoded


ENCODE_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png"
}

def encodeImage(img_arr, img_format: str):
    format = ENCODE_MAP.get(img_format)
    
    if not format: 
        return None
    
    _, img_encoded = cv2.imencode(format, img_arr)

    return img_encoded
    

def decodeImage(img_bytes:bytes, img_format: str):
    """
    Decode image bytes to numpy array
    """
    
    if img_format == "image/jpeg":
        return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    else: 
        return None


def applyWhiteBalance(image):
    """
    Apply white balance correction to an image
    """
    result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 0.8)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 0.8)

    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

def bytesToNdArray(bytes:bytes):
    """
    Convert bytes to numpy array
    """
    return np.frombuffer(bytes, dtype=uint8)




