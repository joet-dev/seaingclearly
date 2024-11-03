import cv2 
import os
import numpy as np
from numpy import ndarray, uint8, dtype
from skimage import img_as_float, exposure
from skimage.restoration import richardson_lucy



current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "static/models/EDSR_x4.pb")

super_res_model = cv2.dnn_superres.DnnSuperResImpl_create()
super_res_model.readModel(model_path)
super_res_model.setModel("edsr", 4)

def processImg(img_bytes, img_type, config:dict): 
    np_image = decodeImage(img_bytes, img_type)

    if np_image is None: 
        return None
    
    if config.get("white_balance"):
        np_image = applyWhiteBalance(np_image)
        
    if config.get("super_res"):
        np_image = superResUpscaling(np_image)

    if config.get("richard_lucy"):
        np_image = richardLucyDeconvolution(np_image)
    
    if config.get("adaptive_hist_eq"):
        np_image = adaptiveHistogramEqualisation(np_image)

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

    white_balanced_img = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return white_balanced_img

def superResUpscaling(image):
    """
    Super-Resolution Upscaling
    """

    super_res_img = super_res_model.upsample(image)
   
    return super_res_img


def richardLucyDeconvolution(image):
    """
    Richardson-Lucy Deconvolution
    """

    float_img = img_as_float(image) # Convert to float for deconvolution
    point_spread_func = np.ones((5, 5)) / 25  # Point Spread Function

    deconvolved_img = np.zeros_like(float_img)
    # Apply deconvolution channel by channel
    for i in range(3):
        deconvolved_img[:, :, i] = richardson_lucy(float_img[:, :, i], point_spread_func, num_iter=30)

    return deconvolved_img

def adaptiveHistogramEqualisation(image):
    """
    Adaptive Histogram Equalisation
    """
    float_img = img_as_float(image)

    equalised_img = np.zeros_like(float_img)
    for i in range(3):
        equalised_img[:, :, i] = exposure.equalize_adapthist(float_img[:, :, i], clip_limit=0.01)

    # The clip limit affects the sharpness & contrast of the image. Lower values are better for noise reduction.

    return equalised_img

def bytesToNdArray(bytes:bytes):
    """
    Convert bytes to numpy array
    """
    return np.frombuffer(bytes, dtype=uint8)




