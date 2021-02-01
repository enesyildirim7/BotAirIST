import tweepy

#API entegrasyonu
def api():
    #Twitter hesabına bağlantı
    api_key = "YOUR_API_KEY"
    api_key_secret = "YOUR_API_KEY_SECRET"

    access_token = "YOUR_ACCESS_TOKEN"
    access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api