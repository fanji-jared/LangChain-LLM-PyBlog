import random
import numpy as np
from pymilvus import DataType, FieldSchema, MilvusClient, CollectionSchema

class MilvusTool:
    def __init__(self, host='localhost', port='19530'):
        self.host = host
        self.port = port
        self.client = MilvusClient(uri=f"http://{ host }:{ port }")
        if self.client is None:
            print("连接服务器失败")
            return False
        else:
            print(f"成功连接到Milvus服务器 {self.host}:{self.port}")
            return True

    def create_collection(self, name, dim):
        """
        快速创建集合

        :param collection_name: 集合名称
        :param dim: 向量维度
        :return: Bool
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False
        
        if not self.client.has_collection(name):
            self.client.create_collection(
                collection_name = name,
                dimension = dim
            )
            print(f"集合[ {name} ]创建成功！")
        else:
            print(f"集合[ {name} ]已经存在！")
    
    def insert_vectors(self, name, vectors):
        """
        插入向量到指定的集合中

        参数:
            name (str): 集合名称
            vectors (list): 需要插入的数据 [{"id": 1, "vector": [0.3580376395471989, 0.9029438446296592]},{"id": 2, "vector": []}]
  
        返回:
            obj: 插入的向量的ID列表
            {
                "insert_count": 10,
                "ids": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            }
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False
        
        return self.client.insert( collection_name = name, data = vectors)
    
    def drop_collection(self, name):
        """
        删除集合

        :param collection_name: 集合名称
        :return: None
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False
        
        return self.client.drop_collection(collection_name = name)

    def delete_entity_by_id(self, name, id_list):
        """
        删除集合中 ID list 的实体

        :param name: 集合名称
        :param id_list: 要删除的实体的 ID list
        :return list: 删除的数量
        {
            "delete_count": 5
        }
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False

        return self.client.delete(
            collection_name = name,
            ids = id_list
        )
    
    def delete_entity_by_query(self, name, query_expr):
        """
        根据 过滤语句 删除 集合中满足条件的实体

        参数:
            name (str): 集合名称
            query_expr (str): 查询表达式，用于过滤要删除的实体

        返回:
            list 删除的数量
            {
                "delete_count": 5
            }
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False

        return self.client.delete(
            collection_name = name,
            filter = query_expr
        )

    def collection_exists(self, collection_name):
        """
        检查指定的集合是否存在

        参数:
            collection_name (str): 集合名称

        返回:
            bool: 如果集合存在则返回True，否则返回False
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False

        return self.client.has_collection(collection_name)
    
    def search_vectors(self, name, query_vectors, limit):
        """
        检查指定的集合是否存在

        参数:
            collection_name (str): 集合名称
            query_vectors (vector): 要查询的向量 query_vectors = [[0.041732933, -0.013061441, 0.009748648]]
            limit (int): 限制搜索结果数量
        返回:
            bool: 如果集合存在则返回: 包含三个字典的子列表的列表，表示返回的实体及其 ID 和距离
            [
                [
                    {
                        "id": 548,
                        "distance": 0.08589144051074982,
                        "entity": {}
                    },
                    {
                        "id": 736,
                        "distance": 0.07866684347391129,
                        "entity": {}
                    },
                    {
                        "id": 928,
                        "distance": 0.07650312781333923,
                        "entity": {}
                    }
                ]
            ]
            否则返回: False
        """
        if self.client is None:
            print("未连接到Milvus服务器")
            return False
        re = self.client.search(collection_name = name, data = query_vectors, limit = limit,)
        return re

if __name__ == "__main__":
    """
    成功连接到Milvus服务器 localhost:19530
    集合[ articles ]已经存在！
    集合[ article_1_sentences ]已经存在！
    {'insert_count': 3, 'ids': [1, 2, 3]}
    True
    {'delete_count': 2}
    {'delete_count': 1}
    None
    False
    """
    MT = MilvusTool()
    
    # 创建集合
    MT.create_collection("articles", 768)  # 所有文章向量 集合
    MT.create_collection("article_1_sentences", 768) # id = 1 的文章的所有句子向量 集合

    # 插入向量
    vectors = [
        {"id": 1, "vector": [random.random() for _ in range(768)]},
        {"id": 2, "vector": [random.random() for _ in range(768)]},
        {"id": 3, "vector": [random.random() for _ in range(768)]}
    ]
    re = MT.insert_vectors("articles", vectors)
    print(re)

    # 检查集合是否存在
    print(MT.collection_exists("article_1_sentences"))

    # 删除指定ID的实体
    print(MT.delete_entity_by_id("articles", [1, 2]))

    # 删除满足条件的实体（这里假设使用一个简单的条件）
    query_expr = "id > 2"
    print(MT.delete_entity_by_query("articles", query_expr))

    # 删除集合
    print(MT.drop_collection("article_1_sentences"))

    # 检查集合是否存在
    print(MT.collection_exists("article_1_sentences"))

    # 向量相似度比较
    print(MT.search_vectors("articles", [random.random() for _ in range(768)], 3))