import os, sys, datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
sys.path.append("../")
# from eo_auxy_funcs import *


class Engine:
    def __init__(self, pgres_url_dict):
        self.engine = create_engine(pgres_url_dict["postgres_db"], poolclass=NullPool)


if __name__ == "__main__":
    pgres_url = {"postgres_db":"postgresql://postgres:postgres@localhost:5432/gutenberg"}
    ie = Engine(pgres_url)

    # req_params = {'filters': {'sinac_name': 'RBS'}, 'tab': 'COVG', 'global_filters': {}}

