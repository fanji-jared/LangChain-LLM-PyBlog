from LangChain_LLM_Utils import bert_chinese_utils, lang_chain_utils, markdown_utils, milvus_utils

from LangChain_LLM_Utils.SharedProgress_Been import SharedProgress, VectorizationProcess

from datetime import datetime

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
    
    def article_vector(self, id, title, content):
        """
        异步向量化流程：
            1. 格式化文章 - Article Format
            2. 向量化全文 - Text Vec
            3. 向量化句子 - Sent Vec
            4. 存储全文向量 - Full Vec Store
            5. 存储句子向量 - Sent Vec Store

        Args:
            id (int): 文章 id - 用于 redis 记录进度
            title (str): 文章标题
            content (str): 文章正文

        Returns:
            None
        """
        # 获取 SharedProgress
        SP = SharedProgress()

        #################################### 1. 格式化文章 - Article Format       ####################################
        if self.MDT is None:
            self.MDT = markdown_utils.MDTool(title, content)
        sentences_list = self.MDT.get_sentences()

        # 设置状态和进度
        if len(sentences_list) > 0 :
            SP.set_progress(id, VectorizationProcess.ARTICLE_FORMAT.value, 100)
            Print(111111111111111111111111111111111111111111111111111111111111111111111111111111)
        else:
            SP.delete_progress(id)
            return


        #################################### 2. 向量化全文 - Text Vec             ####################################
        if self.BML is None:
            self.BML = bert_chinese_utils.BertModelTool()
        article_embedding_list = self.BML.get_article_embedding(sentences_list)

        # 设置状态和进度
        if article_embedding_list.size > 0 :
            SP.set_progress(id, VectorizationProcess.TEXT_VEC.value, 100)
            Print(222222222222222222222222222222222222222222222222222222222222222222222222222222)
        else:
            SP.delete_progress(id)
            return


        #################################### 3. 向量化句子 - Sent Vec             ####################################
        if self.BML is None:
            self.BML = bert_chinese_utils.BertModelTool()
        sentences_embeddings_list = self.BML.get_sentences_embeddings(id, sentences_list)

        # 设置状态和进度
        if len(sentences_embeddings_list) > 0 :
            SP.set_progress(id, VectorizationProcess.SENT_VEC.value, 100)
            Print(333333333333333333333333333333333333333333333333333333333333333333333333333333)
        else:
            SP.delete_progress(id)
            return

        #################################### 4. 存储全文向量 - Full Vec Store      ####################################
        # if self.MT is None:
        #     self.MT = milvus_utils.MilvusTool()

        # # 4.1 判断 articles 集合
        # re411 = True
        # if self.MT.collection_exists("articles") is False:
        #     # 4.1.1 创建集合
        #     re411 = self.MT.create_collection("articles", 768)
        # # 4.2 将 a 和 id 转换为vectors格式的列表
        # vectors = [
        #     {"id": id, "articles": article_embedding_list[0]}
        # ]
        # # 4.3 插入向量
        # re43 = self.MT.insert_vectors("articles", vectors)

        # # 设置状态和进度
        # SP.current_step = VectorizationProcess.FULL_VEC_STORE.value
        # SP.progress =  1.00 if re411 and re43 and sentences_embeddings_list else 0.00


        #################################### 5. 存储句子向量 - Sent Vec Store      ####################################