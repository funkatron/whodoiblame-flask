from flask import request, render_template, redirect, url_for
from .geocodio import get_address_data
from .propublica import get_district_data
from pymemcache.client.base import Client
import pickle
import hashlib

from whodoiblame import app

cache = Client((app.config['MEMCACHE_HOST'], app.config['MEMCACHE_PORT']))


def get_md5(to_hash):
    m = hashlib.md5()
    m.update(to_hash.encode('utf8'))
    return m.hexdigest()


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.jinja2')


@app.route('/', methods=['POST'])
def get_results():
    address = request.form.get('address', None)

    cache_key = get_md5("GEO_%s" % address)
    address_info_pickle = cache.get(cache_key)

    if address_info_pickle:
        address_info = pickle.loads(address_info_pickle)
        print('pulled address from cache')
    else:
        try:
            address_info = get_address_data(app.config['GEOCODIO_API_KEY'], address)
        except Exception:
            error_msg = "We encountered a problem with that address. Try being more specific, and include a ZIP code"
            return render_template('pages/error.jinja2', error_msg=error_msg)
        cache.set(cache_key, pickle.dumps(address_info), expire=3600)
        print("set to address to cache")

    state = address_info['address_components']['state']
    district = address_info['fields']['congressional_district']['district_number']

    return redirect(url_for('show_district_info', state=state, district=district))


@app.route('/<state>/<int:district>', methods=['GET'])
def show_district_info(state, district):
    cache_key = get_md5("REPS_%s_%s" % (state, district))
    reps_pickle = cache.get(cache_key)

    if reps_pickle:
        reps = pickle.loads(reps_pickle)
        print('pulled reps from cache')
    else:
        try:
            reps = get_district_data(app.config['PROPUBLICA_API_KEY'], state, district)
        except Exception:
            error_msg = "Senator/Rep. lookup on Propublica failed for that state/district combination"
            return render_template('pages/error.jinja2', error_msg=error_msg)
        cache.set(cache_key, pickle.dumps(reps), expire=3600)
        print("set reps to cache")

    return render_template('pages/index.jinja2', reps=reps)
