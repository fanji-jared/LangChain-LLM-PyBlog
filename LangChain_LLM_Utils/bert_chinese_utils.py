from transformers import BertTokenizer, BertModel

from pathlib import Path

import os

class BertModelTool:
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
    
    def get_title_embeddings(self, text):
        # 将文本标记化，并添加[CLS]和[SEP]标记
        inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=True)  
        
        # 使用BERT模型生成输出
        outputs = self.model(**inputs)
        
        # 获取最后一个隐藏状态（即向量化表示）
        last_hidden_states = outputs.last_hidden_state
        
        # 由于[CLS]标记通常位于第一个位置，我们可以直接提取它
        """
        batch_size 批量大小：每次迭代训练时所使用的样本数量
        sequence_length 序列长度：一个序列中元素的数量
        hidden_size 隐藏层的维度大小
        """
        cls_vector = last_hidden_states[0, 0, :]  # [batch_size, sequence_length, hidden_size]
        
        return cls_vector
    
    def get_sentence_embeddings(self, text):
        # 将文本标记化，并添加[CLS]和[SEP]标记（如果必要）
        inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512)
        
        # 使用BERT模型生成输出
        outputs = self.model(**inputs)

        # 获取最后一个隐藏状态（即向量化表示）
        last_hidden_states = outputs.last_hidden_state

        # 提取句子分隔符[SEP]的位置
        sep_indices = (inputs["input_ids"] == self.tokenizer.sep_token_id).nonzero().squeeze(-1)

        # 初始化句子嵌入列表
        sentence_embeddings = []

        # 遍历每个[SEP]标记，获取其对应的句子嵌入
        for i in range(1, len(sep_indices)):  # 跳过第一个[CLS]标记
            start_idx = sep_indices[i-1] + 1  # 上一个[SEP]之后的位置
            end_idx = sep_indices[i]  # 当前[SEP]的位置

            # 计算句子内token向量的平均值作为句子嵌入
            sentence_embedding = last_hidden_states[:, start_idx:end_idx, :].mean(dim=1)
            sentence_embeddings.append(sentence_embedding)

        # 如果文本以[SEP]结束，则添加最后一个句子的嵌入（如果有的话）
        if end_idx < last_hidden_states.shape[1] - 1:
            last_sentence_embedding = last_hidden_states[:, end_idx+1:, :].mean(dim=1)
            sentence_embeddings.append(last_sentence_embedding)
            
        return sentence_embeddings
    
    def test(self):
        # 测试：对文本进行编码
        encoded_input = self.tokenizer("你好，这里是测试函数，怎么样了，成功运行了？", return_tensors="pt")
        output = self.model(**encoded_input)
        
        # 获取输出向量的维度
        output_tensor = output.last_hidden_state
        # print(output_tensor)
        print(output_tensor.size())

if __name__ == "__main__":
    bml = BertModelTool()
    bml.test()