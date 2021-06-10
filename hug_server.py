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


from typing import List,Dict,Union,Tuple
import multiprocessing
import re,json,pickle
import numpy as np

import pytime
from datetime import datetime
import time
from tqdm import tqdm

from cacheout import Cache,CacheManager

import hug
from falcon import HTTP_400

from database import sql_query

import tools
from functions import fuzz
from functions import ner
from functions import seg
from functions import w2v


from Config.API_Config import Info as API_config


cacheman = CacheManager({'stopwords': {'maxsize': 5000,'ttl':0},
                         'ner': {'maxsize': 500000, 'ttl': 0},
                         'pos2ner': {'maxsize': 30,'ttl':0},
                        'nertype': {'maxsize': 30, 'ttl': 0},
                         'stockname': {'maxsize': 15000, 'ttl': 0},
                         })

cacheman['stopwords'].set_many({sw.strip():0 for sw in tqdm(sql_query.get_stopwords(),desc='load stopwords to cache')})
cacheman['ner'].set_many({k:v for k,v in tqdm(sql_query.get_ners().items(),desc='load name entity to cache')})
cacheman['nertype'].set_many({k:v for k,v in tqdm(sql_query.get_nertype().items(),desc='load ner info to cache')})
cacheman['pos2ner'].set_many({k:v for k,v in tqdm(sql_query.get_postype().items(),desc='load pos infor to cache')})
cacheman['stockname'].set_many({k:v for k,v in tqdm(sql_query.get_stocknames_bylimit().items(),desc='load stockname to cache')})


def ner_full_scan(raw_text: str):

    ###  Scan Name Entity
    ner_bert_results= { word:nertag   for sentence_for_ner in tools.split_sentences_ner(raw_text) for word,nertag in ner.NER_run(sentence_for_ner).items() }
    ner_bert_results = {k: v for k, v in ner_bert_results.items() if  not tools.str_isNumber(k) and not tools.str_isDate(k) and not cacheman['stopwords'].has(k)}

    ### Scan OOVs
    if ner_bert_results:
        OOV ={word:nertag for word, nertag in ner_bert_results.items() if not cacheman['ner'].has(word) }
        if OOV:
            cacheman['ner'].set_many(OOV)
            sql_query.insert_ners(OOV)
            for word in OOV:
                seg.addword(word,cacheman['pos2ner'].get(OOV[word]))

    ### Scan jieba
    clean_text = tools.Clean_rawtext_Func(raw_text)
    clean_text = re.sub('\n','。',clean_text)
    word_seg=[w for w in seg.cut(clean_text) if  w not in tools.punctuations.all and len(w) > 1 and not  cacheman['stopwords'].has(w) and not tools.str_isDate(   w) and not tools.str_isNumber(w)]

    ner_full_results={}
    for w in word_seg:
        ner_bert_check=ner_bert_results.get(w,None)
        if ner_bert_check  :
            ner_tag=ner_bert_check
        else:
            cache_ner_check=cacheman['ner'].has(w)
            if cache_ner_check:
                ner_tag=cacheman['ner'].get(w)[0]
            else :
                jieba_flag=seg.pos_flag(w)
                pos_flag_check=cacheman['pos2ner'].get(jieba_flag,None)
                if pos_flag_check :
                    ner_tag =pos_flag_check
                else:
                    ner_tag=None
        ner_full_results[w]=ner_tag

    ner_full_results ={w:t for w,t in ner_full_results.items() if t is not None}
    ner_full_results = dict(sorted(ner_full_results.items(), key=lambda item: len(item[0]), reverse=True))
    return ner_full_results

###-----------------------------------------------------------------------------------------------------------------

@hug.startup()
def add_data(api):
    """Adds initial data to the api on startup"""
    print('hug server start up')
    ner.NER_service.initialize()


###-----------------------------------------------------------------------------------------------------------------
API_routes=API_config.routine

root=API_routes.root
ner_route=API_routes.ner
seg_route=API_routes.seg
fuzz_route=API_routes.fuzz
w2v_route=API_routes.w2v



@hug.post(root+seg_route.cut)
def cut(words:str):
    data =words if not words or len(words)<2 else seg.cut(words)
    return {'data':data}

@hug.post(root+seg_route.pseg)
def pseg(words:str):
    data =words if not words or len(words)<2 else seg.cut(words)
    data={d:seg.pos_flag(d) if seg.pos_flag(d) else 'x'  for d in data}
    return {'data':data}

@hug.post(root+seg_route.addword)
def addword(word:str,pos:str):
    seg.add(word=word,pos=pos)

###-----------------------------------------------------------------------------------------------------------------

@hug.post(root+ner_route.simple)
def ner_simple(text):
    NER_results = ner.NER_run(text)
    return {'data':NER_results}

@hug.post(root+ner_route.main)
def ner_run(text):
    NER_results = ner_full_scan(raw_text=text)
    return {'data':NER_results}

###-----------------------------------------------------------------------------------------------------------------

@hug.post(root+fuzz_route.word_sim)
def fuzz_wordsim(wordA,wordB):
    sim = fuzz.word2word_sim(wordA,wordB)
    return {'data':sim}

@hug.post(root+fuzz_route.words_sim)
def fuzz_words_im(word, words, TopN):
    return fuzz.word2words_sim(word, words, TopN)

@hug.post(root+fuzz_route.check_dupe)
def fuzz_check_dupword(word, words, threshold):
    return fuzz.check_dupword(word, words, threshold)

@hug.post(root+fuzz_route.dedupe)
def fuzz_dedupe(words, threshold):
    return fuzz.dedup_words(words, threshold)

###-----------------------------------------------------------------------------------------------------------------

@hug.post(root+w2v_route.word_topn)
def topN(word:str,TopN:int):
    return w2v.word_topn_sim(word, TopN)


@hug.post(root+w2v_route.v2v_sim)
def v2v_sim(query_vec:np.array, target_vec:np.array):
    return w2v.v2v_sim(query_vec, target_vec)

@hug.post(root+w2v_route.words_sim)
def w2v_words_sim(word:str, words):
    return w2v.word2words_sim(query=word, target=words)


@hug.post(root+w2v_route.word_mostsim)
def w2v_mostsim(word:str, words):
    return w2v.word2words_mostsim(query=word, target=words)

@hug.post(root+w2v_route.wordtovec)
def tovec(words):
    return w2v.word2vec_convert(words)

@hug.post(root+w2v_route.dedupe)
def w2v_dedupe(words, threshold:float=0.6):
    return w2v.remove_dupwords(words,threshold)

@hug.post(root+w2v_route.check_dupe)
def w2v_check_dupword(word:str, words, threshold:float=0.6):
    return w2v.check_dupwords(word,words,threshold)



if __name__ == "__main__":
   # func.interface.cli()
    #hug.API(__name__).cli()
  #  fire.Fire()
    hug.API(__name__).http.serve(port=int(API_config.port))