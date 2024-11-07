from processing import ImageEnhancer

import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure, img_as_float, img_as_ubyte




# file_path = r"D:\Programming\_UNI\collection\underwater3.jpg"

# img_enhancer = ImageEnhancer()

# def display_encoded_image(img, img_encoded):
#     # Decode the encoded image back to a NumPy array
#     img_array = cv2.imdecode(np.frombuffer(img_encoded, np.uint8), cv2.IMREAD_COLOR)

#     plt.figure(figsize=(20, 20))

#     plt.subplot(2, 3, 1)
#     plt.title("Original Image")
#     plt.imshow(img[:, :, ::-1])

#     plt.subplot(2, 3, 2)
#     plt.title("Enhanced Image")
#     plt.imshow(img_array[:, :, ::-1])
    
#     plt.axis("off")
#     plt.show()

# img = cv2.imread(file_path)

# _, img_encoded = cv2.imencode('.jpg', img)

# # Convert to bytes
# image_bytes = img_encoded.tobytes()

# image_type = "image/jpeg"

# img_encoded, duration_info, errors = img_enhancer.processImg(
#     image_bytes,
#     image_type,
#     {
#         "adaptive_histograph_equalisation": True,
#         "richard_lucy_deconvolution": True,
#         "super_res_upscale": False,
#         "white_balance": True,
#         "laplacian_variance": True,
#     },
# )

# print("Image processed successfully", duration_info, errors)

# display_encoded_image(cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR), img_encoded)




# img = cv2.imread(file_path)
                 
# result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
# avg_a = np.average(result[:, :, 1])
# avg_b = np.average(result[:, :, 2])
# result[:, :, 1] = result[:, :, 1] - (
#     (avg_a - 128) * (result[:, :, 0] / 255.0) * 0.8
# )
# result[:, :, 2] = result[:, :, 2] - (
#     (avg_b - 128) * (result[:, :, 0] / 255.0) * 0.8
# )


# white_balanced_img = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)


# # white_balanced_img_normalized = img_as_float(white_balanced_img)


# # equalised_img = np.zeros_like(white_balanced_img_normalized)
# # for i in range(3):
# #     equalised_img[:, :, i] = exposure.equalize_adapthist(
# #         white_balanced_img_normalized[:, :, i], clip_limit=0.01
# #     )


# # equalised_img = img_as_ubyte(equalised_img)

# plt.figure(figsize=(16, 12))

# # Display the original image
# plt.subplot(2, 3, 1)
# plt.title("Original Image")
# plt.imshow(img[:, :, ::-1])

# # Display original and white balance corrected image
# plt.subplot(2, 3, 2)
# plt.title("equalised_img")
# plt.imshow(white_balanced_img[:, :, ::-1])
# plt.show()


import websocket
import json

# Define the WebSocket URL
ws_url = "ws://localhost:5000/updates?session_id=cca6155f-1158-4ae6-aae8-0ad71e918f70"

# Define the event handler for when the WebSocket opens
def on_open(ws):
    print("WebSocket is open now.")

# Define the event handler for when a message is received
def on_message(ws, message):
    print("Message from server:", message)

# Define the event handler for when the WebSocket is closed
def on_close(ws, close_status_code, close_msg):
    print("WebSocket is closed now.")

# Create the WebSocket application
ws = websocket.WebSocketApp(
    ws_url,
    on_open=on_open,
    on_message=on_message,
    on_close=on_close
)

# Start the WebSocket connection
ws.run_forever()