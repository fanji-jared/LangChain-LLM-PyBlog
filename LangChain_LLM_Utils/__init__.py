from datetime import datetime
from LangChain_LLM_Utils import bert_chinese_utils, lang_chain_utils, markdown_utils, milvus_utils

import os
import tempfile

from enum import Enum  
  
class VectorizationProcess(Enum):
    ARTICLE_FORMAT = "ArticleFormat"
    TEXT_VEC = "TextVec"
    SENT_VEC = "SentVec"
    FULL_VEC_STORE = "FullVecStore"
    SENT_VEC_STORE = "SentVecStore"

# 测试方法 代替print
def Print(content, file_path = '/home/fanji/Desktop/blog_info.txt'):
    """
    将内容写入文件
    :param content: 要写入文件的内容
    :param file_path: 文件路径
    """
    # 获取当前时间并格式化为字符串  
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'a') as file:  # 'a' 模式表示追加写入
        file.write(f"{ current_time }: { str(content) } \n")

class Manger:
    def __init__(self):
        self.MT = None   # MilvusTool       - 存取管理 milvus 向量数据库
        self.MDT = None  # MDTool           - 处理 markdown 文章
        self.BML = None  # BertModelTool    - 向量化 文章 与 句子
        self.LCT = None  # LangChainTool    - 获得 LLM 回答

    # 测试方法 代替print
    def Print(content, file_path = '/home/fanji/Desktop/blog_info.txt'):
        """
        将内容写入文件
        :param content: 要写入文件的内容
        :param file_path: 文件路径
        """
        # 获取当前时间并格式化为字符串  
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, 'a') as file:  # 'a' 模式表示追加写入
            file.write(f"{ current_time }: { str(content) } \n")

    def getIDVectorize(self, id):
        """
        根据 id 在 milvus数据库 是否存在
        向量集合 命名规则 为 article_{id}_sentences
        """
        name = f'article_{id}_sentences'

        # 检查 self.MT 是否为 None，如果是则创建 MilvusTool 实例
        if self.MT is None:
            self.MT = milvus_utils.MilvusTool()
        # 调用即可
        return self.MT.collection_exists(name)
    
    def save_vectorization_status(self, current_step, completion_percentage, file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorization_status.txt")):
        """
        将向量化流程的状态和完成百分比写入文件，使用临时文件确保数据完整性

        :param current_step: 当前向量化流程的步骤
        :param completion_percentage: 完成进度 小数
        :param file_path: 目标文件路径
        """
        # 获取当前时间并格式化为字符串
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 准备要写入文件的内容
        content = f"{current_time}|{current_step}|{completion_percentage:.2f}"
        # 创建一个临时文件来写入内容
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content.encode())  # 写入内容到临时文件，注意encode为字节流
        # 获取临时文件的路径
        tmp_file_path = tmp_file.name
        # 使用原子操作替换原文件，确保数据一致性
        try:
            os.replace(tmp_file_path, file_path)  # 在Python 3.3及以上版本使用os.replace
        except AttributeError:  
            # 对于Python 3.2及以下版本，使用os.rename，但注意它可能不是原子操作
            os.rename(tmp_file_path, file_path)
        # 删除临时文件（如果delete=True，则不需要这一步，但在上面的代码中设置为了False
        os.remove(tmp_file_path)

    def article_vector(self, id, title, content):
        """
        向量化流程：
            1. 格式化文章 - Article Format
            2. 向量化全文 - Text Vec
            3. 向量化句子 - Sent Vec
            4. 存储全文向量 - Full Vec Store
            5. 存储句子向量 - Sent Vec Store

        Args:
            id (int): 文章 id
            title (str): 文章标题
            content (str): 文章正文

        Returns:
            None
        """
        # 1. 格式化文章 - Article Format
        if self.MDT is None:
            self.MDT = markdown_utils.MDTool(title, content)
        sentences_list = self.MDT.get_sentences()

        Print(111111111111111111111111111111111111111111111111111111111111111111111111111111)
        Print(sentences_list)

        if sentences_list:
            self.save_vectorization_status(VectorizationProcess.ARTICLE_FORMAT.value,1)
        else:
            self.save_vectorization_status(VectorizationProcess.ARTICLE_FORMAT.value,0)

        # 2. 向量化全文 - Text Vec
        if self.BML is None:
            self.BML = bert_chinese_utils.BertModelTool()
        article_embedding_list = self.BML.get_article_embedding(sentences_list)

        Print(222222222222222222222222222222222222222222222222222222222222222222222222222222)
        Print()

        if article_embedding_list:
            self.save_vectorization_status(VectorizationProcess.TEXT_VEC.value,1)
        else:
            self.save_vectorization_status(VectorizationProcess.TEXT_VEC.value,0)

        # 3. 向量化句子 - Sent Vec
        # if self.BML is None:
        #     self.BML = bert_chinese_utils.BertModelTool()
        # sentences_embeddings_list = self.BML.get_sentences_embeddings(sentences_list)

        # if sentences_embeddings_list:
        #     self.save_vectorization_status(VectorizationProcess.SENT_VEC.value,1)
        # else:
        #     self.save_vectorization_status(VectorizationProcess.SENT_VEC.value,0)

        # 4. 存储全文向量 - Full Vec Store
        if self.MT is None:
            self.MT = milvus_utils.MilvusTool()

        # 4.1 判断 articles 集合
        re411 = True
        if self.MT.collection_exists("articles") is False:
            # 4.1.1 创建集合
            re411 = self.MT.create_collection("articles", 768)
        # 4.2 将 a 和 id 转换为vectors格式的列表  
        vectors = [
            {"id": id, "articles": article_embedding_list[0]}
        ]
        # 4.3 插入向量
        # re43 = self.MT.insert_vectors("articles", vectors)

        # if re411 and re43 and sentences_embeddings_list:
        #     self.save_vectorization_status(VectorizationProcess.SENT_VEC.value,1)
        # else:
        #     self.save_vectorization_status(VectorizationProcess.SENT_VEC.value,0)

        # 5. 存储句子向量 - Sent Vec Store