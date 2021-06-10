#/usr/bin/env python
# -*- coding: utf-8 -*-
import os, pathlib, sys,fire,logging

sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))


from typing import Union,List,Dict

from tqdm import tqdm
from datetime import datetime
import time


from typing import List,Dict,Union,Tuple,Optional

import external_API
from database import sql_query

def update_stocknames(market:str='ALL'):
    stocknames=external_API.get_stocknames(market=market)

    sql_query.insert_stocknames(stocknames=stocknames)

def update_ners(limit:int=10):
    sql_records=sql_query.get_ners(limit=limit)


if __name__=='__main__':
    fire.Fire({'stocknames':update_stocknames})