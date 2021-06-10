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
    class StocknamesClass:
        @dataclasses.dataclass
        class HkClass:
            Chi: str
            Eng: str
        
        @dataclasses.dataclass
        class ShanghaiClass:
            Chi: str
            Eng: str
        
        @dataclasses.dataclass
        class ShenzhenClass:
            Chi: str
            Eng: str
        
        HK: HkClass
        Shanghai: ShanghaiClass
        Shenzhen: ShenzhenClass
    
    stocknames: StocknamesClass
