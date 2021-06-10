#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os ,platform,pathlib,fire
sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

from lru import lru_cache_function,LRUCacheDict
from typing import List,Dict,Union,Tuple
import multiprocessing
import re,json
import numpy as np
import operator
import datetime
import time

from sklearn.metrics.pairwise import cosine_similarity
from pymagnitudelight import Magnitude, FeaturizerMagnitude, MagnitudeUtils
from gensim import matutils

from Config.model_Config import Info as Model_Path_config

pymaganitute_config=Model_Path_config.wordvec.maganitute

d = LRUCacheDict(max_size=3, expiration=3, thread_clear=True,thread_clear_min_check=60)

@lru_cache_function(max_size=30000, expiration=60*2)
def get_Magnitude_Vectors():
    Magnitude_Vectors = Magnitude(pymaganitute_config.light, eager=True, case_insensitive=False,  batch_size=500000, supress_warnings=True, normalized=True,  language=None)  # -1 supress_warnings=True,language=None, lazy_loading=20,        data_files.word2vec.magnitude_heavy_model  magnitude_life_model
    return Magnitude_Vectors


mag_vectors = get_Magnitude_Vectors()


def v2v_sim(query_vec:np.array, target_vec:np.array)->float:
    cos_sim = cosine_similarity([query_vec], [target_vec])[0][0]
    return cos_sim

def word2words_sim(query:str, target:Union[str,List]):
   d= dict(zip(target, mag_vectors.similarity(query, target)))
   return dict( sorted(d.items(), key=operator.itemgetter(1),reverse=True))
    #return sim_score



def word2words_mostsim(query:str, target:List[str]):
   # print(f'inside apps, query: {query}, target: {target}')
    return  mag_vectors.most_similar_to_given(query, target)

def word_topn_sim(word:str,TopN:int=10,):
    return [w[0] for w in  mag_vectors.most_similar(mag_vectors.query(word), topn=TopN)]
    #return sim_words

def word2vec_convert(words:Union[List,str])->np.array:
    return mag_vectors.query(words)
    #Magnitude_Vectors.close()


###------------------------------------------------------------------------------------------------------------------------------------------
def check_dupwords(word:str, words:Union[List,str], threshold:float=0.6)->bool:
    if len(words) >= 1:
        sim_check =  max(word2words_sim(word, words).values()) > threshold
        return sim_check
    else:
        return False


def remove_dupwords(words:Union[List, Dict], threshold:float=0.6)->Union[List, Dict, None]:
    if len(words) > 1:
        dedup_words=[]
        word_list_sorted_asc = sorted(list(words), key=len, reverse=False) if isinstance(words, list) else sorted(list(words.keys()), key=len, reverse=False)

        for word_index, word in enumerate(word_list_sorted_asc):
            compare_words = word_list_sorted_asc[word_index + 1:]
            dup_check = check_dupwords(word=str(word), words=compare_words,threshold=threshold)
            if not dup_check:
                dedup_words.append(word)
        dedup_words = sorted(dedup_words, key=len, reverse=True)
        return dedup_words if isinstance(words, list) else {w: words[w] for w in dedup_words}
    else:
        #print(f'word list cannot be empty')
        return []


# threshold=0.6
# query_word='微信'
# compare_words=['微信小程序', '小程序', '淘寶', '監管', '讓步', '微信', '簽署網上銀行帳戶開通協議', '中國科技新聞網', 'Taob', '商品銷售', '商業環境', '支付通道', '管理服務', '反壟斷', '消費者']

if __name__=='__main__':
   # fire.Fire({"dedupe":remove_dupwords,"checkdup":check_dupwords,"w2v":word2vec_convert,"vecsim":v2v_sim,"wordsim":word2words_sim,"words_sim":word2words_sim,"topn":word_topn_sim})
    print(remove_dupwords(words=['微信小程序', '小程序', '淘寶', '監管', '讓步', '微信', '簽署網上銀行帳戶開通協議', '中國科技新聞網', 'Taob', '商品銷售', '商業環境', '支付通道', '管理服務', '反壟斷', '消費者'],threshold=0.6))