import os
import time
from datetime import timedelta
from functools import wraps

import cv2
import numpy as np
from numpy import uint8
from skimage import exposure, img_as_float, img_as_ubyte
from skimage.restoration import richardson_lucy

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "static/models/ESPCN_x2.pb")

super_res_model = cv2.dnn_superres.DnnSuperResImpl_create()
super_res_model.readModel(model_path)
super_res_model.setModel("espcn", 4)

enhancement_registry = []

ENCODE_MAP = {"image/jpeg": ".jpg", "image/png": ".png"}

def save_encoded_image(img_encoded, filename="output_image.jpg"):
    # Decode the image
    img_decoded = cv2.imdecode(np.frombuffer(img_encoded, np.uint8), cv2.IMREAD_COLOR)
    
    # Save the decoded image to disk
    cv2.imwrite(filename, img_decoded)
    print(f"Image saved as {filename}")


def encode_img(img_arr, img_format: str):
    format = ENCODE_MAP.get(img_format)

    if not format:
        return None
    
    _, img_encoded = cv2.imencode(format, img_arr)

    return img_encoded


def decode_img(img_bytes: bytes, img_format: str):
    """
    Decode image bytes to numpy array
    """

    if img_format == "image/jpeg":
        return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    else:
        return None


def bytes_to_ndarray(bytes: bytes):
    """
    Convert bytes to numpy array
    """
    return np.frombuffer(bytes, dtype=uint8)


def enhancement_metadata(name, description):
    def decorator(func):
        func.filter_name = name
        func.filter_description = description
        
        enhancement_registry.append(func)
        return func

    return decorator


def time_enhancement(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = timedelta(seconds=end_time - start_time)

        print(f"{func.__name__} took {elapsed_time} to run.")

        formatted_result = [result, {func.__name__: elapsed_time.total_seconds()}]

        return formatted_result

    return wrapper


class ImageEnhancer:        
    def __init__(self):
        self.sharpness:int = None

    def getAvailableEnhancements(self):
        available_filters = []
        for func in enhancement_registry:
            available_filters.append({
                "name": func.__name__,
                "lbl": func.filter_name,
                "tt": func.filter_description,
            })

        return available_filters

    def processImg(self, img_bytes, img_type, config: dict):
        self.sharpness = None
        np_image = decode_img(img_bytes, img_type)

        if np_image is None:
            return None

        duration = {}
        errors = {}

        for enhancement_func in enhancement_registry:
            if enhancement_func.__name__ not in config or not config[enhancement_func.__name__]:
                continue

            try: 
                result = enhancement_func(self, np_image)
            except Exception as e:
                errors.update({enhancement_func.__name__: str(e)})
                continue

            if isinstance(result, list):
                np_image = result[0]
                duration.update(result[1])
            elif result is None:
                continue
            else: 
                np_image = result

        img_encoded = encode_img(np_image, img_type)

        return img_encoded, duration, errors


    # IMAGE ENHANCEMENT FUNCTIONS

    @enhancement_metadata(
        "Laplacian Variance",
        """This function calculates the variance of the Laplacian of the input image. It is used as a measure of image sharpness.\n
        A low variance indicates that the image is blurry. This function does not enhance the image but allows for other functions to use the sharpness value.""",
    )
    def laplacian_variance(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        laplacian_variance = laplacian.var()

        self.sharpness = laplacian_variance

        return None


    @enhancement_metadata(
        "White Balance Correction",
        "Applies white balance correction to enhance the color balance in the image.",
    )
    @time_enhancement
    def white_balance(self, image):
        """
        Apply white balance correction to an image
        """
        result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - (
            (avg_a - 128) * (result[:, :, 0] / 255.0) * 0.8
        )
        result[:, :, 2] = result[:, :, 2] - (
            (avg_b - 128) * (result[:, :, 0] / 255.0) * 0.8
        )

        white_balanced_img = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

        return white_balanced_img


    @enhancement_metadata(
        "Super-Resolution Upscaling",
        "Enhances image resolution using super-resolution techniques. Is computationally expensive.",
    )
    @time_enhancement
    def super_res_upscale(self, image):
        """
        Super-Resolution Upscaling
        """

        super_res_img = super_res_model.upsample(image)

        return super_res_img


    @enhancement_metadata(
        "Richardson-Lucy Deconvolution",
        "Applies deconvolution to reduce blurring caused by camera optics.",
    )
    @time_enhancement
    def richard_lucy_deconvolution(self, image):
        """
        Richardson-Lucy Deconvolution
        """
        float_img = img_as_float(image)

        height, width, point_spread_func  = self.get_img_config(float_img)
        pad_float_img = np.pad(float_img, ((height, height), (width, width), (0, 0)), mode='reflect')

        iterations = self.get_iterations_by_sharpness(height*width)
        
        deconvolved_img = np.zeros_like(pad_float_img)

        # Apply deconvolution channel by channel
        for i in range(3):
            deconvolved_img[:, :, i] = richardson_lucy(
                pad_float_img[:, :, i], point_spread_func, num_iter=iterations
            )

        unpad_deconvolved_img = deconvolved_img[height:-height, width:-width]

        deconvolved_img = img_as_ubyte(unpad_deconvolved_img)

        return deconvolved_img


    @enhancement_metadata(
        "Adaptive Histogram Equalization",
        "Enhances contrast using adaptive histogram equalization to improve image details.",
    )
    @time_enhancement
    def adaptive_histograph_equalisation(self, image):
        """
        Adaptive Histogram Equalisation
        """
        float_img = img_as_float(image)

        equalised_img = np.zeros_like(float_img)
        for i in range(3):
            equalised_img[:, :, i] = exposure.equalize_adapthist(
                float_img[:, :, i], clip_limit=0.01
            )
        # The clip limit affects the sharpness & contrast of the image. Lower values are better for noise reduction.

        equalised_img = img_as_ubyte(equalised_img)

        return equalised_img


    def get_img_config(self, image, kernel_size=5):
        kernel_size=5
        height, width = image.shape[:2]

        if height*width < 1000000:
            kernel_size=3
        
        point_spread_func = np.ones((kernel_size, kernel_size)) / kernel_size**2 

        pad_height = (((kernel_size - height % kernel_size) % kernel_size) + kernel_size) * 3
        pad_width = (((kernel_size - width % kernel_size) % kernel_size) + kernel_size) * 3

        return pad_height * 3, pad_width * 3, point_spread_func
    
    def get_iterations_by_sharpness(self, pixel_count): 
        iter = 30

        if not self.sharpness: 
            return iter
        
        if self.sharpness < 50:
            iter *= 1.2
            
        if pixel_count < 1000000:
            iter /= 4

        print(int(iter))
        return int(iter)

        

