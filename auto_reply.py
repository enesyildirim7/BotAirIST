import tweepy
import time
from datetime import datetime, timedelta
from get_data import misspelling
from authorise import api

#İstasyon adı içeren bütün mentionları yanıtlar
def autoreply():
    id = 0
    while True:
        try:
            minute = datetime.today().minute
            if minute in range(6):
                time.sleep((6-minute)*60)
            ment_list = list()
            if id == 0:
                for ment in api().search("@BotAirIST", result_type="recent", count=1, since_id=id):
                    id = ment.id
                    time.sleep(6)
            for ment in api().search("@BotAirIST", result_type="recent", count=100, since_id=id):
                ment_list.append([ment.user.screen_name,ment.text.split(" "),ment.id])
                id = ment_list[0][2]
                print(ment.text)
                for item in ment_list:
                    username = item[0]
                    istasyon = item[1]
                    reply_id = item[2]
                if misspelling(istasyon) != False:
                    tweet = f"@{username}\n{str(misspelling(istasyon))}"
                    api().update_status(tweet,in_reply_to_status_id=reply_id)
                    print(tweet)
                    print("*************************")
                else:
                    continue
            print("------------------------")
            time.sleep(6)
            del ment_list
        except tweepy.RateLimitError:
            rate_limit = "API sınırlarına ulaşıldı. Lütfen 15 dakika sonra tekrar deneyiniz."
            print(rate_limit)
            continue
    return misspelling(istasyon)