> 当前项目所使用环境：Python3.6.8，Django3.1

# 项目介绍

##### 1. 后端语言：Python + Django
##### 2. 前端语言：HTML + JQuery + Bootstrap
##### 3. 数据库：MySQL + Redis
##### 4. 大模型：Llama + LangChain

# 实现功能

##### 1. 未使用Django-admin，自己手写的管理后台, 用于文章、友链和背景音乐等的在线管理
##### 2. 实现文章按年月、标签和分类归档
##### 3. 实现文章标签云功能
##### 4. 采用第三方评论插件: [Gitalk](https://github.com/gitalk/gitalk)
##### 5. 实现文章阅读量统计，12小时内连续访问的IP只记录一次
##### 6. 后台引入wangEditor富文本编辑器和editor.md Markdown编辑器，前端使用prism.js进行代码高亮
##### 7. Celery + Redis + Supervisor进行异步任务和定时任务的启动和进程管理
##### 8. 接入[七牛云存储](https://www.qiniu.com/)，文章中的图片通过接口上传到七牛云
##### 9. 添加过期提醒，文章长时间未更新在详情页设置提醒
##### 10. 友情链接随机排序
##### 11. 支持按文章标题、标签和分类搜索
##### 12. 多数数据存入Redis，提升访问速度

# 项目部署

[原项目地址](https://github.com/a1401358759/my_site)

### 本项目使用llama部署本地大模型，然后通过 LangChain 调用，首先确保部署好原项目的环境！

### 
