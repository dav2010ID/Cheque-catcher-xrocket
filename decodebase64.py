import base64
import re
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageDecoder:
    def __init__(self):
        self.decoded_images = {}

    def decode_image_from_code(self, code):
        """
        Decode an image from a base64-encoded data URL found within a given code string.

        :param code: The string containing the data URL to decode.
        :return: The unique identifier of the decoded image or None if an error occurs.
        """
        try:
            # Regular expression to find all data URLs
            pattern = r'url\("data:image/png;base64,([^"]+)"\)'

            match = re.findall(pattern, code)
            if not match:
                logging.error("No base64-encoded image found in the provided code.")
                return None
            
            base64_data = match[0]  # Extract the base64-encoded string

            # Check if the image has already been decoded
            if base64_data not in self.decoded_images:
                decoded_data = base64.b64decode(base64_data)
                
                # Generate a unique identifier for the image using its hash
                image_hash = hashlib.sha256(base64_data.encode()).hexdigest() + '.png'
                
                # Save the decoded image to a file
                self.save_to_file(decoded_data, image_hash)
                
                # Store the decoded data in the dictionary
                self.decoded_images[image_hash] = decoded_data
            
            return image_hash  # Return the identifier of the decoded image
        except Exception as e:
            logging.error(f"An error occurred while decoding the image: {e}")
            return None

    def save_to_file(self, data, filename):
        """
        Save binary data to a file if it does not already exist.

        :param data: The binary data to save.
        :param filename: The name of the file to save the data to.
        """
        try:
            if not os.path.exists(filename):
                logging.info(f"Saving image to {filename}.")
                with open(filename, 'wb') as f:
                    f.write(data)
            else:
                logging.info(f"Image {filename} already exists.")
        except Exception as e:
            logging.error(f"An error occurred while saving the image: {e}")



