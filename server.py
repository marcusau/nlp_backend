#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os ,platform,pathlib
sys.path.append(os.getcwd())

from typing import List,Dict,Union,Tuple
import multiprocessing
import re,json,pickle
import numpy as np

import pytime
from datetime import datetime
import time

import tools



from functions import fuzz as fuzz_func
from functions import ner as ner_func
from functions import seg as seg_func
from functions import w2v as w2v_func

#
# def ner_full_scan(raw_text:str):
#
#
#
#     ner_results={}
#     for ss_ner in tools.split_sentences_ner(raw_text):
#         ner_result=ner_func.NER_run(ss_ner)
#         ner_results.update(ner_result)
#
#     ner_results={k:v for k,v in ner_results.items() if not tools.str_isNumber(k) and not tools.str_isDate(k) and k not in stopwords_cache}
#
#     if ner_results:
#         for k,v in ner_results.items():
#                 ner_key=k + '\t\t\t\t' + v
#                 record={'word': k, 'label': v}
#                 if ner_key not in  name_entity_cache:#.get(ner_key,None) is None:
#                     #print(record)
#                     name_entity_cache[ner_key]=record
#                     vocab_query.insert_ner(word=record['word'],label=record['label'])
#                     pos=ner2pos_cache.get(record['label'],'x')
#                     seg_func.addword(word=record['word'],pos=pos)
#
#
#     clean_text=''.join(s_ner)
#
#     word_pos = {w: pos for w, pos in seg_func.posseg(clean_text) if w not in tools.punctuations.all and len( w) > 1 and w not in stopwords_cache and not tools.str_isDate(w) and not tools.str_isNumber(w)}
#
#     word_seg_ners = {}
#     for (w,pos) in word_pos.items():
#         if ner_results.get(w,None) is None :
#             nertype=pos2ner_cache.get(pos, None)
#             if nertype:
#                 word_seg_ners[w]=nertype
#
#     ner_results.update(word_seg_ners)
#
#     ner_results=dict(sorted(ner_results.items(), key=lambda item: len(item[0]),reverse=True))
#     return ner_results#ners
#
#
#
# # from vocab import update_cache
# # update_cache.get_nertypes()
# # update_cache.get_pos()
# # update_cache.get_ner()
# # update_cache.get_stopwords()
# # update_cache.get_stocknames()
# #
# # name_entity_cache=cache.vocabs['name_entity']
# # stopwords_cache=cache.vocabs['stopwords']
# # stocknames_cache=cache.vocabs['stocknames']
# # stockcodes_cache=cache.vocabs['stockcodes']
# #
# # ner2pos_cache=cache.vocabs['ner2pos']
# # pos2ner_cache=cache.vocabs['pos2ner']
#
#
#
#
# ###------------------------------------------------------------------------------------------------------------------------------------------
#
# def ner_full_scan(raw_text:str):
#
#     s_ner=tools.split_sentences_for_ner(raw_text)
#
#     ner_results={}
#     for ss_ner in s_ner:
#         ner_result=ner_func.NER_run(ss_ner)
#         ner_results.update(ner_result)
#
#     ner_results={k:v for k,v in ner_results.items() if not tools.str_isNumber(k) and not tools.str_isDate(k) and k not in stopwords_cache}
#
#     if ner_results:
#         for k,v in ner_results.items():
#                 ner_key=k + '\t\t\t\t' + v
#                 record={'word': k, 'label': v}
#                 if ner_key not in  name_entity_cache:#.get(ner_key,None) is None:
#                     #print(record)
#                     name_entity_cache[ner_key]=record
#                     vocab_query.insert_ner(word=record['word'],label=record['label'])
#                     pos=ner2pos_cache.get(record['label'],'x')
#                     seg_func.addword(word=record['word'],pos=pos)
#
#
#     clean_text=''.join(s_ner)
#
#     word_pos = {w: pos for w, pos in seg_func.posseg(clean_text) if w not in tools.punctuations.all and len( w) > 1 and w not in stopwords_cache and not tools.str_isDate(w) and not tools.str_isNumber(w)}
#
#     word_seg_ners = {}
#     for (w,pos) in word_pos.items():
#         if ner_results.get(w,None) is None :
#             nertype=pos2ner_cache.get(pos, None)
#             if nertype:
#                 word_seg_ners[w]=nertype
#
#     ner_results.update(word_seg_ners)
#
#     ner_results=dict(sorted(ner_results.items(), key=lambda item: len(item[0]),reverse=True))
#     return ner_results#ners
#
#
#
#
# ###----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#
# # (URL must match the one given to factory function above)
# app = Flask(__name__)
# app.config['JSON_AS_ASCII']= True
#
# @app.route('/app2app')
# def index():
#     return 'Jieba Segment API by Python.'
#
#
# @app.errorhandler(404)
# def not_found(error): # 当我们请求  # 2 id的资源时，可以获取，但是当我们请求#3的资源时返回了404错误。并且返回了一段奇怪的HTML错误，而不是我们期望的JSON，这是因为Flask产生了默认的404响应。客户端需要收到的都是JSON的响应，因此我们需要改进404错误处理：
#     return make_response(jsonify({'error': 'Not found'}), 404)
#
#
# @app.errorhandler(400)
# def para_error(error): # 数据错误
#     return make_response(jsonify({'error': 'Parameter Error'}), 400)
#
# @app.errorhandler(500)
# def para_error(error): # 数据错误
#     return make_response(jsonify({'error': 'internal Error'}), 500)
#
#
# ##---------------------------------------------------
# # 返回对象
# def result(code, msg, data):
#     resultDic = {}
#     resultDic['code'] = code
#     resultDic['msg'] = msg
#     resultDic['data'] = data
#     return resultDic
#
# ##------------jieba ---------------------------------------------------------------------------------------------------------
# #
# # @app.before_first_request
# # @app.route(NLP_Backend_Routes.init, methods=['POST', 'GET'])
# # def jiebaInit():
# #     app.logger.info('---------------------init------------------')
# #     app.logger.info(" start-time:   " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
# #
# #     jieba_func.jieba_init()
# #     ner_func.NER_service.initialize()
# #
# #     app.logger.info(" end-time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
# #     return "jiebaInit done"
#
# ###--------------------------------------------------Jieba------------------------------------------------------------------------------------------------------------------
#
# @app.route('/nlp_engine/jieba/cut', methods=['POST'])
# def jieba_cut():
#     content = request.data.strip()
#
#     if not content:
#         resultObj = result('11001', 'parament content cannot be empty', [])
#     elif content.strip() == '':
#         resultObj = result('11001', 'cannot empty text', [])
#     else:
#         resultList =[word for word in seg_func.cut(content)]
#         resultObj = result('10001', 'tokenize success', resultList)
#     return jsonify(resultObj)
#
#
#
# @app.route('/nlp_engine/jieba/posseg', methods=['POST'])
# def jieba_posseg():
#     content = request.data.strip()
#
#     if not content:
#         resultObj = result('11001', 'parament content cannot be empty', [])
#     elif content.strip() == '':
#         resultObj = result('11001', 'cannot empty text', [])
#     else:
#         resultList =[(word,flag)  for (word,flag) in seg_func.posseg(content)]
#         resultObj = result('10001', 'tokenize success', resultList)
#     return jsonify(resultObj)
#
#
# @app.route('/nlp_engine/jieba/cut_for_search', methods=['POST'])
# def jieba_cut_for_search():
#     content = request.data.strip()
#     print(f'receive content : {content.decode("utf-8").strip()}')
#     if not content:
#         resultObj = result('11001', 'parament content cannot be empty', [])
#     elif content.strip() == '':
#         resultObj = result('11001', 'cannot empty text', [])
#     else:
#         resultList =[word for word in seg_func.cut_for_search(content)]
#         resultObj = result('10001', 'tokenize success', resultList)
#     return jsonify(resultObj)
#
#
# @app.route('/nlp_engine/jieba/addwords', methods=['POST', 'GET'])
# def jieba_addword():
#     word = request.form.get('word', '')
#     pos = request.form.get('pos', '')
#     seg_func.addword(word,pos)
#
# ###--------------------------------------------------ner -----------------------------------------------------------------------------------------------------------------
#
# @app.route('/nlp_engine/ner/simple_scan', methods=['POST','GET'])
# def ner_predict():
#     text = request.data.strip()
#     NER_results = ner_func.NER_run(text.decode("utf-8").strip())
#     return jsonify({'data':NER_results})
#
# @app.route('/nlp_engine/ner/full_scan', methods=['POST','GET'])
# def keywords_extract():
#     content = request.data.strip()
#     if not content:
#         return jsonify({'data':None})
#     else:
#         keywords=ner_full_scan(content.decode("utf-8").strip())
#         return jsonify({'data':keywords})
#
#
# ###--------------------------------------------------fuzz --------------------
#
#
# @app.route('/nlp_engine/fuzz/word2word_sim', methods=['POST','GET'])
# def fuzz_word2word_sim():
#     data=request.json
#     query_word = data['query_word']
#     compare_word = data['compare_word']
#
#     if not data or len(query_word)==0 or len(compare_word)==0:
#         return None
#     else:
#         results=fuzz_func.word2word_sim(word_A=query_word,word_B=compare_word)
#         return jsonify(results)
#
# @app.route('/nlp_engine/fuzz/word2words_sim', methods=['POST','GET'])
# def fuzz_word2words_sim():
#     data=request.json
#     word = data['word']
#     words = data['words']
#     topn = int(data['topn'])
#
#     if not data or len(word)==0 or len(words)==0:
#         return None
#     else:
#         results=fuzz_func.word2words_sim(word=word,words=words,TopN=topn)
#         results={'data':results}
#         return jsonify(results)
#
#
# @app.route('/nlp_engine/fuzz/check_dupword', methods=['POST','GET'])
# def fuzz_check_dupwords():
#     data=request.json
#     word = data['word']  #word:str, words:Union[List[str],str], threshold:float=0.6)
#     words = data['words']
#     threshold = data['threshold']
#
#     if not data or len(word)==0 or len(words)==0:
#         return None
#     else:
#         results=fuzz_func.check_dupword(word=word,words=words,threshold=threshold)
#         return jsonify(results)
#
#
# @app.route('/nlp_engine/fuzz/rmdupwords', methods=['POST','GET'])
# def fuzz_remove_dup_words():
#     data=request.json
#     words = data['data']
#     threshold = data['threshold']
#
#     if not data or len(words)==0:
#         return None
#     else:
#         results=fuzz_func.dedup_words(words, threshold= threshold, )
#         #DedupWord_func = fuzz_func.Dedup_Words if fuzz_method else word2vec_func.Dedup_Words
#         #results= DedupWord_func(words=word_dict, threshold=threshold )
#         if len(results)==0:
#             return None
#         else:
#             return jsonify(results)
#
#
#
# ####--------------------------word2vec -------------------
#
# @app.route('/nlp_engine/word2vec/vectorize', methods=['POST','GET'])
# def w2v_vector_convert():
#
#     data = request.json
#     words = data['words']
#
#     if not words or len(words)==0:
#         return None
#     else:
#         vector=w2v_func.word2vec_convert(words)
#         data_return={'data':vector.tolist()}
#         return jsonify(data_return)
#
#
#
# @app.route('/nlp_engine/word2vec/word2words_sim', methods=['POST','GET'])
# def w2v_word2words_sim():
#     data = request.json
#     word = data['word']
#     words = data['words']
#
#     if not word or len(words)==0:
#         return None
#     else:
#         results=w2v_func.word2words_sim(query=word, target=words)
#         results=[float(i) for i in results]
#         return   jsonify({'data':results})
#
# @app.route('/nlp_engine/word2vec/word2words_mostsim', methods=['POST','GET'])
# def w2v_word2words_mostsim():
#
#     data = request.json
#     word = data['word']
#     words = data['words']
#
#     if not word or len(words)==0:
#         return None
#     else:
#         result=w2v_func.word2words_mostsim(query=word, target=words)
#
#         data_return={'data':result}
#         return jsonify(data_return)
#
#
#
# @app.route('/nlp_engine/word2vec/word_topn_sim', methods=['POST','GET'])
# def w2v_word_topn_sim():
#    # content = request.data.strip()
#     data = request.json
#     word= data['word']
#     topn= int(data['topn'])
#
#     if not word or topn==0:
#         return None
#     else:
#         result=w2v_func.word_topn_sim(word=word,TopN=topn)
#         data_return={'data':result}
#         return jsonify(data_return)
#
#
#
# @app.route('/nlp_engine/word2vec/v2v_sim', methods=['POST','GET'])
# def v2v_sim():
#     data = request.json
#     query = np.array(data['query'])
#     target = np.array(data['target'])
#
#     if query is None:
#         return 'query is None'
#     elif target is None:
#         return 'target is None'
#     else:
#         sim_score=w2v_func.v2v_sim(query,target)
#         #sim_score =word2vec_func.Vector_sim(query_vec=query,target_vec=target)
#         return jsonify({'sim_score':sim_score})
#
#
#
# @app.route('/nlp_engine/word2vec/check_dupwords', methods=['POST','GET'])
# def w2v_check_dupwords():
#     data=request.json
#     word = data['word']
#     words = data['words']
#     threshold = float(data['threshold'])
#
#     if not word or len(words)==0:
#         return None
#     else:
#         results=w2v_func.check_dupwords(word=word,words=words, threshold= threshold,)
#         results=1 if results else 0
#         return jsonify({'data':results})
#
#
#
# @app.route('/nlp_engine/word2vec/remove_dupwords', methods=['POST','GET'])
# def w2v_remove_dupwords():
#     data=request.json
#     words = data['words']
#     threshold = float(data['threshold'])
#
#     if not data or len(data)==0:
#         return None
#     else:
#         results=w2v_func.remove_dupwords(words=words, threshold= threshold,)
#         return jsonify([{'data':results}])
#
#
#
# ##-----------------------4.  Keyword Extraction Components   -------------------------------------------
#
# if __name__ == "__main__":
#     # print('---------------------init------------------')
#     # print("=========start-time:   " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
#     # jieba.set_dictionary(data_files.jieba.bigdict)
#     # jieba.load_userdict(data_files.jieba.userdict)
#     # time.sleep(8)
#     # NER_service.initialize()
#     # time.sleep(5)
#     #
#     # print(("=========end-time:   " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
#     app.run(host='127.0.0.1', port=5002,debug=False,use_reloader=False,threaded=True,)