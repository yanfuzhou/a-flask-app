import logging.config
logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

# Flask settings
FLASK_DEBUG = False  # Do not use debug mode in production

# flask-restx settings
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTX_VALIDATE = True
RESTX_MASK_SWAGGER = False
ERROR_404_HELP = False
