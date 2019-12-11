import os, sys, flask
base_path = os.path.dirname(__file__)
class_path = os.path.join(base_path, "classes")
manager_path = os.path.join(base_path, "classes/managers")
model_path = os.path.join(base_path, "classes/models")
config_path = os.path.join(base_path, "config/")
temp_path = os.path.join(base_path, "temp/")

sys.path.insert(0, base_path)
sys.path.insert(1, class_path)
sys.path.insert(2, manager_path)
sys.path.insert(2, model_path)

WSGI_PATH_PREFIX = ''
SECRET_KEY = 'ABCD'

from flask import redirect, url_for
import managers as managers, services as services

class Config:
    def __init__(self, app, WSGI_PATH_PREFIX):
        self.app = app
        # register managers and then services
        print(' * WSGIPrefix set to %s'%WSGI_PATH_PREFIX)
        self.mgrs = managers.register_managers(app, WSGI_PATH_PREFIX)
        self.srvs = services.register_services(app, WSGI_PATH_PREFIX, SECRET_KEY)

    def reload(self):
        self.mgrs.reload()

# create application
application = flask.Flask(__name__)
application.secret_key = SECRET_KEY
application._static_folder = "dist"
cfg = None

@application.route(WSGI_PATH_PREFIX + '/')
def app_root():
    return redirect(url_for('app_page'))

@application.route(WSGI_PATH_PREFIX + '/gutenberg')
def app_page():
    return application.send_static_file('index.html')

def set_wsgi_prefix(prefix='/'):
    WSGI_PATH_PREFIX = prefix
    cfg = Config(application, WSGI_PATH_PREFIX)

if __name__ == '__main__':
    WSGI_PATH_PREFIX = '/api_gutenberg'
    cfg = Config(application, WSGI_PATH_PREFIX)
    dport = int(sys.argv[1]) if len(sys.argv) > 1 else 35050
    application.run(host='0.0.0.0',port=dport,debug=True,use_reloader=True,processes=1,static_files={'/':'dist'})
else:
    cfg = Config(application, WSGI_PATH_PREFIX)