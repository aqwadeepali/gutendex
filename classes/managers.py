import collections
from engine import Engine
from data import DataManager
# from compression import CompressionManager

def register_managers(app, WSGI_PATH_PREFIX):
    return Managers(app, WSGI_PATH_PREFIX)

class Managers:
    def __init__(self, app, WSGI_PATH_PREFIX):
        self.app = app
        # self.cmpmgr = CompressionManager( app, compresslevel=9 )
        self.DataManager = DataManager(app)
        self.Engine = Engine({"postgres_db": self.DataManager.get_pg_connection_string()})
        mngrs = {
            # 'Compression': self.cmpmgr,
            'DataManager': self.DataManager,
            'Engine': self.Engine
        }
        self.app.config.setdefault('Managers', mngrs)
        self.app.config['Managers'] = mngrs
        print('             Registered Application Managers')
        print('------------------------------------------------------------------')


    def convert(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data