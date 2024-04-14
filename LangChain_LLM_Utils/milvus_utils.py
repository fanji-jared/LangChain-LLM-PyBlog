from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

class MilvusTool:
    def __init__(self, host='localhost', port='19530'):
        self.host = host
        self.port = port
        self.client = None
        self.connect()

    def connect(self):
        """
        初始化连接Milvus
        """
        try:
            self.client = connections.connect(self.host, self.port)
            print(f"连接到Milvus服务器 {self.host}:{self.port}")
        except Exception as e:
            print(f"连接服务器失败。处理步骤: {e}")

    def create_collection(self, collection_name, fields):
        """
        创建集合

        :param collection_name: 集合名称
        :param fields: 字段列表，例如：[FieldSchema(name="field1", dtype=DataType.FLOAT_VECTOR, is_primary=True, dim=128)]
        :return: None
        """
        if self.client is None:
            print("Not connected to Milvus server. Please call `connect` first.")
            return

        if not self.client.has_collection(collection_name):
            schema = CollectionSchema(fields=fields)
            self.client.create_collection(collection_name, schema)
            print(f"集合[ {collection_name} ]创建成功！")
        else:
            print(f"集合[ {collection_name} ]已经存在！")
    
    def insert_vectors(self, collection_name, vectors):
        """
        批量插入向量到指定的集合中

        参数:
            collection_name (str): 集合名称
            vectors (np.ndarray): 形状为 (n, dim) 的NumPy数组，其中n是向量数量，dim是向量维度
  
        返回:
            list: 插入的向量的ID列表
        """
        if self.client is None:
            raise ValueError("Not connected to Milvus server. Please call `connect` first.")
          
        # 使用client直接获取集合
        collection = self.client.get_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} does not exist.")
        
        ids = collection.insert(vectors)
        return list(ids) # 将返回的ID迭代器转换为列表
    
    def drop_collection(self, collection_name):
        """
        删除集合

        :param collection_name: 集合名称
        :return: None
        """
        if self.client is None:
            print("Not connected to Milvus server. Please call `connect` first.")
            return

        if self.client.has_collection(collection_name):
            self.client.drop_collection(collection_name)
            print(f"Collection {collection_name} dropped successfully.")
        else:
            print(f"Collection {collection_name} does not exist.")

    def delete_entity_by_id(self, collection_name, entity_id):
        """
        删除集合中指定ID的实体

        :param collection_name: 集合名称
        :param entity_id: 要删除的实体的ID
        :return: 删除结果
        """
        if self.client is None:
            print("Not connected to Milvus server. Please call `connect` first.")
            return False

        collection = self.client.get_collection(collection_name)
        if collection is None:
            print(f"Collection {collection_name} does not exist.")
            return False

        res = collection.delete_entity_by_id(entity_id)
        return res.status.OK
    
    def delete_entities_by_query(self, collection_name, query_expr):
        """
        根据查询语句删除集合中满足条件的实体

        参数:
            collection_name (str): 集合名称
            query_expr (str): 查询表达式，用于过滤要删除的实体

        返回:
            None
        """
        collection = self.client.get_collection(collection_name)
        if collection is None:
            raise ValueError(f"Collection {collection_name} does not exist.")

        # 执行查询并删除实体
        status, deleted_ids = collection.delete_entity_by_expression(query_expr)
        if not status.OK():
            raise RuntimeError(f"Failed to delete entities: {status.error_msg()}")

        print(f"Deleted {len(deleted_ids)} entities with IDs: {deleted_ids}")

    def collection_exists(self, collection_name):
        """
        检查指定的集合是否存在

        参数:
            collection_name (str): 集合名称

        返回:
            bool: 如果集合存在则返回True，否则返回False
        """
        return self.client.has_collection(collection_name)
    
