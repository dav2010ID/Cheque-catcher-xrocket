import random
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SliderSolver:
    def __init__(self, driver, x,slider):
        self.driver = driver
        self.x = x
        self.slider = slider
        

    def get_track(self, move_distance):
        """
        Generate a list of movements to simulate human behavior while dragging the slider.
        """
        track_list = []
        current = 0
        while current < move_distance:
            move = random.randint(2, 4)  # Small random movements to simulate human behavior
            current += move
            track_list.append(move)
        return track_list
    
    

    def solve(self):
        try:
            slider = self.slider
            if slider:
                print(slider)
                # Calculate the move distance
                move_distance = self.x - 30

                # Initialize ActionChains
                action = ActionChains(self.driver)

                logging.info("Attempting to solve slider challenge...")

                # Click and hold the slider
                action.click_and_hold(slider).perform()

                # Get track points
                track_points = self.get_track(move_distance)

                # Simulate mouse movements for each track point
                for track in track_points:
                    action.move_by_offset(track, 0).perform()
                #action.release(slider).perform()

                logging.info("Slider challenge solved successfully.")
            else:
                print("error")

        except Exception as e:
            logging.error(f"An error occurred while solving the slider challenge: {e}")
        finally:
            try:
                # Release the slider
                print("test")
            except Exception as e:
                logging.error(f"An error occurred while releasing the slider: {e}")


