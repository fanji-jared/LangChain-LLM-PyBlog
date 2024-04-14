from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 默认提示词模板 常量
DEFAULT_PROMPT_TEMPLATE = """
你是一个在网站上热情为读者服务的博客助手AI，你的任务是基于以下已知信息，以友好和亲切的语气为读者的问题提供简洁且专业的回答。在回答时，请合理使用HTML标签来优化文本格式，提升可读性。

你可以使用基本的HTML标签，如<b>加粗</b>、<i>斜体</i>、<u>下划线</u>、<br>换行等，来突出关键信息或改善文本布局。但请确保不要过度使用标签，保持回答的自然和简洁。
请确保你的回答直接相关于已知内容，并且不要包含任何编造成分。
如果无法直接从已知内容中得出答案，你可以以亲切的语气回答 "根据目前的信息，我暂时无法直接回答这个问题" 或 "对于这个问题，目前提供的信息可能还不够充分哦"。
同时，你的回答应该既体现你的专业性，又让读者感受到你的友好和热情。
请使用中文回答，并在回答结束时附上一句亲切的问候或鼓励，比如“希望这能帮到你！”或者“如果你还有其他问题，随时告诉我哦！”。

已知内容:
{context}

问题:
{question}

网站背景信息（供你了解你的工作环境）：
本网站是一个专注于博客写作和分享的平台，读者们在这里寻找写作灵感、学习写作技巧，并交流博客运营经验。作为博客助手AI，你的目标是帮助他们更好地利用网站资源，提升博客质量，并与他们建立友好的互动关系。
"""

class LangChainTool:  
    def __init__(self, context, question, prompt_template: str = DEFAULT_PROMPT_TEMPLATE):
        """
        根据提示语句和问题生成回答

        Args:
            context (str): 用于生成回答的提示语句或背景信息
            question (str): 用户提出的需要回答的问题
            prompt_template (str): 用于生成LLM模型输入提示的模板，自定义以调整回答的风格和格式

        Returns:
            None: 此函数不返回任何值，但可能更新全局状态或执行其他操作
        """
        self.context = context
        self.question = question
        # 加载本地ollama模型
        self.llm = Ollama(model="llama2-chinese")
        # 如果没有提供提示词模板，则使用默认的提示词模板
        self.prompt_template = prompt_template
        self.llm_chain = LLMChain(
            llm = self.llm,
            prompt = PromptTemplate.from_template(self.prompt_template)
        )
        
    # 填充 提示词模板 并 获得回答
    def getrun(self):
        """
        生成回答

        Args:
            None: 构造函数传入参数

        Returns:
            Str: chain.run 输出的是字符串而不是字典
        """
        result = self.llm_chain.invoke({
            "context": self.context,
            "question": self.question
        })
        return result
         
    # 获取提示语句
    def get_context(self):
        return self.context
    
    # 获取问题
    def get_question(self):
        return self.question


if __name__ == "__main__":  
    # 示例的提示语句和问题
    context = "博客助手AI是一个专门为博客作者提供帮助的人工智能。它可以回答有关博客写作、发布和推广的各种问题。"
    question = "请问如何撰写一篇吸引读者的博客文章？"

    # 初始化LangChainTool对象
    lct = LangChainTool(context, question)

    # 运行并获取回答
    answer = lct.getrun()

    # 打印回答
    print("生成的回答:")
    print(answer)
      
    # 如果需要，还可以打印提示语句和问题用于调试
    print("使用的提示语句:")
    print(lct.get_context())

    print("提出的问题:")
    print(lct.get_question())