import os ,sys ,pathlib
import csv,tempfile
sys.path.append(os.getcwd())
from tqdm import tqdm
from typing import Union,List,Dict
from datetime import datetime,date
import fire
import shutil
import jieba_fast as jieba


from Config.model_Config import Info as  Model_Path_Config

Jieba_Config= Model_Path_Config.jieba
JiebaBigDict_filePath=pathlib.Path(Jieba_Config.bigdict)
JiebaUserDict_filePath=pathlib.Path(Jieba_Config.userdict)


def get_JiebaDict(filepath:Union[str,pathlib.Path]=JiebaBigDict_filePath):
    with open(filepath, mode='r', encoding='utf-8') as inp:
    #    output=[]
        for row in csv.reader(inp, delimiter=' '):
            word = str(row[0])
            freq = int(row[1])
            pos = str(row[2])  # if len_ is 3 else ''
            word_len=len(word)
            row={'word':word, 'freq':freq, 'pos':pos,'word_len':word_len}
            #output.append(row)
            yield row
    #return output

def get_jiebaDict_byWord(words:Union[str,List[str]],filepath:Union[str,pathlib.Path]=JiebaBigDict_filePath):
    jieba_dict={i['word']:i  for i in  get_JiebaDict(filepath=filepath)}
    words = [words] if isinstance(words, str) else words
    return [jieba_dict[word] for word in words]

##---------------------------------------------------------------------------------------------------------------------------------------------------------
def UpdateFreq_func(tempfile_path:Union[str,pathlib.Path],Words,WordLen:int,min_freq:int=5,incre_freq:int=2):
    if WordLen>1:
        jieba.set_dictionary(str(tempfile_path))

    for row in Words:
        word=row.get('word')
        row['freq'] = max(jieba.suggest_freq(word), min_freq*WordLen^incre_freq) if WordLen>1 else min_freq
        yield row

def append_tempDict(tempfile_path:Union[str,pathlib.Path],Words=None):
    if Words is not None:
        tempfile_path=pathlib.Path(tempfile_path)
        tempfile_path.touch(exist_ok=True)
        with open(str(tempfile_path), 'a', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=' ', lineterminator='\n', )
            writer.writerows([(r['word'], r['freq'], r['pos']) for r in Words])
    else:
        print(f'wordlist is None')


def run(filepath:Union[str,pathlib.Path]=JiebaBigDict_filePath, min_freq:int=5,incre_freq:int=2):
    filePath=pathlib.Path(filepath) #f isinstance(filepath,str) else filepath
    backup_folder=pathlib.Path(Jieba_Config.backup_folder)
    date_str=date.today().strftime('%Y%m%d')
    backup_file_Path=backup_folder/(pathlib.Path(filepath).stem+f'_{date_str}.txt')
    print(f'back_up file :{backup_file_Path}')

    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path= pathlib.Path(temp_dir.name)
    tempfile_path=temp_dir_path/filePath.name
    tempfile_path.touch(exist_ok=True)
    #
    Jieba_WordList=[]
    for i in get_JiebaDict(filePath):
        Jieba_WordList.append(i)

    Jieba_WordList= sorted(Jieba_WordList,key=lambda x: x['word_len'])

    WordLens=list(set([i['word_len'] for i in Jieba_WordList]))
    print(WordLens)

    for WordLen in tqdm(WordLens):

        ori_words=filter(lambda x:x['word_len']==WordLen,Jieba_WordList)
        update_words=UpdateFreq_func(tempfile_path=tempfile_path,
                                     Words=ori_words,
                                     WordLen=WordLen,
                                     min_freq=min_freq,
                                     incre_freq=incre_freq)

        append_tempDict(tempfile_path=tempfile_path,    Words=update_words)


    shutil.move(filePath,backup_file_Path)
    shutil.move(tempfile_path,filePath)
    temp_dir.cleanup()
    return ''

if __name__=="__main__":
    fire.Fire({"update_dict":run})

