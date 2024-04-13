from transformers import BertTokenizer, BertModel

from pathlib import Path

import os

class BertModelLoader:
    def __init__(self, save_directory='./bert-base-chinese-local'):
        self.save_directory = save_directory

        # 获取当前Python文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前Python文件的父目录路径
        parent_directory = os.path.dirname(current_file_path)
        # 组合父目录路径和save_directory来构建完整的路径
        full_save_directory = os.path.join(parent_directory, save_directory)

        self.save_directory = full_save_directory
        self.model_path = Path(full_save_directory)
        self.tokenizer = None
        self.model = None

        # 检查本地是否存在模型文件夹
        if self.model_path.exists() and list(self.model_path.glob('*')):
            # 如果目录存在且非空，从本地加载模型和分词器
            print("从本地加载模型...")
            self.tokenizer = BertTokenizer.from_pretrained(self.save_directory)
            self.model = BertModel.from_pretrained(self.save_directory)
        else:
            # 如果目录不存在或为空，从Hugging Face模型仓库下载模型
            print("从Hugging Face下载模型...")
            # 模型标识符
            model_identifier = 'google-bert/bert-base-chinese'
            self.tokenizer = BertTokenizer.from_pretrained(model_identifier)
            self.model = BertModel.from_pretrained(model_identifier)

            # 保存模型和分词器到本地
            if not self.model_path.exists():
                self.model_path.mkdir(parents=True, exist_ok=True)
            print("保存模型到本地...")
            self.tokenizer.save_pretrained(self.save_directory)
            self.model.save_pretrained(self.save_directory)

    def get_tokenizer(self):
        return self.tokenizer
    
    def get_model(self):
        return self.model
    
    def test(self):
        # 测试：对文本进行编码
        encoded_input = self.tokenizer("你好，这里是测试函数，怎么样了，成功运行了？", return_tensors="pt")
        output = self.model(**encoded_input)
        
        # 获取输出向量的维度
        output_tensor = output.last_hidden_state
        print(output_tensor.size())

if __name__ == "__main__":
    bml = BertModelLoader()
    bml.test()