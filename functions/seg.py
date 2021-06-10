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

from datetime import date

import jieba_fast as jieba
import jieba_fast.posseg as pseg
from Config.model_Config import Info as Model_Config

jieba_data_path=Model_Config.jieba

jieba_updatedict_path=pathlib.Path(jieba_data_path.update_folder)/(date.today().strftime('%Y%m%d')+'.txt')
jieba_updatedict_path.touch(exist_ok=True)

def cut(sent:str):
    return jieba.cut(sent,cut_all=False,HMM=False)

def posseg(sent:str):
    return pseg.cut(sent,HMM=False)

def cut_for_search(sent:str):
    return jieba.cut_for_search(sent,HMM=False)

def addword(word,pos):
    jieba_freq=jieba.suggest_freq(word)
    jieba_freq = max(6,jieba_freq)
    jieba.add_word(word,jieba_freq, pos)

    print(f"OOV : {word},jieba freq: {jieba_freq}, pos : {pos} , task: jiebadict cache AddWord done")

    with open(str(jieba_updatedict_path), 'a', encoding='utf-8') as f:
        f.write(word + ' ' +str(jieba_freq)+ ' ' +pos  + '\n')

if __name__=='__main__':
    fire.Fire({"seg":cut,"pseg":posseg,"cut_for_search":cut_for_search,"addword":addword})