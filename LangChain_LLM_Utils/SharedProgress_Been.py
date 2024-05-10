from enum import Enum
import json
import os

import redis

from my_site import settings
  
class VectorizationProcess(Enum):
    '''
    流程化状态枚举类
    '''
    ARTICLE_FORMAT = "ArticleFormat"
    TEXT_VEC = "TextVec"
    SENT_VEC = "SentVec"
    FULL_VEC_STORE = "FullVecStore"
    SENT_VEC_STORE = "SentVecStore"

class SharedProgress:
    def __init__(self, prefix='vectorization_progress:'):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        # REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
        # REDIS_PORT = os.getenv('REDIS_PORT', '6379')
        # REDIS_DB = 0
        # REDIS_PASSWORD = None  # 如果你的Redis服务器没有密码，则留空

        # self.redis_client = redis.Redis(
        #     host=REDIS_HOST,
        #     port=REDIS_PORT,
        #     db=REDIS_DB,
        #     password=REDIS_PASSWORD,
        #     decode_responses=True
        # )
        self.prefix = prefix

    def set_progress(self, article_id, step, progress, expire_seconds=10 * 60):
        """
        设置进度并可选地设置过期时间
        
        :param article_id: 文章ID
        :param process: 流程化状态枚举值
        :param progress: 进度值
        :param expire_seconds: 过期时间（秒），如果为None则不设置过期时间
        """
        key = self.prefix + article_id
        progress_data = {
            'step': step,
            'progress': progress
        }
        # 使用 set 保证一个 key 只有一个记录
        self.redis_client.set(key, json.dumps(progress_data), ex=expire_seconds)

    def get_progress(self, article_id):
        """获取进度信息"""
        progress_key = self.prefix + article_id
        progress_json = self.redis_client.get(progress_key)
        if progress_json:
            progress_data = json.loads(progress_json)
            return progress_data['step'], progress_data['progress']
        else:
            # 如果没有找到进度记录，返回None, None
            return None, None
  
    def delete_progress(self, article_id):
        """删除特定id的进度记录"""
        progress_key = self.prefix + article_id
        self.redis_client.delete(progress_key)

    def has_progress(self, article_id):
        """查询是否存在特定id的进度记录"""
        progress_key = self.prefix + article_id
        return self.redis_client.exists(progress_key)

if __name__ == "__main__":
    progress_manager = SharedProgress()

    # 测试set_progress和get_progress
    article_id = 'test_article_1'
    progress_manager.set_progress(article_id, VectorizationProcess.ARTICLE_FORMAT.value, 50)
    step, progress = progress_manager.get_progress(article_id)
    print(f"Step: {step}, Progress: {progress}")  # 应该输出: Step: ArticleFormat, Progress: 50

    # 测试delete_progress和has_progress
    progress_manager.delete_progress(article_id)
    exists = progress_manager.has_progress(article_id)
    print(f"Progress exists: {exists}")  # 应该输出: Progress exists: 0

    # 再设置一次进度并检查是否存在
    progress_manager.set_progress(article_id, VectorizationProcess.TEXT_VEC.value, 75)
    exists = progress_manager.has_progress(article_id)
    print(f"Progress exists: {exists}")  # 应该输出: Progress exists: 1

    # 清理Redis（可选）
    # 注意：在生产环境中不要这样做，除非你确定要删除所有数据
    progress_manager.redis_client.flushall()