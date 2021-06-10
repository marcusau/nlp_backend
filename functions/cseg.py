#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire,os,sys,pathlib
sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))
from typing import List,Dict,Union,Tuple

from datetime import datetime,date
from tqdm import tqdm
import time

import logging,re,json

from cppjieba_py import  Tokenizer
import tools
from Config.model_Config import Info as Model_Config

jieba_data_path=Model_Config.jieba

jieba_updatedict_path=pathlib.Path(jieba_data_path.update_folder)/(date.today().strftime('%Y%m%d')+'.txt')
jieba_updatedict_path.touch(exist_ok=True)


#userdict_path=str(pathlib.Path(r'/home/andrewc/marcus/nlp_engine_uat/userdict.txt'))
#DICT=r'/home/andrewc/marcus/nlp_engine_uat/userdict.txt'

print("creating jieba instance")
t1 = datetime.now()
jieba_instance = Tokenizer(jieba_data_path.bigdict)
t2 = datetime.now()
print("initialize costs:%s" % (t2 - t1))




def cut(text):
    text=tools.Clean_rawtext_Func(text)
    return jieba_instance.lcut(text,False, False)

def pos_flag(word:str):
    return jieba_instance.lookup_tag(word)

def find(word):
  return jieba_instance.find(str(word))
  

def add(word,pos=None):
    pos= 'x' if pos is None else pos
    jieba_freq=jieba_instance.suggest_freq(word)
    jieba_freq = max(6,jieba_freq)
    jieba_instance.add_word(word,jieba_freq, pos)

    print(f"OOV : {word},jieba freq: {jieba_freq}, pos : {pos} , task: jiebadict cache AddWord done")

    with open(str(jieba_updatedict_path), 'a', encoding='utf-8') as f:
        f.write(word + ' ' +str(jieba_freq)+ ' ' +pos  + '\n')


if __name__ == '__main__':
  fire.Fire()

