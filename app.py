import os
from mvc.controller.api import api
from flask import Flask, Blueprint, send_from_directory
from mvc.controller.namespace import ns as api_namespace
from debug import log, SWAGGER_UI_DOC_EXPANSION, RESTX_VALIDATE, RESTX_MASK_SWAGGER, ERROR_404_HELP, FLASK_DEBUG


uri = 'api'
app = Flask(__name__)
log.info('>>>>> Starting development server at http://{}'.format('localhost:4000/' + uri + '/ <<<<<'))
app.config['SWAGGER_UI_DOC_EXPANSION'] = SWAGGER_UI_DOC_EXPANSION
app.config['RESTX_VALIDATE'] = RESTX_VALIDATE
app.config['RESTX_MASK_SWAGGER'] = RESTX_MASK_SWAGGER
app.config['ERROR_404_HELP'] = ERROR_404_HELP
control = Blueprint(uri, __name__, url_prefix='/' + uri)
api.init_app(control)
api.add_namespace(api_namespace)
app.register_blueprint(control)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=FLASK_DEBUG)
