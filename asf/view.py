import json
import logging

from . import app as app_module
from . import model


# @app_module.App.view(model=model.Root)
# def view_root(self, request):
#     request.include('asf')
#     return request.get_response(static.FileApp(
#         module_relative_path('index.html')
#     ))


@app_module.ResourceApp.json(model=model.Resource)
def view_json_resource(self, request):
    return self


@app_module.ResourceApp.json(model=model.DocumentCollection,
                             request_method='POST',
                             body_model=model.Document)
def create_document(self, request):
    log = logging.getLogger(__name__)
    resource = self.add(request.body_obj)

    def redis_publish(response):
        # After function which will be save the object file to
        # redis if post was successfull.
        log.debug('Publishing obj %r to redis', resource)
        data = {'data': resource.dump_json(request),
                'type': 'CREATE'}
        request.app.root.redis.publish(request.path, json.dumps(data))
    request.after(redis_publish)
    return request.view(resource)


# TODO move to path.

@app_module.ResourceApp.defer_links(model=model.Websocket)
def defer_websocket_links(app, obj):
    log = logging.getLogger(__name__)
    log.debug('defering obj %r in app %r.', obj, app)
    return app.child(app_module.WebsocketApp())


@app_module.RootApp.defer_links(model=model.SaladCollection)
def defer_salad_collection_links(app, obj):
    log = logging.getLogger(__name__)
    log.debug('defering obj %r in app %r.', obj, app)
    return app.child(app_module.SaladsApp(obj.parent))


@app_module.ResourceApp.dump_json(model=model.Resource)
def dump_json(self, request):
    return self.dump_json(request)


@app_module.SaladsApp.load_json()
def load_json_salad(json, request):
    return model.SaladDocument.load_json(json, request)


@app_module.IngredientsApp.load_json()
def load_json_ingredient(json, request):
    return model.IngredientDocument.load_json(json, request)
