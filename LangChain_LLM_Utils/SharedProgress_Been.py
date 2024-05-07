from datetime import datetime
from enum import Enum  
  
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
    """
    向量化流程状态传递类
    """
    _instance = None

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

    # 用于判断单例是否存在
    def is_none():
        return SharedProgress._instance is None

    # 提供一个全局访问点
    def get_shared_progress():
        if SharedProgress.is_none():
            SharedProgress()  # 触发__new__和__init__的调用来初始化单例
        return SharedProgress._instance
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        elif cls._instance.is_over:
            cls._instance.reset()  # 如果实例存在且任务已完成，则重置它
        return cls._instance

    def __init__(self):
        self.current_step = VectorizationProcess.ARTICLE_FORMAT  # 初始化当前步骤为文章格式化
        self.progress = 0.00  # 初始化当前进度为 0.00
        self.is_over = False  # 初始化所有任务未完成

    def update(self, new_progress, new_step=None):
        self.progress = new_progress
        if new_step is not None:
            self.current_step = new_step

    def set_over(self):
        self.is_over = True

    def get_progress(self):
        return self.progress

    def get_current_step(self):
        return self.current_step.value

    def is_task_over(self):
        return self.is_over
    
    def reset(self):
        self.progress = 0.00
        self.is_over = False
        self.current_step = VectorizationProcess.ARTICLE_FORMAT