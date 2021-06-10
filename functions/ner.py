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

from typing import Dict,Union,Optional,List

from datetime import datetime
from tqdm import tqdm
import time

import logging,re

import torch
import torch.nn as nn
import torch.functional as F
from pytorchcrf import CRF

import tools

from transformers import BertTokenizer, BertConfig, BertModel,BertForPreTraining
from Config.model_Config import Info as Model_Config
bert_model_path=Model_Config.transformers.bert_model


logger = logging.getLogger(__name__)

class BERT_BiLSTM_CRF(BertForPreTraining):

    def __init__(self, config, need_birnn=False, rnn_dim=128):
        super(BERT_BiLSTM_CRF, self).__init__(config)

        self.num_tags = config.num_labels
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        out_dim = config.hidden_size
        self.need_birnn = need_birnn

        # 如果为False，则不要BiLSTM层
        if need_birnn:
            self.birnn = nn.LSTM(config.hidden_size, rnn_dim, num_layers=1, bidirectional=True, batch_first=True)
            out_dim = rnn_dim * 2

        self.hidden2tag = nn.Linear(out_dim, config.num_labels)
        self.crf = CRF(config.num_labels, batch_first=True)

    def forward(self, input_ids, tags, token_type_ids=None, input_mask=None):
        emissions = self.tag_outputs(input_ids, token_type_ids, input_mask)
        loss = -1 * self.crf(emissions, tags, mask=input_mask.byte())

        return loss

    def tag_outputs(self, input_ids, token_type_ids=None, input_mask=None):

        outputs = self.bert(input_ids, token_type_ids=token_type_ids, attention_mask=input_mask)

        sequence_output = outputs[0]

        if self.need_birnn:
            sequence_output, _ = self.birnn(sequence_output)

        sequence_output = self.dropout(sequence_output)
        emissions = self.hidden2tag(sequence_output)

        return emissions

    def predict(self, input_ids, token_type_ids=None, input_mask=None):
        emissions = self.tag_outputs(input_ids, token_type_ids, input_mask)
        return self.crf.decode(emissions, input_mask.byte())



class NERServeHandler:
    def __init__(self):
        self.initialized = False

    def initialize(self, ):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_def_path = bert_model_path
        training_args_file = os.path.join(model_def_path, 'training_args.bin')

        if not os.path.exists(model_def_path) :
            logger.debug(f"{model_def_path} does not exist, please enter correct bert model path")
            print(f"{model_def_path} does not exist, please enter correct bert model path")
            self.initialized = False
            pass
        elif not os.path.isfile(training_args_file):
            logger.debug(f"{training_args_file} does not exist, please load training_args_file in bert model path")
            print(f"{training_args_file} does not exist, please load training_args_file in bert model path")
            self.initialized = False
        else:
            print('loading NER labels and arguments')
            self.training_args = torch.load(training_args_file)
            self.labels = list(self.training_args.label_list) if "<PAD>" in list(self.training_args.label_list) else list(self.training_args.label_list)+["<PAD>"]
            self.num_labels = len(self.labels)
            self.label2idx = self.training_args.label2id
            self.idx2label = self.training_args.id2label
            self.max_seq_length = self.training_args.max_seq_length

            print('loading BERT Config')
            logger.info('loading BERT Config')
            self.bert_config = BertConfig.from_pretrained(model_def_path, num_labels=self.num_labels, id2label=self.idx2label, label2id=self.label2idx, )

            print('loading BERT tokenizer')
            logger.info('loading BERT Config')
            self.bert_tokenizer= BertTokenizer.from_pretrained(model_def_path,  do_lower_case=self.training_args.do_lower_case,  use_fast=False,config=self.bert_config, )

            print('loading BERT Model')
            self.model = BERT_BiLSTM_CRF.from_pretrained(model_def_path,   config=self.bert_config,  need_birnn=self.training_args.need_birnn,   rnn_dim=self.training_args.rnn_dim,  )
            self.model.to(self.device)
            self.model.eval()
            print("Model successfully loaded.")
            logger.debug("BERT Model successfully loaded.")
            self.initialized = True

    def preprocess(self,  data:str):
        tokens = [w for word in list(data) for w in self.bert_tokenizer.tokenize(word)]

        if len(tokens) >= self.max_seq_length - 1:
            tokens = tokens[0:(self.max_seq_length - 2)]  # -2 的原因是因为序列需要加一个句首和句尾标志

        ntokens = ["[CLS]"] + tokens + ["[SEP]"]
        raw_tokens= ["[CLS]"] + list(data) + ["[SEP]"]

        input_ids = self.bert_tokenizer.convert_tokens_to_ids(ntokens)
        segment_ids = [0] * len(input_ids)
        input_mask = [1] * len(input_ids)

        while len(input_ids) < self.max_seq_length:
            input_ids.append(0)
            segment_ids.append(0)
            input_mask.append(0)

        input_ids = torch.tensor(input_ids, dtype=torch.long)
        segment_ids = torch.tensor(segment_ids, dtype=torch.long)
        input_mask = torch.tensor(input_mask, dtype=torch.long)

        input_ids = input_ids.unsqueeze(0)
        segment_ids = segment_ids.unsqueeze(0)
        input_mask = input_mask.unsqueeze(0)

        input_ids = input_ids#.to(self.device)
        segment_ids = segment_ids # .to(self.device)
        input_mask = input_mask  # .to(self.device)

        feature = {'input_ids': input_ids, 'token_type_ids': segment_ids, 'mask_ids': input_mask, 'ntokens': ntokens}
        return feature,raw_tokens


    def inference(self, inputs,ntokens):
        pred_labels = []
        with torch.no_grad():
            logits = self.model.predict(inputs['input_ids'].to(self.device), inputs['token_type_ids'].to(self.device), inputs['mask_ids'].to(self.device))
            # #             # logits = torch.argmax(F.log_softmax(logits, dim=2), dim=2)
            logits = logits.detach().cpu().numpy()
            for l in logits:
                for idx in l:

                   # print('idx:',idx,type(idx),len(idx),'id2label[idx]:',[self.id2label[i] for i in list(idx)])
                    #pred_labels.append(self.id2label[idx])
                    pred_labels=[self.idx2label[i] for i in list(idx)]
        #assert len(pred_labels) == len(inputs['ntokens'])
       # print(ntokens, pred_labels)
       # sentence_, spans = self.tokens_to_spans(inputs['ntokens'], pred_labels,  allow_multiword_spans=True)
        sentence_, spans = self.tokens_to_spans(ntokens, pred_labels, allow_multiword_spans=True)

        return [(re.sub(' ', '', sentence_[span[0]:span[1]]), span[2]) for span in spans]

    def postprocess(self, inputs):
        ner_raw_results = {word: ner_class for (word, ner_class) in inputs if  len(word) > 1}#ner_class not in ['J', 'UNIT', 'TIME', 'QUANTITY'] and
        return ner_raw_results


    def tokens_to_spans(self, tokens, tags, allow_multiword_spans=False):
        spans = []
        curr, start, end, ent_cls = 0, None, None, None
        sentence = " ".join(tokens)
        if allow_multiword_spans:

            for token, tag in zip(tokens, tags):
                try:
                    if tag == "O":
                        if ent_cls is not None:
                            spans.append((start, end, ent_cls))
                            start, end, ent_cls = None, None, None
                    elif tag.startswith("B-"):
                        ent_cls = tag.split("-")[1]
                        start = curr
                        end = curr + len(token)
                    else:  # I-xxx
                        try:
                            end += len(token) + 1
                        except:
                            end = 0
                            end += len(token) + 1
                    # advance curr
                    curr += len(token) + 1
                except Exception as e:
                    print('cannot process:', token, tag, 'reason', e)
            # handle remaining span
            if ent_cls is not None:
                spans.append((start, end, ent_cls))


        else:
            for token, tag in zip(tokens, tags):
                if tag.startswith("B-") or tag.startswith("I-"):
                    ent_cls = tag.split("-")[1]
                    start = curr
                    end = curr + len(token)
                    spans.append((start, end, ent_cls))
                curr += len(token) + 1

        return sentence, spans

    def predict(self,  data:str):
        features,ntokens=self.preprocess(data)
        infer_results=self.inference(features,ntokens)
        output=self.postprocess(infer_results)
        return output

NER_service = NERServeHandler()


def NER_handle(data):
    if not NER_service.initialized:
        print('initialize BERT Name Entity Recognition engine')
        NER_service.initialize()
        time.sleep(10)
        print(' Completed initial BERT Name Entity Recognition engine')

    if data is None:
        return None
    if NER_service.initialized:
        data = NER_service.predict(data)
    return data


def NER_run(text:str): #,verbose:bool=False
    clean_text=tools.Clean_rawtext_Func(text)
    clean_lines=tools.split_sentences_ner(clean_text)

    ner_results={word:nertype for line in clean_lines for word,nertype in NER_handle(line).items()}

    return ner_results

if __name__=='__main__':
    fire.Fire({'ner':NER_run})