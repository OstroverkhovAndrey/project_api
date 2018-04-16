from telegram.ext import Updater, MessageHandler, Filters
import sys, requests
import pymorphy2
from distance import *
morph=pymorphy2.MorphAnalyzer()

def text(s):
    s=s.split(" ")
    a=[]
    for i in s:
        b=max(morph.parse(i), key=lambda x: x.score)
        a.append([str(b.tag).split(",")[0], b.score, b.normal_form])

    n=0
    s=None
    for i in a:
        if i[0]=="NOUN" and i[1]>n:
            s=i[2]
            n=int(i[1])

    if s==None:
        s=max(a, key=lambda x: int(x[1]))[2]

    return s


def searcher(toponym_to_find1, text):
    try:
        toponym_to_find1 = "+".join(toponym_to_find1.split())
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"geocode": toponym_to_find1, "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        ll =json_response["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']['Point']['pos'].split()
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "3c4a592e-c4c0-4949-85d1-97291c87825c"
        address_ll = "{0},{1}".format(ll[0], ll[1])
        search_params = {
            "apikey": api_key,
            "text": text,
            "lang": "ru_RU",
            "ll": address_ll,
            "type": "biz",
        }
        response = requests.get(search_api_server, params=search_params).json()
        k=0
        min=int(lonlat_distance(list(map(float, ll)), response['features'][0]['geometries'][0]['coordinates']))
        for i in range(len(response['features'])):
            if int(lonlat_distance(list(map(float, ll)), response['features'][i]['geometries'][0]['coordinates']))<min:
                k=i
                min=int(lonlat_distance(list(map(float, ll)), response['features'][i]['geometries'][0]['coordinates']))
        coords1=response['features'][k]['geometries'][0]['coordinates']
        org_point1 = "{0},{1}".format(coords1[0], coords1[1])
        org_point2 = "{0},{1}".format(ll[0], ll[1])
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        name =response['features'][k]['properties']['name']
        res=map_api_server+"?"+"&ll="+"{0},{1}".format((coords1[0]+float(ll[0]))/2, (coords1[1]+float(ll[1]))/2)+"&spn="+",".join([str(abs(coords1[0]-float(ll[0]))), str(abs(coords1[1]-float(ll[1])))])+"&l=map"+"&pt="+ "{1},home~{0},flag".format(org_point1,org_point2)
        dis =int(lonlat_distance(list(map(float, ll)), coords1))
        return [res, name, dis]
    except:
        return [None, None, None]

pos=None
def echo(bot, update):
    global pos
    a = update.message.text
    if a=="Привет":
        update.message.reply_text("Привет, напиши мне где ты находишся и куда тебе нужно, а я постараюсь найти где это, и как туда добраться")
        pos=None
    else:
        if pos==None:
            pos=a
        else:
            a=text(a)
            a, name, l=searcher(pos, a) #надо написать
            # a="https://www.google.com/maps/dir/52.7504575,41.4109015/%D1%83%D0%BB.+%D0%A0%D1%8B%D0%BB%D0%B5%D0%B5%D0%B2%D0%B0,+80,+%D0%A2%D0%B0%D0%BC%D0%B1%D0%BE%D0%B2,+%D0%A2%D0%B0%D0%BC%D0%B1%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D0%B1%D0%BB.,+392003/@52.7584593,41.4045441,15z/data=!3m1!4b1!4m9!4m8!1m1!4e1!1m5!1m1!1s0x4139114c23829f39:0x3c3c031b9dacaebc!2m2!1d41.4233701!2d52.762102"
            pos=None

        if a==None:
            update.message.reply_text("Что-то пошло не так")
        else:
            bot.sendPhoto(update.message.chat.id, a)
            update.message.reply_text("Это место называется "+str(name))
            update.message.reply_text("До тудова идти "+str(l)+" метров")
            update.message.reply_text("Если это не то что ты искал, сформулируй запрос корректнее")


def main():
    updater = Updater("593825537:AAGTULUB119MGcPpVYouQwaGml2tg5B3lT0")
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
