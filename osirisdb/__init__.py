
from . import application
from . import controllers
from . import osiris
from .osiris.core import api

application.app.register_blueprint(api, url_prefix='/osiris/')
