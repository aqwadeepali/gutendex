from sqlalchemy import create_engine

class EO_Engine_global():
    def __init__(self, connection):
        self.db_string = connection['postgres_db']
        self.engine = create_engine(self.db_string)
