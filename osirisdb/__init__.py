from sqlalchemy.exc import SAWarning
import warnings
warnings.filterwarnings("ignore", category=SAWarning)

from . import application
from . import controllers
from . import osiris
from .osiris.core import api

application.app.register_blueprint(api, url_prefix='/osiris/')

from .application import app