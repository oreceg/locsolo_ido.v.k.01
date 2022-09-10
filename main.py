import requests
from datetime import datetime

''' 
Feladat: szükséges-e bekapcsolni reggel (8:00) és/vagy délután (14:00) a kerti locsolót vagy sem.
Mikor nem szükséges locsolni:
Ha a várható napi átlag hőmérséglet  15 C alatt (hidegben), vagy ha esni fog az eső.
Mikor szükséges locsolni:
Ha a várható napi átlag hőmérséglet legalábbb 15 C fok feletti (meleg), és várhatóan nem fog esni az eső. 
Az időjárási adatok lekérésére az Open Weather Map API lesz használva.
'''
#   Open Weather Map API key, és a szükséges URL -k
API_KEY = 'ba90bdde34b41af55d498d88ad37935c'
ONE_CALL_API = 'https://api.openweathermap.org/data/2.5/onecall'
GEOCODING_API = 'http://api.openweathermap.org/geo/1.0/direct'


#   A város koordinátáinak lekérése és tárolása a GEOCODING API -val
def get_coordinates(varos):
    geo_payload = {
        'q': varos,
        'appid': API_KEY
    }
    geo_resp = requests.get(GEOCODING_API, params=geo_payload)

    geo_resp = geo_resp.json()[0]
    return geo_resp['lat'], geo_resp['lon']

#    Az időjárási adatok lekérése és tárolása a ONE CALL API 1.0 -val
def get_weather(lat, lon):
    weather_payload = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'hu',
        'exclude': 'minutely,daily'
    }
    weather_resp = requests.get(ONE_CALL_API, params=weather_payload)
    weather_resp = weather_resp.json()
    return weather_resp

def main():
    varos = input("Adja mneg a város nevét: ")
    varos_koordinatai = get_coordinates(varos)
    idojarasi_adatok = get_weather(varos_koordinatai[0], varos_koordinatai[1])
    lekeres_datum = datetime.fromtimestamp(idojarasi_adatok['current']['dt']).strftime('%Y.%m.%d. %H:%M:%S')

#   locsolásidők meghatározása
    locsolasi_ora_1 = 8
    locsolasi_ora_2 = 14
    locsolasi_ora_1_index = 0
    locsolasi_ora_2_index = 0
    index = 0
    while index < 25:
        ora = int(datetime.fromtimestamp(idojarasi_adatok['hourly'][index]['dt']).strftime('%H'))
        if ora == locsolasi_ora_1:
            locsolasi_ora_1_index = index
            index += 1
        elif ora == locsolasi_ora_2:
            locsolasi_ora_2_index = index
            index += 1
        else:
            index += 1
    locsolasi_ora_1 = \
        datetime.fromtimestamp(idojarasi_adatok['hourly'][locsolasi_ora_1_index]['dt']).strftime('%Y.%m.%d. %H')
    locsolasi_ora_2 = \
        datetime.fromtimestamp(idojarasi_adatok['hourly'][locsolasi_ora_2_index]['dt']).strftime('%Y.%m.%d. %H')

# a locsolás eldöntése
    def locsolas_beallito(locsolasi_ora_index):
        varhato_varos_homerseglet = idojarasi_adatok['hourly'][locsolasi_ora_index]['temp']
        varhato_varos_idojaras_kod = int(idojarasi_adatok['hourly'][locsolasi_ora_index]['weather'][0]['id'])
        varhato_ido_csapadek_vizsgalat = (varhato_varos_idojaras_kod >= 200 and varhato_varos_idojaras_kod < 400) \
                                         or (varhato_varos_idojaras_kod >= 500 and varhato_varos_idojaras_kod < 700)
        varhato_varos_csapadek_mennyiseg = idojarasi_adatok['hourly'][index]['pop']
        elmult_varos_csapadek_mennyiseg =  idojarasi_adatok['hourly'][(index-1)]['pop'] != 0 \
                                           and idojarasi_adatok['hourly'][(index-2)]['pop'] != 0
        locsolas = ('Hideg van, nem kell locsolni',
                    'Nem szükséges locsolni, esni fog az eső.',
                    'Felhős az ég, de nem fog esni, locsolni kell.',
                    'Meleg lesz, locsolni kell!',
                    "Eset az eső nem kell locsolni")

        if varhato_varos_homerseglet < 15:
            locsolas_beallit = locsolas[0]

        elif varhato_ido_csapadek_vizsgalat:

            if varhato_varos_csapadek_mennyiseg != 0:

                if elmult_varos_csapadek_mennyiseg:
                    locsolas_beallit = locsolas[4]

                else:
                    locsolas_beallit = locsolas[1]

            else:
                locsolas_beallit = locsolas[2]

        else:
            locsolas_beallit = locsolas[3]

        return locsolas_beallit

    locsalas_beallit_1 = locsolas_beallito(locsolasi_ora_index=locsolasi_ora_1_index)
    locsalas_beallit_2 = locsolas_beallito(locsolasi_ora_index=locsolasi_ora_2_index)
    varhato_varos_homerseglet_1 = idojarasi_adatok['hourly'][locsolasi_ora_1_index]['temp']
    varhato_varos_idojaras_1 = idojarasi_adatok['hourly'][locsolasi_ora_1_index]['weather'][0]['description']
    varhato_varos_homerseglet_2 = idojarasi_adatok['hourly'][locsolasi_ora_2_index]['temp']
    varhato_varos_idojaras_2 = idojarasi_adatok['hourly'][locsolasi_ora_2_index]['weather'][0]['description']
    elvalaszto = '------------------------------------------------------------------------'

    print(elvalaszto)
    print("Időjárási adatok - {}  || {}".format(varos.capitalize(), 'Lekérdezés dátuma ' + lekeres_datum))
    print(elvalaszto)
    if locsolasi_ora_1_index < locsolasi_ora_2_index:
        print(locsolasi_ora_1 + ' -kor ')
        print("A várható hőmérséglet: {:.2f} °C".format(varhato_varos_homerseglet_1))
        print("A várható időjárás   :", varhato_varos_idojaras_1)
        print(elvalaszto)
        print("locsolási javaslat: \n" + locsalas_beallit_1)
        print(elvalaszto)
        print(elvalaszto)
        print(locsolasi_ora_2 + ' -kor ')
        print("A várható hőmérséglet: {:.2f} °C".format(varhato_varos_homerseglet_2))
        print("A várható időjárás   :", varhato_varos_idojaras_2)
        print(elvalaszto)
        print("locsolási javaslat: \n" + locsalas_beallit_2)
        print(elvalaszto)
    else:
        print(locsolasi_ora_2 + ' -kor ')
        print("A várható hőmérséglet: {:.2f} °C".format(varhato_varos_homerseglet_2))
        print("A várható időjárás   :", varhato_varos_idojaras_2)
        print(elvalaszto)
        print("locsolási javaslat: \n" + locsalas_beallit_2)
        print(elvalaszto)
        print(elvalaszto)
        print(locsolasi_ora_1 + ' -kor ')
        print("A várható hőmérséglet: {:.2f} °C".format(varhato_varos_homerseglet_1))
        print("A várható időjárás   :", varhato_varos_idojaras_1)
        print(elvalaszto)
        print("locsolási javaslat: \n" + locsalas_beallit_1)
        print(elvalaszto)
    print(elvalaszto)

main()
