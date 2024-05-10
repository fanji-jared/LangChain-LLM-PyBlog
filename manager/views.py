# -*- coding: utf-8 -*-
from datetime import datetime
import urllib.parse
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from utils.errorcode import ERRORCODE
from utils.dlibs.http.response import http_response
from utils.dlibs.tools.paginator import paginate
from utils.libs.utils.mine_qiniu import upload_data
from utils.common import form_error
from article.models import (
    Article, Links, Classification, CarouselImg,
    Music, Author, OwnerMessage, Tag
)
from article.constants import EditorKind, BlogStatus, CarouselImgType
from manager.forms import (
    SearchBlogForm, AddFriendLinkForm, OperateOwnMessageForm, LoginForm, AddAuthorForm,
    AddMusicForm, AddCarouselForm, OperateBlogForm, ChangePasswordForm, UpdateBlogStatusForm
)
from django.core.exceptions import ObjectDoesNotExist

# 导入工具使用类
from LangChain_LLM_Utils import Manger
LLUM = Manger()

# 导入 article_vector_task
from article.tasks import article_vector_task

# 获取 SharedProgress 单例实例
from LangChain_LLM_Utils.SharedProgress_Been import SharedProgress
SP = SharedProgress()

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

def login_view(request):
    """
    用户登录
    :param request:
    :return:
    """
    back_url = request.parameters.get('back_url')
    if not back_url:
        back_url = reverse('blog_list')
    user_info = request.session.get('user_info')
    if user_info:
        return HttpResponseRedirect(back_url)

    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'manager/login.html', {"back_url": back_url, "form": form})

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            messages.warning(request, '登录失败')
            return HttpResponseRedirect(reverse('login_view'))

        user_name = form.cleaned_data.get('user_name')
        password = form.cleaned_data.get('password')
        user = authenticate(username=user_name, password=password)
        if not user:
            messages.error(request, '登录失败，请检查用户名密码后重试.')
            return HttpResponseRedirect('%s?%s' % (reverse('login_view'), urllib.parse.urlencode({'back_url': back_url})))
        login(request, user)
        return HttpResponseRedirect(reverse('blog_list'))


@login_required
def logout_view(request):
    """
    用户登出
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('/manager')


@login_required
def change_passwd_view(request):
    """
    修改密码
    """
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            if user.check_password(form.cleaned_data['old_password']):
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                messages.success(request, '密码修改成功，请重新登录')
                return HttpResponseRedirect(reverse("logout_view"))
            else:
                messages.error(request, '原密码错误.')
                return HttpResponseRedirect(reverse('change_password'))
    else:
        form = ChangePasswordForm()
    data = {
        'form': form
    }
    return render(request, "manager/change_password.html", data)


@login_required
def blog_list_view(request):
    """
    博客列表
    :param request:
    :return:
    """
    form = SearchBlogForm(request.GET)
    form.is_valid()
    query = Q()
    title = form.cleaned_data.get("title")
    if title:
        query &= (Q(title__icontains=title) | Q(classification__name=title) | Q(tags__name=title))

    blogs = Article.objects.select_related().filter(query).order_by("-id")

    # 为每个博客对象添加 isVectorize 属性
    for blog in blogs:
        try:
            # 根据 blog.id 在 milvus数据库 是否存在 来确定 isVectorize 的值
            blog.isVectorize = LLUM.getIDVectorize(blog.id)
        except:
            # 默认，假设所有博客都没有向量化
            blog.isVectorize = False

    blog_list, total = paginate(
        blogs,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/blog_list.html', {
        "active_classes": ['.blog', '.blog_list'],
        "params": request.GET,
        "form": form,
        "data_list": blog_list,
        "total": total,
    })


@login_required
def blog_create_view(request):
    """
    博客添加
    """
    tp = "manager/create_blog.html"
    auhtors = Author.objects.values("id", "name")
    classifications = Classification.objects.values("id", "name")
    tags = Tag.objects.values("id", "name")
    context = {
        "active_classes": ['.blog', '.blog_list'],
        "auhtors": auhtors,
        "classifications": classifications,
        "tags": tags,
        "blog_status": BlogStatus.CHOICES,
    }
    if request.method == "GET":
        return render(request, tp, context)

    if request.method == "POST":
        form = OperateBlogForm(request.POST)
        if not form.is_valid():
            messages.warning(request, "</br>".join(form_error(form)))
            return HttpResponseRedirect(reverse('blog_list'))
        try:
            article = Article.objects.create(
                title=form.cleaned_data.get("title"),
                author_id=form.cleaned_data.get("author"),
                classification_id=form.cleaned_data.get("classification"),
                content=form.cleaned_data.get("content"),
                count=form.cleaned_data.get("count"),
                status=form.cleaned_data.get("status"),
                editor=EditorKind.Markdown,
            )
            tags = request.POST.getlist('tags')
            article.set_tags(tags)
            messages.success(request, '添加成功')
            cache.delete_pattern("tmp_articles")  # 清除缓存
            cache.delete_pattern("tmp_archive")  # 清除缓存
            return HttpResponseRedirect(reverse('blog_list'))
        except Exception as ex:
            messages.warning(request, ex)
            return HttpResponseRedirect(reverse('blog_list'))


@login_required
def blog_edit_view(request, item_id):
    """
    博客编辑
    :param request:
    :return:
    """
    article = Article.objects.filter(id=item_id).first()
    if not article:
        messages.warning(request, "此博客不存在")
        return HttpResponseRedirect(reverse('blog_list'))

    selected_tags = article.get_tags()
    auhtors = Author.objects.values("id", "name")
    classifications = Classification.objects.values("id", "name")
    tags = Tag.objects.values("id", "name")
    context = {
        "active_classes": ['.blog', '.blog_list'],
        "article": article,
        "auhtors": auhtors,
        "classifications": classifications,
        "tags": tags,
        "selected_tags": selected_tags,
        "blog_status": BlogStatus.CHOICES,
        "item_id": item_id
    }
    if request.method == "GET":
        return render(request, "manager/edit_blog.html", context)

    if request.method == "POST":
        form = OperateBlogForm(request.POST)
        if not form.is_valid():
            messages.warning(request, "</br>".join(form_error(form)))
            return HttpResponseRedirect(reverse('blog_list'))

        try:
            new_tags = request.POST.getlist('tags')
            article.set_tags(new_tags)
            Article.objects.filter(id=item_id).update(
                title=form.cleaned_data.get("title"),
                author_id=form.cleaned_data.get("author"),
                classification_id=form.cleaned_data.get("classification"),
                content=form.cleaned_data.get("content"),
                count=form.cleaned_data.get("count"),
                status=form.cleaned_data.get("status"),
                editor=form.cleaned_data.get("editor"),
                last_update=datetime.now()
            )
            messages.success(request, '修改成功')
            cache.delete_pattern("tmp_articles")  # 清除缓存
            cache.delete_pattern("tmp_archive")  # 清除缓存
            return HttpResponseRedirect(reverse('blog_list'))
        except Exception as ex:
            messages.warning(request, ex)
            return HttpResponseRedirect(reverse('blog_list'))


@login_required
def blog_del_view(request):
    """
    删除博客
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Article.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern("tmp_articles")  # 清除缓存
        cache.delete_pattern("tmp_archive")  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def blog_update_status_view(request):
    """
    发布或撤回博客
    """
    form = UpdateBlogStatusForm(request.POST)
    if not form.is_valid():
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR)

    blog_id = form.cleaned_data.get('blog_id')
    status = form.cleaned_data.get('status')

    try:
        if Article.objects.filter(id=blog_id).update(status=status) <= 0:
            return http_response(request, statuscode=ERRORCODE.NOT_FOUND)
        cache.delete_pattern("tmp_articles")  # 清除缓存
        cache.delete_pattern("tmp_archive")  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='失败: %s' % e)
    
@login_required
def blog_vector_status_view(request):
    """
    向量化 / 删除向量化 视图
    """
    form = UpdateBlogStatusForm(request.POST)
    if not form.is_valid():
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR)

    blog_id = int(form.cleaned_data.get('blog_id'))
    status = int(form.cleaned_data.get('status'))

    # 调用 LangChain_LLM_Utils 向量化或删除向量化（本质为 增加集合 删除集合）
    try:
        # 尝试获取具有特定ID的文章对象
        article = Article.objects.get(id = blog_id)

        # 获取文章标题和内容
        title = str(article.title)
        content = str(article.content)

        # 当前选项没有向量化，想要向量化，值为 1
        if status == 1:

            Print("# 开始向量化 !!启动了一个异步任务!!")

            # 使用 Celery 来调用向量化操作函数
            task = article_vector_task.delay(blog_id, title, content)

            # 返回成功响应 TaskId
            return http_response(request, statuscode=ERRORCODE.START_VECTOR, msg=task.id)
        elif status == 2: # 当前选项已经向量化，想要去向量化，值为 2
            # 开始去向量化
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            

            # 返回成功响应
            return http_response(request, statuscode=ERRORCODE.REMOVE_VECTOR, msg=title)
    
    except ObjectDoesNotExist:
        # 如果文章不存在，返回参数错误响应
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, message='ID not exist')
    
    except Exception as e:
        # 返回通用错误响应
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='失败: %s' % e)

@login_required
def get_vectorization_process(request):
    # 从GET请求中获取blog_id参数
    blog_id_str = request.GET.get('blog_id')  # 这将返回一个字符串或者None

    # 检查blog_id_str是否存在并且是一个可以转换为整数的字符串
    if blog_id_str is not None and blog_id_str.isdigit():
        blog_id = int(blog_id_str)  # 转换为整数

        # 获取当前向量化 流程步骤 和 完成百分比
        try:
            # 检查 blog_id 任务状态并返回相应信息
            if not SP.has_progress(blog_id):
                return http_response(request, statuscode=ERRORCODE.NO_TASK)  # 没有流程化任务
            elif LLUM.getIDVectorize(blog_id):
                return http_response(request, statuscode=ERRORCODE.TASK_OVER) #  流程化任务结束
            else:
                # 获取 blog_id 状态和进度
                current_step, progress = SP.get_progress(blog_id)

                # 检查 current_step 或 progress 是否为 None
                if current_step is None or progress is None:
                    return http_response(request, sstatuscode=ERRORCODE.UNKNOWN, context={f"current_step: {current_step}, progress: {progress}"})
                
                return http_response(request, statuscode=ERRORCODE.SUCCESS, context={
                    "current_step": str(current_step),
                    "progress": str(progress)
                })

        except Exception as e:
            return http_response(request, statuscode=ERRORCODE.UNKNOWN, context={f"读取向量化状态时发生错误: {e}"})
    else:
        # 如果 blog_id 错误，返回参数错误响应
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, message='GET param \'blog_id\' is error!')

@login_required
def friend_link_list_view(request):
    """
    友情链接列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    links = Links.objects.filter(query).order_by("-id")
    link_list, total = paginate(
        links,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/link_list.html', {
        "active_classes": ['.blog', '.link_list'],
        "params": request.GET,
        "data_list": link_list,
        "total": total,
        "name": name
    })


@login_required
def add_friend_link_view(request):
    """
    添加/编辑友情链接
    """
    form = AddFriendLinkForm(request.POST)
    if not form.is_valid():
        messages.warning(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('friend_link_list'))

    edit_id = form.cleaned_data.get('edit_id')
    try:
        if not edit_id:
            Links.objects.create(
                name=form.cleaned_data.get('name'),
                link=form.cleaned_data.get('link'),
                avatar=form.cleaned_data.get('avatar'),
                desc=form.cleaned_data.get('desc'),
            )
            messages.success(request, '添加成功')
        else:
            Links.objects.filter(id=edit_id).update(
                name=form.cleaned_data.get('name'),
                link=form.cleaned_data.get('link'),
                avatar=form.cleaned_data.get('avatar'),
                desc=form.cleaned_data.get('desc'),
            )
            messages.success(request, '编辑成功')
        cache.delete_pattern('tmp_links')  # 清除缓存
        return HttpResponseRedirect(reverse('friend_link_list'))
    except Exception as e:
        messages.error(request, '操作失败: %s' % e)
        return HttpResponseRedirect(reverse('friend_link_list'))


@login_required
def del_friend_link_view(request):
    """
    删除友情链接
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Links.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern('tmp_links')  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def author_list_view(request):
    """
    作者列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    authors = Author.objects.filter(query).order_by("-id")
    author_list, total = paginate(
        authors,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/author_list.html', {
        "active_classes": ['.blog', '.author_list'],
        "params": request.GET,
        "data_list": author_list,
        "total": total,
        "name": name
    })


@login_required
def add_author_view(request):
    """
    添加作者
    """
    form = AddAuthorForm(request.POST)
    if not form.is_valid():
        messages.warning(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('author_list'))

    item_id = form.cleaned_data.get('item_id')
    try:
        if not item_id:
            Author.objects.create(
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                website=form.cleaned_data.get('website'),
            )
            messages.success(request, '添加成功')
        else:
            Author.objects.filter(id=item_id).update(
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                website=form.cleaned_data.get('website'),
            )
            messages.success(request, '编辑成功')
        return HttpResponseRedirect(reverse('author_list'))
    except Exception as e:
        messages.error(request, '操作失败: %s' % e)
        return HttpResponseRedirect(reverse('author_list'))


@login_required
def del_author_view(request):
    """
    删除作者
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Author.objects.filter(id__in=item_ids).delete()
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def classification_list_view(request):
    """
    文章分类列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    classifications = Classification.objects.filter(query).order_by("-id")
    classification_list, total = paginate(
        classifications,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/classification_list.html', {
        "active_classes": ['.blog', '.classification_list'],
        "params": request.GET,
        "data_list": classification_list,
        "total": total,
        "name": name
    })


@login_required
def add_classification_view(request):
    """
    添加文章分类
    """
    item_id = request.POST.get('item_id')
    try:
        if not item_id:
            Classification.objects.create(name=request.POST.get('name'))
            messages.success(request, '添加成功')
        else:
            Classification.objects.filter(id=item_id).update(name=request.POST.get('name'))
            messages.success(request, '编辑成功')
        cache.delete_pattern('tmp_classification')  # 清除缓存
        return HttpResponseRedirect(reverse('classification_list'))
    except Exception as e:
        messages.error(request, '操作失败: %s' % e)
        return HttpResponseRedirect(reverse('classification_list'))


@login_required
def del_classification_view(request):
    """
    删除文章分类
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Classification.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern('tmp_classification')  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def tag_list_view(request):
    """
    文章标签列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    tags = Tag.objects.filter(query).order_by("-id")
    tag_list, total = paginate(
        tags,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/tag_list.html', {
        "active_classes": ['.blog', '.tag_list'],
        "params": request.GET,
        "data_list": tag_list,
        "total": total,
        "name": name
    })


@login_required
def add_tag_view(request):
    """
    添加文章标签
    """
    item_id = request.POST.get('item_id')
    try:
        if not item_id:
            Tag.objects.create(name=request.POST.get('name'))
            messages.success(request, '添加成功')
        else:
            Tag.objects.filter(id=item_id).update(name=request.POST.get('name'))
            messages.success(request, '编辑成功')
        cache.delete_pattern('tmp_tags')  # 清除缓存
        return HttpResponseRedirect(reverse('tag_list'))
    except Exception as e:
        messages.error(request, '操作失败: %s' % e)
        return HttpResponseRedirect(reverse('tag_list'))


@login_required
def del_tag_view(request):
    """
    删除文章标签
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Tag.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern('tmp_tags')  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def music_list_view(request):
    """
    背景音乐列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    musics = Music.objects.filter(query).order_by("-id")
    music_list, total = paginate(
        musics,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/music_list.html', {
        "active_classes": ['.blog', '.music_list'],
        "params": request.GET,
        "data_list": music_list,
        "total": total,
        "name": name
    })


@login_required
def add_music_view(request):
    """
    添加背景音乐
    """
    form = AddMusicForm(request.POST)
    if not form.is_valid():
        messages.error(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('music_list'))
    try:
        Music.objects.create(
            name=form.cleaned_data.get('name'),
            url=form.cleaned_data.get('url'),
            cover=form.cleaned_data.get('cover'),
            artist=form.cleaned_data.get('artist'),
        )
        messages.success(request, '添加成功')
        cache.delete_pattern('tmp_musics')  # 清除缓存
        return HttpResponseRedirect(reverse('music_list'))
    except Exception as e:
        messages.error(request, '添加失败: %s' % e)
        return HttpResponseRedirect(reverse('music_list'))


@login_required
def del_music_view(request):
    """
    删除背景音乐
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        Music.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern('tmp_musics')  # 清除缓存
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def carousel_list_view(request):
    """
    轮播图片列表
    :param request:
    :return:
    """
    query = Q()
    name = request.GET.get('name')
    if name:
        query &= Q(name__icontains=name)

    carousels = CarouselImg.objects.filter(query).order_by("-id")
    carousel_list, total = paginate(
        carousels,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/carousel_list.html', {
        "active_classes": ['.blog', '.carousel_list'],
        "params": request.GET,
        "data_list": carousel_list,
        "total": total,
        "name": name,
        "image_types": CarouselImgType.CHOICES
    })


@login_required
def add_carousel_view(request):
    """
    添加轮播图片
    """
    form = AddCarouselForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "</br>".join(form_error(form)))
        return HttpResponseRedirect(reverse('carousel_list'))
    try:
        img_path = ''
        filestream = request.FILES.get('path')
        if filestream:
            _, img_path = upload_data(filestream, 'blog')
        img_type = int(form.cleaned_data.get('img_type'))
        edit_id = request.POST.get('edit_id')

        if not edit_id:
            CarouselImg.objects.create(
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                path=img_path,
                link=form.cleaned_data.get('link'),
                weights=form.cleaned_data.get('weights'),
                img_type=img_type,
            )
            messages.success(request, '添加成功')
        else:
            data = {
                'name': form.cleaned_data.get('name'),
                'description': form.cleaned_data.get('description'),
                'link': form.cleaned_data.get('link'),
                'weights': form.cleaned_data.get('weights'),
                'img_type': img_type,
            }
            if img_path:
                data['path'] = img_path
            CarouselImg.objects.filter(id=edit_id).update(**data)
            messages.success(request, '编辑成功')
        if img_type == CarouselImgType.BANNER:
            cache.delete_pattern('tmp_carouse_imgs')  # 清除缓存
        elif img_type == CarouselImgType.ADS:
            cache.delete_pattern('tmp_ads_imgs')  # 清除缓存
        return HttpResponseRedirect(reverse('carousel_list'))
    except Exception as e:
        messages.error(request, '操作失败: %s' % e)
        return HttpResponseRedirect(reverse('carousel_list'))


@login_required
def del_carousel_view(request):
    """
    删除轮播图片
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        CarouselImg.objects.filter(id__in=item_ids).delete()
        cache.delete_pattern('tmp_carouse_imgs')  # 清除缓存
        cache.delete_pattern('tmp_ads_imgs')
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def ownmessage_list_view(request):
    """
    主人寄语列表
    """
    messages = OwnerMessage.objects.order_by("-id")
    ownmessage_list, total = paginate(
        messages,
        request.GET.get('page') or 1
    )

    return render(request, 'manager/ownmessage_list.html', {
        "active_classes": ['.blog', '.ownmessage_list'],
        "params": request.GET,
        "data_list": ownmessage_list,
        "total": total,
    })


@login_required
def add_ownmessage_view(request):
    """
    添加主人寄语
    """
    tp = "manager/create_ownmessage.html"
    context = {
        "active_classes": ['.blog', '.ownmessage_list'],
    }
    if request.method == "GET":
        return render(request, tp, context)

    if request.method == "POST":
        form = OperateOwnMessageForm(request.POST)
        if not form.is_valid():
            messages.warning(request, "</br>".join(form_error(form)))
            return HttpResponseRedirect(reverse('ownmessage_list'))
        try:
            OwnerMessage.objects.create(
                summary=form.cleaned_data.get("summary"),
                message=form.cleaned_data.get("message"),
                editor=EditorKind.Markdown
            )
            messages.success(request, '添加成功')
            return HttpResponseRedirect(reverse('ownmessage_list'))
        except Exception as ex:
            messages.warning(request, ex)
            return HttpResponseRedirect(reverse('ownmessage_list'))


@login_required
def edit_ownmessage_view(request, item_id):
    """
    主人寄语编辑
    :param request:
    :return:
    """
    message = OwnerMessage.objects.filter(id=item_id).first()
    if not message:
        messages.warning(request, "此主人寄语不存在")
        return HttpResponseRedirect(reverse('ownmessage_list'))
    tp = "manager/edit_ownmessage.html"
    context = {
        "active_classes": ['.blog', '.ownmessage_list'],
        "message": message,
        "item_id": item_id
    }
    if request.method == "GET":
        return render(request, tp, context)

    if request.method == "POST":
        form = OperateOwnMessageForm(request.POST)
        if not form.is_valid():
            messages.warning(request, "</br>".join(form_error(form)))
            return HttpResponseRedirect(reverse('ownmessage_list'))
        data = {
            "summary": form.cleaned_data.get("summary"),
            "message": form.cleaned_data.get("message"),
            "editor": form.cleaned_data.get("editor"),
            "last_update": datetime.now()
        }
        try:
            OwnerMessage.objects.filter(id=item_id).update(**data)
            messages.success(request, '修改成功')
            return HttpResponseRedirect(reverse('ownmessage_list'))
        except Exception as ex:
            messages.warning(request, ex)
            return HttpResponseRedirect(reverse('ownmessage_list'))


@login_required
def del_ownmessage_view(request):
    """
    删除主人寄语
    """
    item_ids = request.POST.getlist('item_ids')
    if not item_ids:
        return http_response(request, statuscode=ERRORCODE.PARAM_ERROR, msg='参数错误')

    try:
        OwnerMessage.objects.filter(id__in=item_ids).delete()
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as e:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg='删除失败: %s' % e)


@login_required
def clear_caches_view(request):
    """
    清除全部缓存
    """
    try:
        cache.delete_pattern("tmp_*")
        return http_response(request, statuscode=ERRORCODE.SUCCESS)
    except Exception as exp:
        return http_response(request, statuscode=ERRORCODE.FAILED, msg=exp)
