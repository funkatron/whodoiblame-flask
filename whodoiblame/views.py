from flask import request, render_template, redirect, url_for
from .geocodio import get_address_data
from .propublica import get_district_data
from pymemcache.client.base import Client
import json

from whodoiblame import app

cache = Client((app.config['MEMCACHE_HOST'], app.config['MEMCACHE_PORT']))


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.jinja2')


@app.route('/', methods=['POST'])
def get_results():
    address = request.form.get('address', None)

    cache_key = "GEO_%s" % address
    address_info_json = cache.get(cache_key)

    if address_info_json:
        address_info = json.loads(address_info_json)
        print('pulled address from cache')
    else:
        address_info = get_address_data(app.config['GEOCODIO_API_KEY'], address)
        cache.set(cache_key, json.dumps(address_info), expire=3600)
        print("set to address to cache")

    state = address_info['address_components']['state']
    district = address_info['fields']['congressional_district']['district_number']

    return redirect(url_for('show_district_info', state=state, district=district))


@app.route('/<state>/<int:district>', methods=['GET'])
def show_district_info(state, district):
    cache_key = "REPS_%s_%s" % (state, district)
    reps_json = cache.get(cache_key)

    if reps_json:
        reps = json.loads(reps_json)
        print('pulled reps from cache')
    else:
        reps = get_district_data(app.config['PROPUBLICA_API_KEY'], state, district)
        cache.set(cache_key, json.dumps(reps), expire=3600)
        print("set reps to cache")

    return render_template('pages/index.jinja2', reps=reps)
