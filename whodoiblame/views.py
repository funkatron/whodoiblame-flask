from flask import request, render_template, redirect, url_for
from .geocodio import get_address_data
from .propublica import get_district_data
from .cache import CacheClient

from whodoiblame import app


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.jinja2')


@app.route('/', methods=['POST'])
def get_results():
    address = request.form.get('address', None)

    cache = CacheClient(app.config)
    cache_key = "GEO_%s" % address
    address_info = cache.get(cache_key)

    if not address_info:
        try:
            address_info = get_address_data(app.config['GEOCODIO_API_KEY'], address)
        except Exception:
            error_msg = "We encountered a problem with that address. Try being more specific, and include a ZIP code"
            return render_template('pages/error.jinja2', error_msg=error_msg)
        cache.set(cache_key, address_info)

    state = address_info['address_components']['state']
    district = address_info['fields']['congressional_district']['district_number']

    return redirect(url_for('show_district_info', state=state, district=district))


@app.route('/<state>/<int:district>', methods=['GET'])
def show_district_info(state, district):
    cache = CacheClient(app.config)
    cache_key = "REPS_%s_%s" % (state, district)
    reps = cache.get(cache_key)

    if not reps:
        try:
            reps = get_district_data(app.config['PROPUBLICA_API_KEY'], state, district)
        except Exception:
            error_msg = "Senator/Rep. lookup on Propublica failed for that state/district combination"
            return render_template('pages/error.jinja2', error_msg=error_msg)
        cache.set(cache_key, reps)

    return render_template('pages/index.jinja2', reps=reps)
