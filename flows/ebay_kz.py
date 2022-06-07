import gspread
import pandas as pd
import requests
from df2gspread import df2gspread as d2g
from google.oauth2 import service_account
from prefect import Flow, task
from prefect.tasks.secrets import PrefectSecret
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


from flow_config import RUN_CONFIG, STORAGE


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
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)

    else:
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
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

    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


@task(log_stdout=True)
def check_listings(google_service_account, telegram_token):
    credentials = service_account.Credentials.from_service_account_info(
        google_service_account,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"],
    )

    gc = gspread.authorize(credentials)

    spreadsheet_key = "1n0J_1SpvBfJJNkyeXTCkOJpaF-u1aHEcvb9wXno28cc"
    wks_name = "ebay"

    worksheet = gc.open_by_key(spreadsheet_key).worksheet(wks_name)

    target_url = "https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/berlin/anzeige:angebote/preis::1400/c203l3331r30+wohnung_mieten.swap_s:nein+wohnung_mieten.zimmer_d:2%2C3"
    domain = "https://www.ebay-kleinanzeigen.de"

    driver = create_driver(headless=True)

    driver.get(target_url)

    cookie_accept_button = element_from_xpath(driver, "//button[@id='gdpr-banner-accept']")

    if len(cookie_accept_button) > 0:
        cookie_accept_button[0].click()

    listings = driver.find_elements_by_xpath('//article[@class="aditem"]')
    locations = driver.find_elements_by_xpath('//div[@class="aditem-main--top--left"]')
    locations = [location.text for location in locations]

    links_listings = [domain + link.get_attribute("data-href") for link in listings]

    favorite_locations = [
        "Mitte",
        "Prenzlauer Berg",
        "Friedrichshain",
        "Kreuzberg",
        "Lichtenberg",
    ]

    negative_keywords = [
        "tausch",
        "befristet",
        "temporär",
        "vorübergehend",
        "untermiete",
        "zwischenmiete",
    ]

    for location, link in zip(locations, links_listings):

        print(f"Checking {location}")

        if any(fav in location for fav in favorite_locations):

            driver.get(link)

            print(f"Getting details for listing: {link}")

            title = driver.find_element_by_xpath("//h1").text
            publish_date = driver.find_element_by_xpath("//div[@id='viewad-extra-info']").text
            publish_date = publish_date.split("\n")[0]

            features = driver.find_elements_by_xpath('//li[@class="addetailslist--detail"]')
            features = [header.text for header in features]

            feature_dict = {}

            for feature in features:
                if "\n" in feature:
                    feature_dict[feature.split("\n")[0]] = feature.split("\n")[1]

            equipment = driver.find_elements_by_xpath('//li[@class="checktag"]')
            equipment = [equipment.text for equipment in equipment]

            description = driver.find_element_by_xpath("//p[@id='viewad-description-text']").text
            descripition = [word.lower() for word in description.split()]

            if any(neg in descripition for neg in negative_keywords):
                print(f"{title} is a negative ad machting a negative keyword")
                continue

            if "Balkon" not in equipment:
                print(f"{title} is missing a balcony")
                continue

            existing_df = pd.DataFrame(worksheet.get_all_records())

            links = existing_df["link"].tolist()

            if link in links:
                print(f"Link {link} already in list...")
                continue

            temp_df = pd.DataFrame(
                {
                    "link": [link],
                }
            )

            existing_df = existing_df.append(temp_df, ignore_index=True)

            worksheet.update([existing_df.columns.values.tolist()] + existing_df.values.tolist())

            bot_message = (
                f"💬 Anzeige: {title} \n\n"
                f"🕑 Published on: {publish_date} \n\n"
                f"🔗 Link: {link} \n\n"
                f"🏠 Anzahl Schlafzimmer: {feature_dict.get('Schlafzimmer')} \n\n"
                f"💵 Warmmiete: {feature_dict.get('Warmmiete')} \n\n"
                f"📐 Größe: {feature_dict.get('Wohnfläche')} \n\n"
                f"🏢 Verfügbar ab: {feature_dict.get('Verfügbar ab')} \n\n"
            )

            bot_token = telegram_token
            bot_chatID = "-1001656270853"

            send_text = (
                "https://api.telegram.org/bot"
                + bot_token
                + "/sendMessage?chat_id="
                + bot_chatID
                + "&parse_mode=Markdown&text="
                + bot_message
            )

            print(f"Sending message to telegram: {send_text}")

            response = requests.get(send_text)


FLOW_NAME = "ebay_kleinanzeigen"

with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:

    google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT")
    telegram_token = PrefectSecret("TELEGRAM_TOKEN")

    check_listings(google_service_account, telegram_token)

if __name__ == "__main__":
    # flow.run()
    flow.register(project_name="datadrivendao")
