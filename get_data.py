import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

class get_data():
    def __init__(self):
        #Verilerin alınacağı internet sitesine erişim
        self.url = "https://havakalitesi.ibb.gov.tr"
        self.erisim = requests.get(self.url)

        #Web sitesinin içeriği
        self.icerik = self.erisim.content
        self.derleme = BeautifulSoup(self.icerik,"html.parser")

        #İstasyon isimleri web sitesinden alınıp listeye ekleniyor
        self.istasyonlar = list()
        for istasyon in self.derleme.find_all("div",{"class":"col-xs-12"}):
            self.istasyonlar.append(istasyon.text)

        #İstasyonların linkleri alınıp listeye ekleniyor
        self.istasyon_link = list()
        for link in self.derleme.find_all("a",attrs={"href": re.compile("/Pages/AirQualityDetails/")}):
            self.istasyon_link.append(self.url + link.get("href"))

#Web sitesinden alınan verilerin saklanacağı veri çerçevesi
class data():
    def __init__(self):
        self.get_data = get_data()
        self.data = pd.DataFrame(self.get_data.istasyon_link,index=self.get_data.istasyonlar,columns=["İstasyon Linkleri"])
        self.data.sort_index(inplace=True)

#İçerisine verilen istasyonun güncel parametre verilerini bize döndürür
def istasyon_verisi(istasyon):
    if istasyon in data().data.index.values.tolist():
        response = requests.get(data().data.loc[istasyon,"İstasyon Linkleri"])
        content = response.content
        parser = BeautifulSoup(content,"html.parser")
        bolge = [i.text for i in parser.find_all("div",{"class":"col-xs-12"})][0]
        pm10 = [pm10.text.split()[0].strip(" ").replace(",",".") for pm10 in parser.find_all("div",{"data-tparam":"PM10"})][0]
        pm25 = [pm25.text.split()[0].strip(" ").replace(",",".") for pm25 in parser.find_all("div",{"data-tparam":"PM25"})][0]
        so2 = [so2.text.split()[0].strip(" ").replace(",",".") for so2 in parser.find_all("div",{"data-tparam":"SO2"})][0]
        o3 = [o3.text.split()[0].strip(" ").replace(",",".") for o3 in parser.find_all("div",{"data-tparam":"O3"})][0]
        co = [co.text.split()[0].strip(" ").replace(",",".") for co in parser.find_all("div",{"data-tparam":"CO"})][0]
        no2 = [no2.text.split()[0].strip(" ").replace(",",".") for no2 in parser.find_all("div",{"data-tparam":"NO2"})][0]
        hki = parser.find("div",{"class":"value"}).text.split()[0].strip(" ")
        if int(hki) <= 50:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"Kalite İndeksi (HKİ): {hki} - İyi 😇\n⚠️Hava kalitesi gayet iyi. Risk oldukça az veya hiç risk teşkil etmiyor.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        elif int(hki) <= 100:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"Kalite İndeksi (HKİ): {hki} - Orta 😐\n⚠️Hava kalitesi uygun fakat hassas kişiler için sağlık endişesi oluşabilir.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        elif int(hki) <= 150:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"Kalite İndeksi (HKİ): {hki} - Hassas 🤧\n⚠️Hassas kişileri için sağlık sorunları oluşabilir.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        elif int(hki) <= 200:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"Kalite İndeksi (HKİ): {hki} - Sağlıksız 😷\n⚠️Herkes sağlık etkileri yaşamaya başlayabilir. Hassas kişiler için ciddi sağlık sorunları oluşabilir.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        elif int(hki) <= 300:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"Kalite İndeksi (HKİ): {hki} - Kötü 🥵\n🚨Sağlık açısından acil durum oluşturabilir. Nüfusun tamamının etkilenme olasılığı yüksektir.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        elif int(hki) <= 500:
            return f"Konumunuza en yakın istasyon : {istasyon}\n\n" \
                   f"HKİ: {hki} - Tehlikeli ☠️\n🚨Sağlık alarmı: Ciddi sağlık etkileri ile karşılaşılabilir.\n\n" \
                   f"🔗Detaylı istasyon verileri için: {data().data.loc[istasyon,'İstasyon Linkleri']}"
        else:
            return "Üzgünüm, yaşadığın yerdeki verilere ulaşamadım. :(\nDaha detaylı bilgiyi burada bulabilirsin: https://havakalitesi.ibb.gov.tr/"
    else:
        return "Üzgünüm, yaşadığın yerdeki verilere ulaşamadım. :(\nDaha detaylı bilgiyi burada bulabilirsin: https://havakalitesi.ibb.gov.tr/"

#Twitter kullanıcılarından alınan mentionlarda yazım yanlışı bulunsa dahi, aranan veya en yakın istasyonun verisine ulaşır
def misspelling(stations):
    for station in stations:
        if station[0] == "@":
            continue
        elif station[0] == " " or station[1] == " ":
            continue
        else:
            adalar = ["Adalar","adalar","Büyükada","büyükada","Büyük ada","büyük ada"
                    "Heybeliada","heybeliada","heybeli ada","Heybeli ada"
                    "Kınalıada","Kınalı ada","kınalıada","kınalı ada"
                    "Burgazadası","burgazadası","Burgaz adası","burgaz adası"]
            if station in adalar:
                return istasyon_verisi("Büyükada")

            elif station in ["Arnavutköy", "arnavutköy", "Arnavut köy", "arnavut köy"]:
                return istasyon_verisi("Arnavutköy")

            elif station in ["Ataşehir", "ataşehir", "Ata şehir", "ata şehir", "Göztepe", "göztepe"]:
                return istasyon_verisi("Göztepe")

            elif station in ["Avcılar", "avcılar", "avcilar", "Avcilar"]:
                return istasyon_verisi("Avcılar")

            elif station in ["Bağcılar", "bağcılar", "Bagcilar", "bagcilar"]:
                return istasyon_verisi("Bağcılar")

            elif station in ["Bahçelievler", "bahçelievler", "Bahçeli evler", "bahçeli evler",
                             "Şirinevler", "şirinevler", "Şirin evler", "şirin evler"]:
                return istasyon_verisi("Şirinevler")

            elif station in ["Bakırköy", "bakırköy", "Bakır köy", "bakır köy",
                             "Yenibosna", "yenibosna", "yeni bosna", "Yeni bosna"]:
                return istasyon_verisi("Yenibosna")

            elif station in ["Başakşehir", "başakşehir", "Başak şehir", "başak şehir"]:
                return istasyon_verisi("Başakşehir")

            elif station in ["Bayrampaşa", "bayrampaşa", "Bayram paşa", "bayram paşa",
                             "Güngören", "güngören", "Esenler", "esenler"]:
                return istasyon_verisi("Esenler")

            elif station in ["Beşiktaş", "beşiktaş", "Besiktas", "besiktas", "BJK", "bjk", "8taş", "8tas"]:
                return istasyon_verisi("Beşiktaş")

            elif station in ["Beykoz", "beykoz"]:
                return istasyon_verisi("Kandilli 2")

            elif station in ["Beylikdüzü", "Beylik düzü", "beylikdüzü", "beylik düzü",
                           "Büyükçekmece", "büyükçekmece", "Büyük çekmece", "büyük çekmece",
                           "Esenyurt", "Esen yurt", "esenyurt", "esen yurt",
                           "Küçükçekmece", "küçükçekmece", "Küçük çekmece", "küçük çekmece"]:
                return istasyon_verisi("Esenyurt")

            elif station in ["Alibeyköy","alibeyköy","alibey köy","Alibey köy","Beyoğlu", "beyoğlu", "Bey oğlu", "bey oğlu",
                           "Eyüpsultan", "Eyüp sultan", "eyüpsultan", "eyüp sultan", "Eyüp", "eyüp",
                           "Gaziosmanpaşa", "gaziosmanpaşa", "Gaziosman paşa", "Gazi osmanpaşa", "gaziosman paşa", "gazi osmanpaşa"]:
                return istasyon_verisi("Alibeyköy")

            elif station in ["Çatalca", "çatalca", "catalca", "Catalca"]:
                tweet = "Bulunduğunuz konumda veya yakınlarında hava ölçüm istasyonu bulunmamaktadır."
                return tweet

            elif station in ["Çekmeköy", "çekmeköy", "cekmeköy", "cekmekoy", "Çekme köy", "çekme köy", "cekme koy", "cekme köy"]:
                return istasyon_verisi("Sancektepe")

            elif station in ["Fatih", "fatih", "aksaray", "ak saray", "Aksaray", "Ak saray", "Eminönü", "eminönü",
                             "Emin önü", "emin önü"]:
                return istasyon_verisi("Aksaray")

            elif station in ["Kadıköy", "kadıköy", "kadiköy", "kadikoy", "Kadiköy", "Kadikoy", "Fenerbahçe", "fenerbahçe",
                             "Fenerbahce", "fenerbahce", "Fener bahçe", "fener bahçe", "Fener bahce", " fener bahce"]:
                return istasyon_verisi("Kadıköy")

            elif station in ["Kağıthane", "kağıthane", "kağıt hane", "Kağıt hane"]:
                return istasyon_verisi("Kağıthane 1")

            elif station in ["Kartal", "kartal"]:
                return istasyon_verisi("Kartal")

            elif station in ["Kumköy", "kumköy", "kum köy", "Kum köy"]:
                return istasyon_verisi("Kumköy")

            elif station in ["Maltepe", "maltepe"]:
                return istasyon_verisi("Kartal")

            elif station in ["Maslak", "maslak"]:
                return istasyon_verisi("Maslak")

            elif station in ["Pendik", "pendik", "Kurtköy", "kurtköy"]:
                return istasyon_verisi("Kartal")

            elif station in ["Sancektepe", "sancaktepe", "Sancak tepe", "sancak tepe"]:
                return istasyon_verisi("Sancaktepe")
            
            elif station in ["Selimiye", "selimiye"]:
                return istasyon_verisi("Selimiye")    

            elif station in ["Sarıyer", "sarıyer"]:
                return istasyon_verisi("Sarıyer")

            elif station in ["Silivri", "silivri"]:
                return istasyon_verisi("Silivri")

            elif station in ["Sultanbeyli", "Sultan beyli", "sultanbeyli", "sultan beyli"]:
                return istasyon_verisi("Sultanbeyli")

            elif station in ["Sultangazi", "sultangazi", "Sultan gazi", "sultan gazi"]:
                return istasyon_verisi("Sultangazi 1")

            elif station in ["Şile", "şile"]:
                return istasyon_verisi("Şile")

            elif station in ["Şişli", "şişli", "Mecidiyeköy", "mecidiyeköy"]:
                return istasyon_verisi("Mecidiyeköy")

            elif station in ["Tuzla", "tuzla"]:
                return istasyon_verisi("Tuzla")

            elif station in ["Ümraniye", "ümraniye"]:
                return istasyon_verisi("Ümraniye 2")

            elif station in ["Üsküdar", "üsküdar"]:
                return istasyon_verisi("Üsküdar 1")

            elif station in ["Zeytinburnu", "zeytinburnu", "Zeytin burnu", "zeytin burnu"]:
                return istasyon_verisi("Aksaray")

            else:
                if station == stations[-1]: #Tweetteki kelimenin son olup olmadığını kontrol eder
                    return False
                    break
                else:
                    continue

a = misspelling(["selimiye"])
print(a)