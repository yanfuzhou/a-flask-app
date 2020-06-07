from mvc.controller.api import api
from flask_restx import Resource
from mvc.modeller.model import ServiceRegister

ns = api.namespace('api', description='API')


@ns.route('/hello')
class HelloWorld(Resource):
    @api.response(201, 'API is running!')
    def get(self):
        return ServiceRegister().response
