import os
import logging
from cv2 import imread, imshow, destroyAllWindows, waitKey, circle, FILLED
from inference_sdk import InferenceHTTPClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageProcessor:
    def __init__(self, api_url, api_key, model_id):
        self.client = InferenceHTTPClient(api_url=api_url, api_key=api_key)
        self.model_id = model_id

    def show_image(self, path_image, point_coords):
        try:
            image = imread(path_image)
            if image is None:
                logging.error(f"Error: Unable to load image from {path_image}")
                return
            
            center = tuple(point_coords)
            color = (0, 0, 255)  # Red color in BGR
            diameter = 20  # Diameter of the point
            
            self.draw_point(image, center, diameter, color)
            
            #imshow('Image with Point', image)
            #waitKey(0)
            #destroyAllWindows()
        except Exception as e:
            logging.error(f"An error occurred while showing the image: {e}")

    @staticmethod
    def draw_point(image, center, diameter, color):
        try:
            radius = diameter // 2
            circle(image, center, radius, color, thickness=FILLED)
        except Exception as e:
            logging.error(f"An error occurred while drawing the point: {e}")

    def get_prediction(self, image_path):
        try:
            results = self.client.infer(image_path, model_id=self.model_id)
            logging.info(f"Prediction results: {results}")
            return results
        except Exception as e:
            logging.error(f"An error occurred while getting prediction: {e}")
            return None

    @staticmethod
    def to_list(text):
        try:
            text = text.strip('[]').split(',')
            text_list = [int(float(num)) for num in text]
            return text_list
        except Exception as e:
            logging.error(f"An error occurred while converting text to list: {e}")
            return []

    @staticmethod
    def extract_centers(data):
        try:
            highest_confidence = -1
            x_with_highest_confidence = None

            for prediction in data['predictions']:
                confidence = prediction['confidence']
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    x_with_highest_confidence = prediction['x']
                    y_with_highest_confidence = prediction['y']

            return [x_with_highest_confidence, y_with_highest_confidence]
        except Exception as e:
            logging.error(f"An error occurred while extracting centers: {e}")
            return [None, None]

    def anti_captcha_ai(self, image_path):
        try:
            txt_path = f'{image_path}.txt'
            if not os.path.exists(txt_path):
                logging.info("Loading model and making initial prediction.")
                with open(txt_path, 'w') as f:
                    centers = self.extract_centers(self.get_prediction(image_path))
                    f.write(str(centers))

            image = imread(image_path)
            if image is None:
                logging.error(f"Error: Unable to load image from {image_path}")
                return None, None

            if os.path.exists(txt_path):
                with open(txt_path, 'r') as f:
                    content = f.read()
                    if not content:
                        centers = self.extract_centers(self.get_prediction(image_path))
                        with open(txt_path, 'w') as f1:
                            f1.write(str(centers))

                point_coords = self.to_list(content)
                self.show_image(image_path, point_coords)
                image_height, image_width = image.shape[:2]
                x, y = point_coords
                percent_x = (x / image_width) * 100
                percent_y = (y / image_height) * 100
                percent_coords = [percent_x, percent_y]
                logging.info(f"Percent coordinates: {percent_coords}")
                return percent_coords, point_coords
            else:
                logging.error("File save error")
                return None, None
        except Exception as e:
            logging.error(f"An error occurred in anti_captcha_ai: {e}")
            return None, None

