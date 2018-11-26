from app import db
from datetime import datetime

#写个例子来说明多对多
#多对多需要关系表实现
rel_table = db.Table('rel_table', \
                     db.Column('sid', db.Integer, db.ForeignKey('stus.id')),\
                     db.Column('cid', db.Integer, db.ForeignKey('clas.id')))
class Stu(db.Model) :
    __tablename__ = 'stus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    #多对多的反向关系
    #db.backref('students', lazy='dynamic') 代表添加到目标类中的字段students是一个query
    classes = db.relationship('Cla', secondary=rel_table, \
                              backref=db.backref('students', lazy='dynamic'), \
                              lazy='dynamic')
class Cla(db.Model) :
    __tablename__ = 'clas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


# 权限类
class Permission(object):
    FOLLOW = 0x01   # 发评论权限
    WRITE = 0x02    # 发博客权限
    COMMENT = 0x04  # 关注其他博主
    MODE_COMMENT = 0x08 # 管理博客
    ADMIN = 0x80    # 管理员，所有权限

# 角色模型
class Role(db.Model):# id在Model类中,为父类添加属性
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='role')

    # 创建角色
    @staticmethod
    def create_roles():
        roles = {
            # 普通用户
            'user': [Permission.FOLLOW | Permission.WRITE | Permission.COMMENT, True],
            # 协管员
            'moderator': [Permission.FOLLOW | Permission.WRITE | Permission.COMMENT | Permission.MODE_COMMENT, False],
            # 管理员
            'admin': [0xff, False]
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role()
                role.name = r
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default='libai')
    age = db.Column(db.Integer, default=20)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default='Rain')
    age = db.Column(db.Integer, default=30)
    # lazy='dynamic' 代表访问students的时候返回的是一个query，可以进一步过滤
    # 如果没有lazy='dynamic'则访问students的时候返回的是一个列表
    students = db.relationship('Student', backref='teacher', lazy='dynamic')





# 多对多时需要一个关系表
class Follow(db.Model):
    # 关注者的ID
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # 被关注者ID
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # 关注的时间
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# User用户模型
# Flask_login是专门用来管理用户认证系统中的认证状态。可以做到储存在会话中的活跃状态，实现轻松摩纳哥登录退出
# 可以让你限制未登录的用户访问某些页面，处理‘记住我’的功能
from flask_login import UserMixin
# 在用户模型中添加生成token和验证token的功能，导入JWS
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# generate_password_hash：密码生成函数：是一个密码加盐哈希函数
# check_password_hash：生成的哈希值可通过此进行验证
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    name = db.Column(db.String(128), default='李清照')
    password_hash = db.Column(db.String(128))
    # 外键，角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 为用户做邮箱激活
    confirmed = db.Column(db.Boolean, default=False)
    # 自我介绍
    about_me = db.Column(db.Text)
    # 地址
    location = db.Column(db.String(64))
    # 注册时间，register_time存放的都是修改表（数据库迁移）的时间，存放的是创建User对象的时间
    register_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 访问时间
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 评论
    comment = db.relationship("Comment", backref="user", lazy="dynamic")

    # ----------------- 用于邮箱验证 --------------------------
    def generate_confirmed_token(self):
        # 生成令牌
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], expires_in=120)
        # 用户id加密，生成加密串
        token = s.dumps({'id': self.id})
        return token
    def confirm(self, token):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        try:
            # token超时异常，解密
            d = s.loads(token)
        except:
            return False

        if d.get('id') == self.id:
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False


    def __str__(self):
        return str(self.id) + ':' + self.name

    # 构建一个属性：隐藏细节，截获它
    @property
    def password(self):
        # 密码不能被读取，否则抛出异常
        raise AttributeError('不能读取密码')
    @password.setter
    def password(self, password):
        # 利用sha256+杂质串的方法产生hash方法
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        # 验证密码是否正确：password_hash：生成的哈希字符串
        # password：需要验证的明文密码
        return check_password_hash(self.password_hash, password)

    # ----------------- 实现权限认证方法 --------------------------
    def has_permission(self, permission):
        return self.role.permissions & permission == permission
    def is_admin(self):
        return self.has_permission(0xff)

    # 更新用户访问的时间，在用户访问任何页面的时候调用
    def flush_access_time(self):
        self.access_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    news = db.relationship('News', backref = 'user', lazy = 'dynamic')

    # 粉丝们
    followers = db.relationship('Follow', \
                                foreign_keys=[Follow.followed_id], \
                                backref=db.backref('followed', lazy='joined'), \
                                lazy='dynamic', \
                                cascade='all, delete-orphan')
    # 大V们
    followeds = db.relationship('Follow', \
                                foreign_keys=[Follow.follower_id], \
                                backref=db.backref('follower', lazy='joined'), \
                                lazy='dynamic', \
                                cascade='all, delete-orphan')

    # 用来关注其他用户的函数
    def follow(self, user):
        if self.if_follower_of(user) == False:
            f = Follow()
            # f.follower_id = self.id
            # f.followed_id = user.id

            # self.followeds.append(user)

            f.followed = user
            f.follower = self

            db.session.add(f)
            db.session.commit()

    # 取消关注
    def unfollow(self, user):
        if self.if_follower_of(user):
            f = self.followeds.filter_by(followed_id=user.id).first()
            db.session.delete(f)
            db.session.commit()

    # 判断自己是不是user的粉丝
    def if_follower_of(self, user):
        # Follow.query.filter_by(followed_id=user.id).filter_by(follower_id=self.id).first()
        # self.followeds.filter_by(followed_id=user.id).first()
        # self.followeds.fiter_by(followed=user).first()
        return self.followeds.filter_by(followed_id=user.id).first() is not None

    # 判断自己是不是user的大微
    def if_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None


# 匿名用户类，当一个没有登录的用户访问时，那么login_manager会创建一个匿名用户对象
# current_user会代理这个匿名用户
from flask_login import AnonymousUserMixin
class AnonymousUser(AnonymousUserMixin):
    name = '游客'
    def has_permission(self, permission):
        return False
    def is_admin(self):
        return False
    def flush_access_time(self):
        pass

# 在模型中添加回调函数
# 以接收以Unicode字符串表示的用户标识符，在logout_user中调用。获取用户后会把该用户设置为匿名用户
from app import login_manager
@login_manager.user_loader
def user_load(id):
    return User.query.get(int(id))

# 诗词类
class News(db.Model) :
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    private = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.relationship("Comment", backref="news", lazy="dynamic")

# 评论类
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.Integer)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    news_id = db.Column(db.Integer,db.ForeignKey("news.id"))



