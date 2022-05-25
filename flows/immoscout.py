import requests
import pandas as pd
import os
from google.oauth2 import service_account
import gspread
from prefect import Flow, task
from prefect.tasks.secrets import PrefectSecret
from df2gspread import df2gspread as d2g
from datetime import datetime
from common import df_to_gcs_parquet
import time

from flow_config import RUN_CONFIG, STORAGE

@task(log_stdout=True)
def check_listings(google_service_account, telegram_token):
    credentials = service_account.Credentials.from_service_account_info(
        google_service_account,
        scopes = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'],
    )

    gc = gspread.authorize(credentials)

    spreadsheet_key = '1n0J_1SpvBfJJNkyeXTCkOJpaF-u1aHEcvb9wXno28cc'
    wks_name = 'sent'

    worksheet = gc.open_by_key(spreadsheet_key).worksheet(wks_name)

    headers= {
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest'
    }

    for page_number in range(0,1):

        api_url = f"https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mit-balkon-mieten?numberofrooms=2.0-&price=1000.0-1600.0&livingspace=50.0-&exclusioncriteria=projectlisting,swapflat&pricetype=rentpermonth&sorting=2&enteredFrom=result_list&pagenumber={page_number}"

        json_data = requests.post(api_url).json()

        try:
            results = json_data['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']
        except:
            break

        for e in results:

            time.sleep(1)

            try:
                publish_date = e.get('@publishDate')
                # if publish_date:
                #     formatted = datetime.fromisoformat(publish_date).date()
                #     date_now = datetime.now().date()

                #     if formatted < date_now:
                #         break

            except:
                publish_date = None
                # print('Publish date Exception')
            try:
                title = e.get('resultlist.realEstate').get('title')
            except:
                title = None
                # print('Title Exception')
            try:
                number_of_rooms = e.get('resultlist.realEstate').get('numberOfRooms')
            except:
                number_of_rooms = None
                # print('Number of rooms Exception')
            try:
                quarter = e.get('resultlist.realEstate').get('address').get('quarter')
            except:
                quarter = None
                # print('Quarter Exception')
            try:
                square_meters = float(e.get('resultlist.realEstate').get('livingSpace'))
            except:
                square_meters = None
                # print('Square meters Exception')
            try:
                gmaps_link = f"https://maps.google.com/?q={e.get('resultlist.realEstate').get('address').get('wgs84Coordinate').get('latitude')},{e.get('resultlist.realEstate').get('address').get('wgs84Coordinate').get('longitude')}"
            except:
                gmaps_link = None
                # print('Gmaps link Exception')
            try:
                price_cold = float(e.get('resultlist.realEstate').get('price').get('value'))
            except:
                price_cold = None
                # print('Price cold Exception')
            try:
                link = f"https://www.immobilienscout24.de/expose/{e.get('resultlist.realEstate').get('@id')}"
            except:
                link = None
                # print('Link Exception')
            try:
                name = f"{e.get('resultlist.realEstate').get('contactDetails').get('firstname')} {e.get('resultlist.realEstate').get('contactDetails').get('lastname')}"
            except:
                name = None
                # print('Name Exception')
            try:
                phone = e.get('resultlist.realEstate').get('contactDetails').get('phoneNumber')
            except:
                phone = None
                # print('Phone Exception')

            desired_quarters = [
                'Mitte (Mitte)',
                'Prenzlauer Berg (Prenzlauer Berg)',
                'Friedrichshain (Friedrichshain)',
                'Kreuzberg (Kreuzberg)',
                'Lichtenberg (Lichtenberg)',

            ]

            if quarter not in desired_quarters:
                print(f"Quarter {quarter} not matching...")
                continue

            existing_df = pd.DataFrame(worksheet.get_all_records())

            if "tausch" in title.lower():
                print(f"Tausch in title {title}...")
                continue

            links = existing_df['link'].tolist()

            if link in links:
                print(f"Link {link} already in list...")
                continue

            if quarter in desired_quarters and not 'tausch' in title.lower() and link not in links:

                print(f"{publish_date}, {title}, {number_of_rooms}, {quarter}, {square_meters}, {gmaps_link}, {price_cold}, {link}, {name}, {phone}")
                print('_____________________________________________')

                temp_df = pd.DataFrame({
                    'link': [link],
                })

                existing_df = existing_df.append(temp_df, ignore_index=True)

                worksheet.update([existing_df.columns.values.tolist()] + existing_df.values.tolist())

                bot_message = (
                    f"💬 Anzeige: {title} \n\n"
                    f"🕑 Published on: {publish_date} \n\n"
                    f"🔗 Link: {link} \n\n"
                    f"🏠 **Anzahl Zimmer:** {number_of_rooms} \n\n"
                    f"💵 Preis: {price_cold}€ \n\n"
                    f"📐 Größe: {square_meters}m² \n\n"
                    f"🏢 Stadteil: {quarter} \n\n"
                    f"📍 Karte: {gmaps_link} \n\n"
                    f"🥸 Kontakt Person: {name}\n\n"
                    f"📞 Telefon: {phone} \n\n"
                )

                bot_token = telegram_token
                bot_chatID = '-1001656270853'

                send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

                response = requests.get(send_text)


FLOW_NAME = "immobilienscout24_bot"

with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:


    google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT")
    telegram_token = PrefectSecret("TELEGRAM_TOKEN")

    check_listings(google_service_account, telegram_token)

if __name__ == "__main__":
    #flow.run()
    flow.register(project_name="datadrivendao")
