#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire,os,sys,pathlib,platform
sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

from typing import List,Dict,Union,Tuple,Optional

from datetime import datetime
from tqdm import tqdm
import time

import logging,re

from rapidfuzz import fuzz
from rapidfuzz import process as fuzzyprocess


def word2word_sim(word_A:str, word_B:str)->float:
    return fuzz.token_sort_ratio(word_A,word_B)


def word2words_sim(word:str, words:Union[List[str],str],TopN:Optional[Union[int,None]]=None):
    word_list=[words] if isinstance(words,str) else words
    limit=len(word_list) if TopN is None else TopN
    return {i[0]:i[1]/100 for i in fuzzyprocess.extract(word, word_list, scorer=fuzz.token_sort_ratio, limit=limit ) if i[1]<=100}


def check_dupword(word:str, words:Union[List[str],str], threshold:float=0.6)->bool:
    words = [words] if isinstance(words, str) else words
    if len(words) >= 1:
        sim_results =  word2words_sim(word, words)
        sim_check = max([c for w, c in sim_results.items()]) > threshold
        return sim_check
    else:
        return False

def dedup_words(words:Union[List, Dict], threshold:float=0.6)->Union[List, Dict, None]:
    if len(words) > 1:
        dedup_words=[]
        word_list_sorted_asc = sorted(list(words), key=len, reverse=False) if isinstance(words, list) else sorted(list(words.keys()), key=len, reverse=False)
        for word_index, word in enumerate(word_list_sorted_asc):
            compare_words = word_list_sorted_asc[word_index + 1:]
            dup_check = check_dupword(word, compare_words,threshold=threshold)
            if not dup_check:
                dedup_words.append(word)
        dedup_words = sorted(dedup_words, key=len, reverse=True)
        return dedup_words if isinstance(words, list) else {w: words[w] for w in dedup_words}
    else:
        print(f'word list cannot be empty')
        return []

if __name__ == '__main__':
    fire.Fire({'word_sim':word2word_sim,
               'words_sim': word2words_sim,
               'check_dup': check_dupword,
               'dedupe': dedup_words,  })


   #print(check_dupword(word='畢馬威會計師事務所', words= [普華永道中天會計師事務所, 羅兵咸永道會計師事務所, 畢馬威華振會計師事務所, 畢馬威會計師事務所, 特殊普通合夥, 股東周年大會, 國資委, 董事會, 退任], threshold= 0.6))
    # print(dedup_words(   words=['每股經調整盈利', '每股盈利預測', '收入增長放緩', '首季業績', '新冠肺炎病毒檢測', '首季盈利', 'BinaxNOW', 'Panbio', '製藥業務收入', '營養業務收入',  '醫療器械', '美國藥廠', '快速檢測', '雅培'], threshold=0.8))
    # print(dedup_words(
    #   words=['每股經調整盈利', '每股盈利預測', '收入增長放緩', '首季業績', '新冠肺炎病毒檢測', '首季盈利', 'BinaxNOW', 'Panbio', '製藥業務收入', '營養業務收入',
    #          '醫療器械', '美國藥廠', '快速檢測', '雅培'], threshold=0.7))
    # print(dedup_words( words= ['每股經調整盈利', '每股盈利預測', '收入增長放緩', '首季業績', '新冠肺炎病毒檢測', '首季盈利', 'BinaxNOW', 'Panbio', '製藥業務收入', '營養業務收入', '醫療器械', '美國藥廠', '快速檢測', '雅培'], threshold= 0.6))
    # print(dedup_words( words= ['每股經調整盈利', '每股盈利預測', '收入增長放緩', '首季業績', '新冠肺炎病毒檢測', '首季盈利', 'BinaxNOW', 'Panbio', '製藥業務收入', '營養業務收入', '醫療器械', '美國藥廠', '快速檢測', '雅培'], threshold= 0.5))
    # print(dedup_words(  words=['每股經調整盈利', '每股盈利預測', '收入增長放緩', '首季業績', '新冠肺炎病毒檢測', '首季盈利', 'BinaxNOW', 'Panbio', '製藥業務收入', '營養業務收入', '醫療器械',
    #        '美國藥廠', '快速檢測', '雅培'], threshold=0.45))