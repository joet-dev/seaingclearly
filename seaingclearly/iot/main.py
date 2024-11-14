import cv2

from seaingclearly.iot.client import SeaingAPIClient
from seaingclearly.iot.processing import preprocess_image



class Application: 
    """
    The main application class for the SeaingClearly IoT device. 
    Please Note: This has not been tested on a Raspberry Pi and is not fully implemented.
    """
    def __init__(self): 
        self.cap = cv2.VideoCapture(0) 
        self.uploader:SeaingAPIClient = SeaingAPIClient()

    def run(self): 
        while True: 
            ret, frame = self.cap.read()
            if not ret:
                break

            jpg = preprocess_image(frame, 800, 600)

            self.uploader.upload(jpg)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = Application()
    app.run()