import dataclasses
import os,pathlib,sys
sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

import yaml2pyclass

class Config(yaml2pyclass.CodeGenerator):
    @dataclasses.dataclass
    class JiebaClass:
        bigdict: str
        backup_folder: str
        update_folder: str
    
    @dataclasses.dataclass
    class TransformersClass:
        bert_model: str
    
    @dataclasses.dataclass
    class WordvecClass:
        @dataclasses.dataclass
        class MaganituteClass:
            heavy: str
            light: str
        
        gensim: str
        maganitute: MaganituteClass
    
    jieba: JiebaClass
    transformers: TransformersClass
    wordvec: WordvecClass
