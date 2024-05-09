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

    # 提供一个全局访问点
    @classmethod
    def get_shared_progress(cls):
        if cls._instance is None:
            cls._instance = cls()  # 修复实例初始化
        return cls._instance
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        elif cls._instance.is_over:
            cls._instance.reset()  # 如果实例存在且任务已完成，则重置它
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'current_step'):  # 检查是否已经初始化
            self.current_step = VectorizationProcess.ARTICLE_FORMAT.value
            self.progress = 0.00
            self.is_over = False

    def update(self, new_step = None, new_progress = 0.00):
        self.progress = new_progress
        if new_step is not None:
            self.current_step = new_step

    def set_progress(self, new_progress):
        self.progress = new_progress

    def set_current_step(self, new_step):
        self.current_step = new_step

    def set_over(self):
        self.is_over = True

    def get_progress(self):
        return self.progress

    def get_current_step(self):
        return self.current_step

    def is_task_over(self):
        return self.is_over
    
    def reset(self):
        self.progress = 0.00
        self.is_over = False
        self.current_step = VectorizationProcess.ARTICLE_FORMAT.value