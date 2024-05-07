# -*- coding: utf-8 -*-

import requests
from article.models import Article
from article.constants import BlogStatus, DOMAIN
from celery import shared_task
from utils.libs.logger.syslogger import SysLogger
from utils.send_email import SendEmailClient


# 导入工具使用类
from LangChain_LLM_Utils import Manger
LLUM = Manger()

@shared_task
def submit_urls_to_baidu():
    articles = Article.objects.filter(status=BlogStatus.PUBLISHED).order_by('-id')
    urls = [DOMAIN + article.get_absolute_url() for article in articles]
    api = 'http://data.zz.baidu.com/urls?site=xxxxxxxx&token=xxxxxxxxxx'
    response = requests.post(api, data='\n'.join(urls))
    SysLogger.info(response.content.decode())
    print(response.content.decode())


@shared_task
def send_email_task(mail, mail_body):
    send_client = SendEmailClient()
    subject = '👉 咚！「LLM智能博客」上有新评论了'
    receivers = [mail]
    result = send_client.send_email(subject, receivers, mail_body)
    print(result)
    return result

@shared_task
def article_vector_task(id, title, content):
    """
    使用 Celery 来调用向量化操作函数
    """
    LLUM.article_vector(id, title, content)