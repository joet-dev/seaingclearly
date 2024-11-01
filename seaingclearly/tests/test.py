import cv2
from PIL import Image
import io
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from seaingclearly.iot.service import SeaingService

api_service = SeaingService()

image = cv2.imread(r"D:\Programming\_UNI\collection\underwater1.jpg")
_, img_encoded = cv2.imencode('.png', image) 
image_bytes = img_encoded.tobytes()

api_service.setConfig({"config": {"white_balance": True}})
enhanced_image_bytes = api_service.enhanceImage(image_bytes)

enhanced_image = Image.open(io.BytesIO(enhanced_image_bytes))

plt.figure(figsize=(16, 12))

plt.subplot(2, 3, 1)
plt.title("Original Image")
plt.imshow(image[:, :, ::-1])
plt.axis('off')  # Hide the axis

# Display the image using matplotlib
plt.subplot(2, 3, 2)
plt.title("White Balance Corrected Image")
plt.imshow(enhanced_image)
plt.show()