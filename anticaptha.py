import logging
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from decodebase64 import ImageDecoder
from yolod import ImageProcessor
from move_slider import SliderSolver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for API
API_URL = "https://detect.roboflow.com"
API_KEY = "yjo1qgySoGHmqEUSm14j"
MODEL_ID = "t-kjc05/2"

class CaptchaSolver:
    def __init__(self):
        self.driver = self.setup_driver()
        self.css_selector = "div[class*='_body-captcha_'] > div > div[class*='_rsc-card-container_'] > div > div[class*='_rsc-card-slider-puzzle']"
        self.processor = ImageProcessor(API_URL, API_KEY, MODEL_ID)
        self.decoder = ImageDecoder()
        self.css_selector = "div[class*='_body-captcha_'] > div > div[class*='_rsc-card-container_'] > div > div[class*='_rsc-card-slider-container_'] > div[class*='_rsc-card-slider-control_'][class*='_rsc-card-slider-control-default_']"

    def setup_driver(self):
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", "localhost:9223")
            driver = Chrome(options=options)
            logging.info("WebDriver setup successfully.")
            return driver
        except Exception as e:
            

            logging.error(f"Error setting up WebDriver: {e}")
            return None

    def open_new_tab(self, url):
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)
            logging.info(f"Opened new tab with URL: {url}")
        except Exception as e:
            logging.error(f"Error opening a new tab: {e}")

    def wait_for_element(self, by, value, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logging.info(f"Element found: {value}")
            return element
        except Exception as e:
            logging.error(f"Element not found ({value}): {e}")
            return None

    def click_button(self, xpath):
        try:
            button = self.wait_for_element(By.XPATH, xpath)
            if button:
                button.click()
                logging.info(f"Clicked button: {xpath}")
            else:
                logging.warning("Button not found")
        except Exception as e:
            logging.error(f"Error clicking button: {e}")

    def solve_captcha(self):
        try:
            background = self.wait_for_element(By.CSS_SELECTOR, "#root > div > div[class*='_body-captcha_'] > div > div[class*='_rsc-card-container_'] > div > div[class*='_rsc-card-background_']")
            slider = self.wait_for_element((By.XPATH, "/html/body/div/div/div[2]/div/div[3]/div/div[3]/div[5]"))
            print(slider)
            if background:
                background_style = background.get_attribute("style")
                image_hash = self.decoder.decode_image_from_code(background_style)
                if image_hash:
                    _, coordinates = self.processor.anti_captcha_ai(image_hash)
                    x = coordinates[0]
                    try:
                        solver = SliderSolver(self.driver, x,slider)
                        solver.solve()
                    except Exception as e:
                        logging.error(f"An error occurred while solving the slider challenge: {e}")
                    jsscript = f'document.querySelector("{self.css_selector}").style.left = "{x-30}px";'
                    #self.driver.execute_script(jsscript)
                    logging.info("Captcha solved and slider moved.")
                else:
                    logging.error("Failed to decode image hash.")
            else:
                logging.warning("Background not found")
        except Exception as e:
            logging.error(f"Error solving captcha: {e}")

    def run(self, url):
        try:
            self.open_new_tab(url)
            self.driver.implicitly_wait(10)
            self.click_button("/html/body/div/div/div[2]/div/div/button")
            self.solve_captcha()
            input("Press Enter to continue...")  # Keep the browser open
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Browser quit")

if __name__ == "__main__":
    url = "https://webcaptcha2.ton-rocket.com/W320oNyqDUQn6KN#tgWebAppData=query_id%3DAAHaCyNPAgAAANoLI08cy7jw%26user%3D%257B%2522id%2522%253A5622664154%252C%2522first_name%2522%253A%2522and%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253A%2522Puzzle_xx%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1720120212%26hash%3D2f644be0797c6ff460b6c70f4b4f35a594623d501072aad3b856e02ecb488ab7&tgWebAppVersion=7.4&tgWebAppPlatform=web&tgWebAppBotInline=1&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D"
    solver = CaptchaSolver()
    solver.run(url)
