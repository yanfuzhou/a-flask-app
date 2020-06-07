import os
from debug import log
from flask_restx import Api

api = Api(version="1.0", description=os.environ['API_NAME'])


@api.errorhandler
def default_error_handler(e):
    log.exception(e)
    return dict(error=e), 500
