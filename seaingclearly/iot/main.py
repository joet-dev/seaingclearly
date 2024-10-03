import cv2

from .stream_upload import StreamUploader
from .processing import preprocess_image


class Application: 
    def __init__(self): 
        self.cap = cv2.VideoCapture(0) 
        self.uploader = StreamUploader()


    def run(self): 
        while True: 
            ret, frame = self.cap.read()
            if not ret:
                break

            # cv2.imshow('Frame', frame)
            jpg = preprocess_image(frame, 800, 600)

            self.uploader.upload_frame(jpg)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = Application()
    app.run()