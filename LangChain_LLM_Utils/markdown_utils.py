import os
import re
import markdown

class MDTool:
    def __init__(self, blog_title, markdown_text):
        self.blog_title = blog_title
        self.markdown_text = markdown_text
        # 句子数
        self.MDLen = 0

    def remove_markdown_links(self):
        # 正则表达式匹配链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        # 使用re.sub替换匹配到的链接为链接文本
        plain_text = re.sub(link_pattern, r'\1', self.markdown_text)
        return plain_text
    
    def remove_markdown_formatting(self):  
        # 先去除Markdown中的链接
        markdown_text_without_links = self.remove_markdown_links()
        # 将Markdown文本转换为HTML
        html_text = markdown.markdown(markdown_text_without_links)
        # 去除HTML标签，不会处理嵌套的标签
        plain_text = html_text.replace('<', '').replace('>', '')
        # 去除可能残留的Markdown格式字符，例如斜体、加粗等
        plain_text = re.sub(r'\*{2}|_{2}', '', plain_text)
        return plain_text.strip()
    
    def split_sentences(self, text):
        # 正则表达式匹配句子结束符，包括中文和英文的句号、问号和感叹号，以及分号
        # 同时考虑可能连续出现的标点符号和前后可能存在的空白字符
        sentence_endings = r'[。！？．；;]+'
        # 使用re.split按照句子结束符分割文本，同时去除空白字符
        sentences = re.split(sentence_endings, text.strip())
        # 进一步去除空句子和句子前后的空白字符
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        return sentences

    def MD2SEP(self) -> str:
        """
        根据 博客文章 的 Markdown文本 和 标题 生成 BERT模型 所需的 输入序列

        Args:
            blog_title (str): 博客文章的标题
            markdown_text (str): 博客文章的Markdown文本内容

        Returns:
            str: 符合BERT模型输入格式的序列字符串

        输入序列格式：
        [CLS] 标题：xxx [SEP] 句子1 [SEP] 句子2 [SEP] ... [SEP] 句子n [SEP]

        其中，[CLS]为分类标记，[SEP]为句子分隔标记，xxx为博客标题，句子1到句子n为Markdown文本解析出的句子
        """
        # 初始化输入序列列表
        input_sequence = ['[CLS]']
        # 添加标题和分隔符到输入序列
        input_sequence.append(f"{self.blog_title} [SEP]")

        # 得到 markdown 句子 list
        sentences = self.split_sentences(self.remove_markdown_formatting())
  
        # 遍历每个句子
        for index, sentence in enumerate(sentences):
            # 忽略空句子
            if sentence.strip() and index != (len(sentences)- 1):
                # 添加句子和分隔符到输入序列
                input_sequence.append(f"{sentence.strip()} [SEP]")

        # 在序列末尾添加额外的分隔符
        input_sequence.append('[SEP]')

        # 更新句子数
        MDLen = len(input_sequence)

        # 将输入序列列表转换为单个字符串
        pis = ' '.join(input_sequence)

        # 去掉processed_input_sequence中的所有换行符  
        text = pis.replace('\n', '')

        # 使用正则表达式去除/li、/ol等标签以及多余的空白字符  
        cleaned_text = re.sub(r'/\w+', '', text).strip().replace('\n', ' ').replace('[SEP] ', '[SEP]')

        # 返回处理后的输入序列字符串
        return cleaned_text
    
    # 获取句子数
    def get_MDLen(self):
        return self.MDLen

if __name__ == "__main__":
    markdown_text = """
在职场中，口才的[重要性](https://so.csdn.net/so/search?q=重要性&spm=1001.2101.3001.7020)不言而喻。无论是与同事沟通协作，还是向上级汇报工作，亦或是与客户洽谈业务，都需要具备良好的口才能力。一个出色的职场人，除了拥有扎实的专业技能外，还应具备出色的口才，以更好地表达自己的想法、解决问题并赢得他人的尊重和信任。因此，提升职场口才成为每一位职场人士必须面对的课题。

![img](https://img-blog.csdnimg.cn/direct/9ff8238d664240f1b9848ff9faf5f3d0.jpeg)

一、职场口才的核心要素

职场口才的核心要素主要包括清晰、准确、有条理的表达，以及适当的情感传递和互动能力。清晰准确的表达能够帮助我们传递明确的信息，避免误解和歧义；有条理的表达则能够使我们的发言更加有逻辑性和说服力；适当的情感传递和互动能力则能够增强我们的感染力，使他人更愿意倾听和接受我们的观点。

二、提升职场口才的方法与途径

1. 积累知识与经验

口才的基础是知识和经验的积累。只有对所在领域有深入的了解和丰富的实践经验，才能在发言时言之有物、言之有理。因此，我们应注重日常学习和实践，不断提升自己的专业素养和实践能力。

1. 练习口语表达

口语表达是提升职场口才的重要途径。我们可以通过朗读、演讲、辩论等方式来锻炼自己的口语表达能力。在练习过程中，要注意发音准确、语调自然、语速适中，并学会运用适当的肢体语言来增强表达效果。

1. 增强逻辑思维能力

逻辑思维能力是职场口才的重要支撑。我们应学会分析问题、归纳总结、提出观点并给出论据。在日常工作中，可以多思考、多讨论，锻炼自己的思维能力和表达能力。

1. 学会倾听与反馈

良好的口才不仅包括说，还包括听。我们应学会倾听他人的观点和意见，理解他人的需求和感受。在倾听的基础上，给予适当的反馈和回应，以展现自己的关注和理解。

1. 掌握职场沟通技巧

职场沟通有其独特的规则和技巧。我们应学会根据[不同的](https://so.csdn.net/so/search?q=不同的&spm=1001.2101.3001.7020)场合和对象调整自己的沟通方式和策略。例如，与上级沟通时要尊重权威、简洁明了；与同事沟通时要平等交流、注重合作；与客户沟通时要热情周到、专业可信。

三、职场口才提升的实践策略

1. 定期参与团队讨论与会议

团队讨论和会议是锻炼职场口才的绝佳场所。我们应积极参与其中，主动发言、分享观点，并在讨论中学会倾听他人的意见并作出合理回应。通过不断实践，我们可以逐渐提高自己的发言质量和应对能力。

1. 参加演讲与辩论活动

演讲和辩论是提升口才的有效方式。我们可以参加公司或行业组织的演讲比赛或辩论活动，通过准备稿件、现场发挥以及与对手的交锋来锻炼自己的表达能力和思维逻辑。

1. 学习优秀演讲者的技巧

优秀的演讲者往往具备出色的口才和表达能力。我们可以通过观看他们的演讲视频或现场聆听他们的发言来学习他们的表达技巧、肢体语言以及情感传递方式，并将其应用到自己的职场沟通中。

1. 反思与总结

提升职场口才是一个持续的过程，我们需要不断反思和总结自己的表现。在每次发言后，我们可以回顾自己的表达方式和效果，找出不足之处并加以改进。同时，我们还可以向他人请教或寻求反馈，以便更好地了解自己在口才方面的优势和不足。

四、职场口才提升的长远意义

提升职场口才不仅有助于我们在当前的工作中取得更好的表现，还具有长远的意义。一个拥有出色口才的职场人，往往能够更好地展示自己的能力和价值，赢得他人的尊重和信任。这不仅有助于个人在职场中的晋升和发展，还能够为公司带来更多的合作机会和业务资源。

此外，提升职场口才还有助于我们更好地应对职场中的挑战和变化。随着社会的不断发展和变化，职场环境也在不断变化。我们需要具备灵活应对的能力，而良好的口才则是实现这一目标的重要工具之一。通过提升职场口才，我们可以更加自信地面对各种挑战和变化，展现出自己的专业素养和应对能力。

五、结语

职场口才的提升是一个长期且需要不断努力的过程。我们需要不断积累知识与经验、练习口语表达、增强逻辑思维能力、学会倾听与反馈并掌握职场沟通技巧。同时，我们还应积极参与实践、学习优秀演讲者的技巧并不断反思与总结。只有这样，我们才能真正提升自己的职场口才水平，为职业生涯的成功奠定坚实的基础。在未来的职场道路上，让我们不断提升自己的口才能力，以更加自信、从容的姿态面对各种挑战和机遇。
"""
    mdt = MDTool("langchain 快速开始", markdown_text)
    inputStr = mdt.MD2SEP()
    print(inputStr)