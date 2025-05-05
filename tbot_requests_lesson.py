import requests
import time
import config

API_URL = "https://api.telegram.org/bot"
BOT_TOKEN = config.BOT_TOKEN
API_CATS_URL = "https://api.thecatapi.com/v1/images/search"
ERROR_TEXT = "Здесь должна была быть картинка с котиком :("
MAX_COUNTER = 100

offset = -2
counter = 0
cat_response: requests.Response
cat_link: str

while counter < MAX_COUNTER:
    print("attempt =", counter)

    updates = requests.get(
        f"{API_URL}{BOT_TOKEN}/getUpdates?offset={offset + 1}"
    ).json()

    if updates["result"]:
        for result in updates["result"]:
            offset = result["update_id"]
            chat_id = result["message"]["from"]["id"]
            cat_response = requests.get(API_CATS_URL)
            user_message = result["message"]["text"]
            if cat_response.status_code == 200:
                cat_link = cat_response.json()[0]["url"]
                requests.get(
                    f'{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text="{user_message}" - это конечно хорошо. Но лучше вот тебе фото котика!'
                )
                requests.get(
                    f"{API_URL}{BOT_TOKEN}/sendPhoto?chat_id={chat_id}&photo={cat_link}"
                )
            else:
                requests.get(
                    f"{API_URL}{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={ERROR_TEXT}"
                )

    time.sleep(1)
    counter += 1
