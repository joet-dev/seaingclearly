
from cv2.typing import MatLike
import cv2
from numpy import ndarray, uint8, dtype


def load_image(path:str):
    img = cv2.imread(path)

    img_encoded = preprocess_image(img, 800, 600)

    return img_encoded 

def preprocess_image(image:MatLike, max_width:int, max_height:int) -> ndarray[any, dtype[uint8]]: 
    height, width = image.shape[:2]

    scaling_factor = min(max_width / width, max_height / height)

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # additional preprocessing steps can be added here
    
    _, img_encoded = cv2.imencode('.jpg', resized_image)
    
    return img_encoded