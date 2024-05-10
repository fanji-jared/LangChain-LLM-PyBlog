from datetime import datetime
import tempfile
import torch
from transformers import BertTokenizer, BertModel

from pathlib import Path
import os

# 获取 SharedProgress 单例实例
from LangChain_LLM_Utils.SharedProgress_Been import SharedProgress, VectorizationProcess
SP = SharedProgress()

class BertModelTool:
    def __init__(self, save_directory='./bert-base-chinese-local'):
        self.nowSentencesI = 1 # 用于计算进度
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
        
        self.model.eval()  # 设置模型为评估模式

    def get_tokenizer(self):
        return self.tokenizer
    
    def get_model(self):
        return self.model
    
    def get_nowSentencesI(self):
        return self.nowSentencesI

    def get_article_embedding(self, sentences_list):
        """  
        获取整篇文章的嵌入表示
    
        Args:  
            sentences_list (list): 句子列表，用于合并成整篇文章
    
        Returns:  
            numpy.ndarray: 文章整体嵌入的 NumPy 数组
            [[ 1.18853319e+00 -1.04827571e+00 7.83498824e-01 -3.44603896e-01 ]]
        """
        # 合并句子列表为一个长文本
        article_text = ' '.join(sentences_list)
        # 文本标记化
        inputs = self.tokenizer(article_text, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512, padding=True, return_overflowing_tokens=False)
        # 获取模型的输出
        with torch.no_grad():
            outputs = self.model(**inputs)
        # 假设我们使用第一个隐藏状态作为句子嵌入
        sentence_embeddings = outputs.last_hidden_state[:, 0, :]

        # 返回 文章整体嵌入 数组
        return sentence_embeddings.cpu().numpy()

    def get_sentences_embeddings(self, id, sentences_list):
        """  
        获取句子列表中每个句子的嵌入表示
    
        Args:
            sentences_list (list): 句子列表，每个句子将被单独处理以获取嵌入
    
        Returns:
            list: 包含每个句子嵌入的 NumPy 数组的列表
            [
                array([[ 1.23959875e+00,  2.59410173e-01 1.74765006e-01, -2.03462631e-01]], dtype=float32),
                array([[ 1.23959875e+00,  2.59410173e-01 1.74765006e-01, -2.03462631e-01]], dtype=float32)
            ]
        """
        # 初始化一个空列表来存储句子嵌入
        sentence_embeddings = []
        # 遍历每个句子
        for i, sentence in enumerate(sentences_list, start = 1):
            # 文本标记化
            inputs = self.tokenizer(sentence, return_tensors="pt", add_special_tokens=True, truncation=True, max_length=512, padding='max_length', return_overflowing_tokens=False)
            # 获取模型的输出
            with torch.no_grad():
                outputs = self.model(**inputs)
            # 提取CLS标记对应的隐藏状态作为句子嵌入
            sentence_embedding = outputs.last_hidden_state[:, 0, :]
            # 将嵌入添加到列表中
            sentence_embeddings.append(sentence_embedding.cpu().numpy())

            # 传出i
            self.nowSentencesI = i
            
            # 设置状态和进度
            progress = min(100, (i / len(sentences_list)) * 100)  # 转换为百分比并限制在0-100之间
            SP.set_progress(id, VectorizationProcess.TEXT_VEC.value, progress)

        return sentence_embeddings
    
    def test(self):
        # 测试：对文本进行编码
        encoded_input = self.tokenizer("你好，这里是测试函数，怎么样了，成功运行了？", return_tensors="pt")
        output = self.model(**encoded_input)
        
        # 获取输出向量的维度
        output_tensor = output.last_hidden_state
        # print(output_tensor)
        print(output_tensor.size())

# inputs是一个字典，包含input_ids, attention_mask等键
# input_ids就是tokenizer处理后的token IDs张量
# input_ids = inputs['input_ids']
# # 将token IDs解码回文本
# decoded_text = self.tokenizer.decode(input_ids.squeeze().tolist())

if __name__ == "__main__":
    BML = BertModelTool()
    BML.test()

    sentences_list = ['langchain 快速开始', '在职场中，口才的重要性不言而喻', '无论是与同事沟通协作，还是向上级汇报工作，亦或是与客户洽谈业务，都需要具备良好的口才能力', '一个出色的职场人，除了拥有扎实的专业技能外，还应具备出色的口才，以更好地表达自己的想法、解决问题并赢得他人的尊重和信任', '因此，提升职场口才成为每一位职场人士必须面对的课题', '一、职场口才的核心要素\n职场口才的核心要素主要包括清晰、准确、有条理的表达，以及适当的情感传递和互动能力', '清晰准确的表达能够帮助我们传递明确的信息，避免误解和歧义', '有条理的表达则能够使我们的发言更加有逻辑性和说服力', '适当的情感传递和互动能力则能够增强我们的感染力，使他人更愿意倾听和接受我们的观点', '二、提升职场口才的方法与途径\n\n积累知识与经验\n\n口才的基础是知识和经验的积累', '只有对所在领域有深入的了解和丰富的实践经验，才能在发言时言之有物、言之有理', '因此，我们应注重日常学习和实践，不断提升自己的专业素养和实践能力', '练习口语表达\n\n口语表达是提升职场口才的重要途径', '我们可以通过朗读、演讲、辩论等方式来锻炼自己的口语表达能力', '在练习过程中，要注意发音准确、语调自然、语速适中，并学会运用适当的肢体语言来增强表达效果', '增强逻辑思维能力\n\n逻辑思维能力是职场口才的重要支撑', '我们应学会分析问题、归纳总结、提出观点并给出论据', '在日常工作中，可以多思考、多讨论，锻炼自己的思维能力和表达能力', '学会倾听与反馈\n\n良好的口才不仅包括说，还包括听', '我们应学会倾听他人的观点和意见，理解他人的需求和感受', '在倾听的基础上，给予适当的反馈和回应，以展现自己的关注和理解', '掌握职场沟通技巧\n\n职场沟通有其独特的规则和技巧', '我们应学会根据不同的场合和对象调整自己的沟通方式和策略', '例如，与上级沟通时要尊重权威、简洁明了', '与同事沟通时要平等交流、注重合作', '与客户沟通时要热情周到、专业可信', '三、职场口才提升的实践策略\n\n定期参与团队讨论与会议\n\n团队讨论和会议是锻炼职场口才的绝佳场所', '我们应积极参与其中，主动发言、分享观点，并在讨论中学会倾听他人的意见并作出合理回应', '通过不断实践，我们可以逐渐提高自己的发言质量和应对能力', '参加演讲与辩论活动\n\n演讲和辩论是提升口才的有效方式', '我们可以参加公司或行业组织的演讲比赛或辩论活动，通过准备稿件、现场发挥以及与对手的交锋来锻炼自己的表达能力和思维逻辑', '学习优秀演讲者的技巧\n\n优秀的演讲者往往具备出色的口才和表达能力', '我们可以通过观看他们的演讲视频或现场聆听他们的发言来学习他们的表达技巧、肢体语言以及情感传递方式，并将其应用到自己的职场沟通中', '反思与总结\n\n提升职场口才是一个持续的过程，我们需要不断反思和总结自己的表现', '在每次发言后，我们可以回顾自己的表达方式和效果，找出不足之处并加以改进', '同时，我们还可以向他人请教或寻求反馈，以便更好地了解自己在口才方面的优势和不足', '四、职场口才提升的长远意义\n提升职场口才不仅有助于我们在当前的工作中取得更好的表现，还具有长远的意义', '一个拥有出色口才的职场人，往往能够更好地展示自己的能力和价值，赢得他人的尊重和信任', '这不仅有助于个人在职场中的晋升和发展，还能够为公司带来更多的合作机会和业务资源', '此外，提升职场口才还有助于我们更好地应对职场中的挑战和变化', '随着社会的不断发展和变化，职场环境也在不断变化', '我们需要具备灵活应对的能力，而良好的口才则是实现这一目标的重要工具之一', '通过提升职场口才，我们可以更加自信地面对各种挑战和变化，展现出自己的专业素养和应对能力', '五、结语\n职场口才的提升是一个长期且需要不断努力的过程', '我们需要不断积累知识与经验、练习口语表达、增强逻辑思维能力、学会倾听与反馈并掌握职场沟通技巧', '同时，我们还应积极参与实践、学习优秀演讲者的技巧并不断反思与总结', '只有这样，我们才能真正提升自己的职场口才水平，为职业生涯的成功奠定坚实的基础', '在未来的职场道路上，让我们不断提升自己的口才能力，以更加自信、从容的姿态面对各种挑战和机遇']
    
    # 获取文章向量
    print(BML.get_article_embedding(sentences_list))

    # 获取句子向量
    print(BML.get_sentences_embeddings(sentences_list))