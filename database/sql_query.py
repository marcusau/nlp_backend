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


from typing import Union,List,Dict,Optional,Tuple

from tqdm import tqdm
from datetime import datetime
import time

from Config.SQL_Config import Info as SQL_config

import fire

import pymysql
from database.sql_db import SQL_connection,schema,tables
import tools

Schema=SQL_config.nlp_engine.schema
Tables=SQL_config.nlp_engine.tables

###-----------------------------------------------------------------------------------------------------------------------------------------------------------
def get_nertype(label:Union[str,List]=None):
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        if not label:
            select_query = f"""   SELECT *  FROM {Schema}.{Tables.util.NameEntity_type}"""
        else:
            label=",".join(["'"+l+"'" for l in label]) if isinstance(label,list) else "'"+label+"'"
            select_query = f"""   SELECT *  FROM {Schema}.{Tables.util.NameEntity_type} where label in ({label})"""

        cursor.execute(select_query )
        rows={i['label']:i for i in cursor.fetchall()}
        SQL_connection.close()
        return rows


def insert_nertype(label:str,pos:str,desc:str,example:str,remark:Optional[str]):
    remark = "" if not remark else remark
    data=[label,pos,desc,example,remark,datetime.now()]

    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        insert_query = f""" insert into  {Schema}.{Tables.util.NameEntity_type}  (label,pos,desc.example,remark,update_time) values (%s,%s,%s,%s,%s,%s)  ON DUPLICATE KEY UPDATE update_time=values(update_time); """
        cursor.execute(insert_query,data )
###--------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_postype(limit:Optional[int]=None,pos:Optional[Union[str,List]]=None):
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        select_query = f"""   SELECT pos,nertype  FROM {Schema}.{Tables.util.pos} """

        if pos:
            pos=",".join(["'"+l+"'" for l in pos]) if isinstance(pos,list) else "'"+pos+"'"
            select_query = select_query+ f""" where pos in ({pos})"""

        if limit:
            select_query = select_query+ f"""  limit {limit}"""
        cursor.execute(select_query )
        rows={i['pos']:i['nertype'] for i in cursor.fetchall()}
        SQL_connection.close()
        return rows


def insert_postype(pos:str,nertype:str):
    data=[pos,nertype,datetime.now()]
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        insert_query = f""" insert into {Schema}.{Tables.util.pos}   (pos,nertype,update_time) values (%s,%s,%s)  ON DUPLICATE KEY UPDATE update_time=values(update_time); """
        cursor.execute(insert_query,data )
###--------------------------------------------------------------------------------------------------------------------------------------------------------------


def get_stopwords(limit:int=None):
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)

        select_query = f"""   SELECT word  FROM {Schema}.{Tables.vocab.stopwords}"""
        if limit:
            select_query=select_query+f""" limit {int(limit)} """
        cursor.execute(select_query )
        rows=[r['word'] for r in cursor.fetchall()]
        SQL_connection.close()
        return rows


def insert_stopwords(words:str):
    words=[(w,datetime.now() ) for w in words.split(",") ]
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        insert_query = f""" insert into  {Schema}.{Tables.vocab.stopwords}  (word,update_time) values (%s,%s)  ON DUPLICATE KEY UPDATE update_time=values(update_time); """
        cursor.executemany(insert_query,words )

###-------------------------------------------------------------------------------------------------------------------------------------------------


def get_stocknames_bylimit(limit:Optional[int]=None,market:Optional[Union[str,List]]=None):
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)

        select_query = f"""   SELECT *  FROM {Schema}.{Tables.vocab.stocknames}"""

        if market :
            market=",".join(["'"+ma+"'" for ma in market]) if isinstance(market,list) else "'"+market+"'"
            select_query = select_query + f""" where market in ({market})"""

        if limit:
            select_query=select_query+f""" limit {int(limit)} """

        cursor.execute(select_query )
        rows={r['name'].strip():r['code']+'.'+r['market'] for r in cursor.fetchall()}
        SQL_connection.close()
        return rows


def get_stocknames_byname(name:str,market:Optional[Union[str,List]]=None,limit:int=None):
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)

        select_query = f"""   SELECT *  FROM {Schema}.{Tables.vocab.stocknames}"""

        select_query = select_query + f"""  where name LIKE '%{name}%'"""
        if market:
            market = ",".join(["'" + ma + "'" for ma in market]) if isinstance(market, list) else "'" + market + "'"
            select_query =select_query+f""" and market in ({market})  """

        if limit:
            select_query = select_query + f"""limit {limit}  """

        cursor.execute(select_query )
        rows={r['code']+'.'+r['market']:r['name'].strip() for r in cursor.fetchall()}
        SQL_connection.close()
        return rows


def insert_stocknames(stocknames:List[Dict]):
    data=[]
    for s in stocknames:
        code,market,name=str(s['code']), s['market'], s['name']
        alias=s.get('alias') if s.get('alias') else ''
        update_time=datetime.now()
        row=(code,market,name,update_time)
        data.append(row)

    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        insert_query = f""" insert into  {Schema}.{Tables.vocab.stocknames}  (code,market, name,update_time) values (%s,%s,%s,%s)  ON DUPLICATE KEY UPDATE update_time=values(update_time); """
        cursor.executemany(insert_query,data)

###-------------------------------------------------------------------------------------------------------------------------------------------------


def get_ners(limit:Optional[int]=None,label:Optional[Union[str,List[str]]]=None,word:str=None):
   # sep='------------------------------------'
    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)

        select_query = f"""   SELECT word, GROUP_CONCAT(label SEPARATOR '|') as labels  FROM {Schema}.{Tables.vocab.NameEntites}   """

        if label:
            label__ = ",".join(["'" + l + "'" for l in label]) if isinstance(label, list) else "'" + label + "'"
            label_query_tail =f""" label in ({label__})  """

        if word:
            words_query_tail =f"""word like '%{word}%'  """


        if label and not word:
            select_query=select_query+' where '+label_query_tail


        elif word and not label:
            select_query=select_query+' where '+words_query_tail

        elif word and label:
            select_query=select_query+' where '+label_query_tail +' and '+words_query_tail

        select_query=select_query+f" group by word"

        if limit:
            select_query = select_query + f"  limit {limit}"

        cursor.execute(select_query )
        rows={r['word']:r['labels'].split("||") for r in cursor.fetchall()}
        SQL_connection.close()
        return rows

# def get_ner_byorder(limit:Optional[int]=100,label:Optional[Union[str,List[str]]]=None):
#     sep='------------------------------------'
#     with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
#         SQL_connection.ping(reconnect=True)
#
#         select_query = f"""   SELECT *  FROM {Schema}.{Tables.vocab.NameEntites}"""
#
#         if label:
#             label = ",".join(["'" + l + "'" for l in label]) if isinstance(label, list) else "'" + label + "'"
#             select_query =select_query+f""" WHERE label in ({label})  """
#
#         if limit:
#             select_query=select_query+f""" limit {int(limit)} """
#
#         cursor.execute(select_query )
#         rows={r['word']+sep+r['label']:r for r in cursor.fetchall()}
#         SQL_connection.close()
#         return rows

#
# def get_ner_byword(word:str,label:Optional[Union[str,list]]=None,limit:int=None): #,label:Optional[Union[str,List[str]]],
#     sep='------------------------------------'
#     with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
#         SQL_connection.ping(reconnect=True)
#
#
#         select_query = f"""   SELECT *  FROM {Schema}.{Tables.vocab.NameEntites} where word like '%{word}%' """
#         if label:
#             label = ",".join(["'" + l + "'" for l in label]) if isinstance(label, list) else "'" + label + "'"
#             select_query =select_query+f""" and label in ({label})  """
#
#         if limit:
#             select_query=select_query+f"""  limit {limit}  """
#         cursor.execute(select_query )
#         rows={r['word']+sep+r['label']:r for r in cursor.fetchall()}
#         SQL_connection.close()
#         return rows


def insert_ners(ners:Union[List[Dict],Dict]):

    ners=[{'word':word,'label':label} for word,label in ners.items()] if isinstance(ners,dict) else ners

    data=[(str(s['word']), str(s['label']),datetime.now()) for s in ners]

    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        insert_query = f""" insert into  {Schema}.{Tables.vocab.NameEntites}  (word,label,update_time) values (%s,%s,%s)  ON DUPLICATE KEY UPDATE update_time=values(update_time); """
        cursor.executemany(insert_query,data)


def update_ners(ners:Union[List[Dict],Dict]):

    ners=[dict] if isinstance(ners,dict) else ners

    data=[]
    for s in ners:
        word,label=str(s['word']), str(s['label'])
        update_time=datetime.now()
        row=(word,label,update_time)
        data.append(row)

    with SQL_connection.cursor(pymysql.cursors.DictCursor) as cursor:
        SQL_connection.ping(reconnect=True)
        update_query = f""" upate  {Schema}.{Tables.vocab.NameEntites}  set label=%s, update_time=%s where word=%s; """
        cursor.executemany(update_query,data)


###-------------------------------------------------------------------------------------------------------------------------------------------------

if __name__=='__main__':
    fire.Fire({ 'nertype': get_nertype, 'insert_nertype': insert_nertype,
                'stopwords': get_stopwords, 'insert_stopwords': insert_stopwords,
                'pos':get_postype,'insert_pos':insert_postype,
                'stockname': get_stocknames_bylimit,'stocknames_byname':get_stocknames_byname,'insert_stocknames': insert_stocknames,
                'insert_ner': insert_ners,'ners':get_ners,  })#'ner_limit':get_ner_byorder,'ners':get_ner_byword,
    # ner=open('ner.txt','w',encoding='utf-8')
    # for word, nertypes in get_ners().items():
    #     ner.write(word+'\t'+'\t'.join(nertypes)+'\n')
    # ner.close()