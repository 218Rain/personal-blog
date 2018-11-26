from flask import render_template, request,url_for, redirect
from flask import abort

from app import db
from . import main

from flask_login import login_required

# 主页
@main.route('/')
def index():
    # render_template会去app/templates下找模板
    return render_template('main/index.html')

# 个人主页，没有认证就不能访问
@main.route('/user_info')
@login_required
def user_info():
    # 访问视图用户资料视图
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id = id).first()
    if user is None:
        abort(404)
    return render_template('main/user_info.html', user=user)

@main.route('/favicon.ico')
def favicon():
    return 'ok'

# 更改个人信息表单
from app.models import User
from .forms import EditUserForm
# current_user根据cookie查找用户id，保cookie存了登录信息：登录状态
from flask_login import current_user
# methods提交表单
@main.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    form = EditUserForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        if len(form.password.data) != 0:
            current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('.user_info', id=current_user.id))

    form.email.data = current_user.email
    form.name.data = current_user.name
    # form.password.data = '*******'
    # form.password_again.data = '*******'
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('main/edit_user.html', form=form)

# 全部新闻
from app.models import Follow
#http://127.0.0.1/all_news?page=4
#http://127.0.0.1/all_news
@main.route('/all_news')
def all_news() :
    # ans = News.query.all()
    # 分页对象
    page = request.args.get('page', type=int, default=1)
    # 获取cookie中follow_flag的值 '0' '1'
    follow_flag = request.cookies.get('follow_flag', default='0')

    # 所有的
    if follow_flag == '0':
        # order_by(News.id.desc())降序
        paginate = News.query.order_by(News.id.desc()).paginate(page=page, per_page=5, error_out=False)
    else:
        # followeds = Follow.query.filter_by(follower_id=current_user.id).all()
        # users = [f.followed for f in followeds]
        # news = [u.news.all() for u in users]
        # 联结查询：多张表一起查询
        # 本质：把符合条件的记录查询出来做一张虚拟表
        query = News.query.join(Follow, Follow.followed_id == News.user_id).filter(
            Follow.follower_id == current_user.id)
        paginate = query.order_by(News.id.desc()).paginate(page=page, per_page=5, error_out=False)

    # 用到的表   users follows news
    # 1.current_user.id == follows.follower.id
    # 2.news.user_id == follows.followed.id

    #return render_template('main/all_news.html', ans=ans)
    #分页对象中有什么？
    #1.表示上一页页码的prev_num
    #2.表示下一页页码的next_num
    #3.表示上一页的分页对象的prev
    #4.表示下一页的分页对象的next
    #5.表示是否有上一页的has_prev
    #6.表示是否有下一页的has_next
    #7.表示总共的页数的pages
    #8.表示总共的元素数量的total_num
    #9.用来设置分页数字样式的iter_pages
    #10.用来表示当前分页的所有元素的items

    # 渲染模板，把all_news.html的所有变量替换、把python代码执行，变成一个纯静态页面
    return render_template('main/all_news.html', paginate=paginate)

# 发表文章
from .forms import PostNewsForm
from app.models import News
@main.route('/post_news', methods = ['GET', 'POST'])
@login_required
def post_news():
    form = PostNewsForm()
    if form.validate_on_submit():
        news = News()
        news.body = form.body.data
        news.private = form.private.data
        news.title = form.title.data
        news.user_id = current_user.id
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('.all_news'))
    return render_template('main/post_news.html', form=form)

# 文章 | 评论
from .forms import PostCommentForm
from app.models import Comment
from random import randint
from ..decorators import decorator_permission
from app.models import Permission
@main.route('/news', methods = ["GET","POST"])
@decorator_permission(Permission.COMMENT)
def news():
    has_form = request.args.get("has_form", default=False)
    nid = request.args.get('nid')
    if nid is None:
        abort(404)
    news = News.query.filter_by(id = nid).first()
    if news is None:
        abort(404)
    comment = news.comment.all()
    # 评论表单
    form = PostCommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.body = form.body.data
        comment.title = "{}评论{}".format(current_user.name, news.user.name)
        comment.user = current_user
        comment.news = news
        comment.color = randint(1, 4)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("main.news", nid=nid))

    return render_template("main/news.html", news = news, form = form, has_comment=has_form, comment=comment)

# 删除评论
@main.route("/delete_comment")
def delete_comment():
    cid = request.args.get("cid")
    if cid is None:
        abort(404)
    comment = Comment.query.filter_by(id=cid).first()
    nid = comment.news_id
    if current_user == comment.user or current_user.has_permission(Permission.MODE_COMMENT):
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for("main.news",nid = nid))

# 删除文章
@main.route('/delete_news')
@login_required
def delete_news():
    nid = request.args.get('nid')
    if nid is None:
        abort(404)
    news = News.query.filter_by(id = nid).first()
    if news is None:
        abort(404)
    if current_user == news.user or current_user.is_admin():
        db.session.delete(news)
        db.session.commit()
    return redirect(url_for('main.all_news'))

from app.decorators import decorator_permission
from app.models import Permission
# 关注用户
@main.route('/follow')
@decorator_permission(Permission.FOLLOW)
def follow():
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    current_user.follow(user)
    return redirect(url_for('main.user_info', id=user.id))

# 取消关注用户
@main.route('/unfollow')
@decorator_permission(Permission.FOLLOW)
def unfollow():
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)
    current_user.unfollow(user)
    return redirect(url_for('main.user_info', id=user.id))

# 查看粉丝
@main.route('/all_followers')
def all_followers():
    id = request.args.get('id')
    if id is None:
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None:
        abort(404)

    #通过反向关系followers得到的全是Follow对象
    #这些对象的特点是：followed_id都等于user.id
    #follower_id是关注user的用户的id---->follower是user对象
    afs = user.followers.all()

    users = [f.follower for f in afs]

    return render_template('main/all_followers.html', users=users)

# 所有诗词，这个函数要修改浏览器中的cookie
# make_response构造一个响应
from flask import make_response
@main.route('/set_all_news_flag')
def set_all_news_flag():
    response = make_response(redirect(url_for('.all_news')))
    response.set_cookie('follow_flag', '0', 60*60*24)
    # 返回一个字符串
    return response

# 关注诗词
@main.route('/set_follow_news_flag')
def set_follow_news_flag():
    response = make_response(redirect(url_for('.all_news')))
    response.set_cookie('follow_flag', '1', 60 * 60 * 24)
    return response







