# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 23:42:02 2021

@author: VICKY
"""

import time
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set matplotlib default values
plt.style.use('fivethirtyeight')

params = {'legend.fontsize': 14,
          'figure.figsize': (15, 8),
         'axes.labelsize': 14,
         'axes.titlesize': 14,
         'xtick.labelsize': 14,
         'ytick.labelsize': 14,
         'axes.facecolor': 'white',
         'axes.edgecolor': 'white',
         'axes.grid': 'False',
         'figure.facecolor': 'white'}
plt.rcParams.update(params)


def create_api():

    consumer_key = "qR2iL5WqNiDOvpnrJ5LZDJj1d"
    consumer_secret = "OEEO0wirEbEf3mMJ8PtSB0SAgSzCzq5nbd9zMVPY2J27lKjDlv"
    access_token = "1349480856100986882-Z1sCAeWuSxsOxSy3AUMT90Fw3GJPpq"
    access_token_secret = "0VBEtYLW3j9qDaQA2y9AZgQuZDi9q8rK9xnIUBYgvoOyJ"
    
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api


def fichero():

    url = "https://datos.comunidad.madrid/catalogo/dataset/7da43feb-8d4d-47e0-abd5-3d022d29d09e/resource/f22c3f43-c5d0-41a4-96dc-719214d56968/download/covid19_tia_muni_y_distritos_s.csv"
    c = pd.read_csv(url, delimiter=';', encoding='iso-8859-1', decimal=',')
    d = c[['municipio_distrito', 'fecha_informe', 'casos_confirmados_ultimos_14dias', 'tasa_incidencia_acumulada_ultimos_14dias']]
    d.columns = ['municipio', 'fecha', 'casos', 'tasa']
    d['fecha'] = d['fecha'].str.slice(0, 10)
    d['fecha'] = pd.to_datetime(d['fecha'])
    d['habitantes'] = d['casos'] * 100000 / d['tasa']
    
    # Calcular tasa media ponderada por habitantes de la Comunidad
    tasa_media = d.groupby(['fecha']).sum().reset_index()
    tasa_media['tasa'] = tasa_media['casos'] / tasa_media['habitantes'] * 100000

    return tasa_media, d


def municipio_grafico(municipio, d):
    
    # analisis del municipio
    d_get = d[d['municipio'] == municipio].reset_index()
    
    # Datos para municipio o distrito concreto
    x1 = d_get['fecha']
    y1 = d_get['tasa']
    
    return x1, y1
    
    
def grafico(x1, y1, tasa_media, municipio):

    plt.figure()
    
    # Datos para Comunidad de Madrid
    x = tasa_media['fecha']
    y = tasa_media['tasa']

    # Grafico de municipio concreto
    plt.plot(x1, y1, lw=5, ls='-', alpha=1, color=sns.color_palette()[0], label= municipio)
    plt.plot(x1[0], y1[0], markersize=14, marker='o', color=sns.color_palette()[0])
    # Grafico de Comunidad de Madrid
    plt.plot(x, y, lw=3, ls='-', alpha=0.1, color=sns.color_palette()[4], label='Comunidad de Madrid')
    plt.fill_between(x, 0, y, alpha=0.1, color=sns.color_palette()[4])

    plt.grid(axis='y')
    plt.tick_params(axis='x', direction='in', length=10, width=1)
    plt.legend(loc='best')
    plt.ylabel('Tasa', rotation=90, ha='right')
    plt.title('Casos positivos por 100.000 habitantes en los últimos 14 días', fontsize=18)

    plt.savefig('grafico.png', bbox_inches='tight', pad_inches=0.3, dpi=220, facecolor='white')
    plt.close()


def check_day(last_day, table):

    date = table['fecha'].dt.strftime('%d/%m/%Y')
    date = date.values.tolist()
    actual_day = date[0]

    print(last_day)
    print(actual_day)
    if actual_day == last_day:
        return False
    else:
        return True


def create_tweets(tasa_media, table, municipios, api):

    # Loop para crear tweets
    for municipio in municipios:
        # Tasa y hora del primer municio de la lista
        date_m, tasa_m = municipio_grafico(municipio, table)

        # Crea grafico
        grafico(date_m, tasa_m, tasa_media, municipio)

        # Convertir la tabla de fecha y tasa a lista para que no de problemas
        date = date_m.dt.strftime('%d/%m/%Y')
        date = date.values.tolist()
        tasa = tasa_m.values.tolist()

        # Publicacion de tweet de ultimo valor con foto
        create_tweet(municipio, date[0], tasa[0], api)

        time.sleep(60*5)

    # Ultima dia que se publicaron datos
    last_day = date[0]

    return last_day



def create_tweet(municipio,date, tasa, api):
    
    text = "A "+ str(date)+", " + str(municipio)+ " tiene una tasa de incidencia  "+ str(tasa)+ " contagios."
    api.update_with_media('grafico.png', status=text)

def main():

    api = create_api()

    # Lista municipios
    municipios = ['Madrid-Retiro',
                  'Madrid-Salamanca',
                  'Madrid-Centro',
                  'Madrid-Arganzuela',
                  'Madrid-Chamartín',
                  'Madrid-Tetuán',
                  'Madrid-Chamberí',
                  'Madrid-Fuencarral-El Pardo',
                  'Madrid-Moncloa-Aravaca',
                  'Madrid-Latina',
                  'Madrid-Carabanchel',
                  'Madrid-Usera',
                  'Madrid-Puente de Vallecas',
                  'Madrid-San Blas - Canillejas',
                  'Madrid-Barajas',
                  'Madrid-Moratalaz',
                  'Madrid-Ciudad Lineal',
                  'Madrid-Hortaleza',
                  'Madrid-Villaverde',
                  'Madrid-Villa de Vallecas',
                  'Madrid-Vicálvaro',
                  'Pozuelo de Alarcón',
                  'Galapagar',
                  'Alcorcón',
                  'Las Rozas de Madrid',
                  'Aranjuez',
                  'Coslada',
                  'Fuenlabrada',
                  'Pinto',
                  'Ciempozuelos',
                  'Móstoles',
                  'Leganés',
                  'Villaviciosa de Odón',
                  'Navalcarnero',
                  'Arroyomolinos',
                  'Parla',
                  'Boadilla del Monte',
                  'San Sebastián de los Reyes',
                  'Arganda del Rey',
                  'Paracuellos de Jarama',
                  'Collado Villalba',
                  'Valdemoro',
                  'Tres Cantos',
                  'Rivas-Vaciamadrid',
                  'Alcobendas',
                  'Alcalá de Henares',
                  'Colmenar Viejo',
                  'San Fernando de Henares',
                  'Torrejón de Ardoz',
                  'Getafe',
                  'Majadahonda']

    municipios.sort()
    last_day = None

    while api is not None:

        # Datos actuales del fichero
        tasa_media, table = fichero()

        # Checks la ultima hora del archivo con la ultima publicada
        status = check_day(last_day, table)


        if status == True:
            last_day = create_tweets(tasa_media, table, municipios, api)
        else:
            # Poner en espera el sistema durante un dias
            time.sleep(3600 * 24)


if __name__ == "__main__":

    main()
