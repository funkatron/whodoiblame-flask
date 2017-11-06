from flask import Flask
from .geocodio import get_address_data
from .propublica import get_district_data

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# this relies on app so we have to import after creation
import whodoiblame.views