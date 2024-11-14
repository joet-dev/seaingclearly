
from cv2.typing import MatLike
import cv2
from numpy import ndarray, uint8, dtype


def load_image(path:str):
    """
    Loads an image from a given file path and preprocesses it.

    Args:
        path (str): The file path to the image to be loaded.

    Returns:
        ndarray: The preprocessed, encoded image ready for further use.

    This function reads an image from the specified path, then resizes it
    to a maximum width of 800px and height of 600px before returning the
    encoded result.
    """

    img = cv2.imread(path)

    img_encoded = preprocess_image(img, 800, 600)

    return img_encoded 

def preprocess_image(image:MatLike, max_width:int, max_height:int) -> ndarray[any, dtype[uint8]]: 
    """
    Preprocesses an image by resizing it to fit within the specified maximum dimensions.

    Args:
        image (MatLike): The input image to be resized.
        max_width (int): The maximum width the image should be resized to.
        max_height (int): The maximum height the image should be resized to.

    Returns:
        ndarray: The resized and encoded image in .jpg format.

    This function calculates the scaling factor based on the provided maximum
    dimensions, resizes the image accordingly, and returns the encoded image.
    Additional preprocessing steps (e.g., normalization, augmentation) can be added
    in the future.
    """

    height, width = image.shape[:2]

    scaling_factor = min(max_width / width, max_height / height)

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # additional preprocessing steps can be added here
    
    _, img_encoded = cv2.imencode('.jpg', resized_image)
    
    return img_encoded

def load_preprocess_image(path:str, max_width:int, max_height:int) -> ndarray[any, dtype[uint8]]:
    """
    Loads an image from a given file path and preprocesses it by resizing.

    Args:
        path (str): The file path to the image to be loaded.
        max_width (int): The maximum width the image should be resized to.
        max_height (int): The maximum height the image should be resized to.

    Returns:
        ndarray: The preprocessed and encoded image.

    This function reads the image from the given path, resizes it to fit within
    the specified maximum dimensions, and then returns the encoded image.
    """
    
    img = cv2.imread(path)

    img_encoded = preprocess_image(img, max_width, max_height)

    return img_encoded

