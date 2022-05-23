from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# helper function
def element_from_xpath(driver, xpath, multi=False):
        """[summary]

        Args:
            xpath (str): valid xpath for argument, e.g. '//element[@class="some attribute"]'
            multi (bool, optional): wether to look for one or several elements (list). Defaults to False.

        Returns:
            selenium.wedriver.element: A selenium webdriver element
        """
        if multi:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element = driver.find_element(By.XPATH, xpath)

        else:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element = driver.find_elements(By.XPATH, xpath)

        return element

def create_driver(headless):

        chrome_options = Options()

        if headless:
            chrome_options.headless = True
            chrome_options.add_argument("--window-size=1920,1080")
            # chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"  # noqa
            )

        return webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options
        )


def authenticate(email, password):

        login_url = 'https://discord.com/login'

        driver.get(login_url)

        email_input = element_from_xpath(driver, '//input[@name="email"]')
        email_input.send_keys(email)

        driver.send_keys(email)


driver = create_driver(headless=False)

email = 'felix.vemmer@gmail.com'