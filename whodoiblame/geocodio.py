import requests

GEOCODIO_BASE_URL = 'http://api.geocod.io/v1/'


def get_address_data(api_key, address, fields='cd,stateleg'):
    resp = requests.get(GEOCODIO_BASE_URL + 'geocode', params={
        'api_key': api_key, 'q': address, 'fields': fields
    })

    return resp.json()['results'][0]
