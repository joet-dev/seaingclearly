import os
import time
from datetime import timedelta
from functools import wraps

import cv2
import numpy as np
from numpy import uint8
from skimage import exposure, img_as_float
from skimage.restoration import richardson_lucy

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "static/models/EDSR_x4.pb")

super_res_model = cv2.dnn_superres.DnnSuperResImpl_create()
super_res_model.readModel(model_path)
super_res_model.setModel("edsr", 4)

def run_enhancement(enhancement_name:str, img_array:np.ndarray):
    """
    Run an enhancement function on an image array
    """
    func = globals().get(enhancement_name)
    
    if func is None: 
        return None
    
    return func(img_array)

def process_img(img_bytes, img_type, config:dict): 
    np_image = decode_img(img_bytes, img_type)

    if np_image is None: 
        return None
    
    duration = {}

    for enhancement, enabled in config.items():
        if not enabled: 
            continue
        
        np_image, time = run_enhancement(enhancement, np_image)
        duration.update(time)

    img_encoded = encode_img(np_image, img_type)
    
    return img_encoded, duration

ENCODE_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png"
}

def encode_img(img_arr, img_format: str):
    format = ENCODE_MAP.get(img_format)
    
    if not format: 
        return None
    
    _, img_encoded = cv2.imencode(format, img_arr)

    return img_encoded
    
def decode_img(img_bytes:bytes, img_format: str):
    """
    Decode image bytes to numpy array
    """
    
    if img_format == "image/jpeg":
        return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    else: 
        return None

def bytes_to_ndarray(bytes:bytes):
    """
    Convert bytes to numpy array
    """
    return np.frombuffer(bytes, dtype=uint8)

def enhancement_metadata(name, description):
    def decorator(func):
        func.filter_name = name
        func.filter_description = description
        return func
    
    return decorator

def get_available_enhancements():
    available_filters = {}
    for func in [white_balance, super_res_upscale, richard_lucy_deconvolution, adaptive_histograph_equalisation]:
        available_filters[func.__name__] = {
            "lbl": func.filter_name,
            "tt": func.filter_description
        }
    return available_filters

def time_enhancement(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = timedelta(seconds=end_time - start_time)
        
        print(f"{func.__name__} took {elapsed_time} to run.")

        formatted_result = (result, {func.__name__: elapsed_time.total_seconds()})

        return formatted_result
    
    return wrapper

# Image Enhancement Functions
@enhancement_metadata("White Balance Correction", "Applies white balance correction to enhance the color balance in the image.")
@time_enhancement
def white_balance(image):
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

@enhancement_metadata("Super-Resolution Upscaling", "Enhances image resolution using super-resolution techniques. Is computationally expensive.")
@time_enhancement
def super_res_upscale(image):
    """
    Super-Resolution Upscaling
    """

    super_res_img = super_res_model.upsample(image)
   
    return super_res_img

@enhancement_metadata("Richardson-Lucy Deconvolution", "Applies deconvolution to reduce blurring caused by camera optics.")
@time_enhancement
def richard_lucy_deconvolution(image):
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

@enhancement_metadata("Adaptive Histogram Equalization", "Enhances contrast using adaptive histogram equalization to improve image details.")
@time_enhancement
def adaptive_histograph_equalisation(image):
    """
    Adaptive Histogram Equalisation
    """
    float_img = img_as_float(image)

    equalised_img = np.zeros_like(float_img)
    for i in range(3):
        equalised_img[:, :, i] = exposure.equalize_adapthist(float_img[:, :, i], clip_limit=0.01)

    # The clip limit affects the sharpness & contrast of the image. Lower values are better for noise reduction.

    return equalised_img






