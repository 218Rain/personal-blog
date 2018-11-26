# 前端框架Bootstrap
from flask_bootstrap import Bootstrap
# 能够将utc时间渲染成当地时间
from flask_moment import Moment
#邮件
from flask_mail import Mail, Message
from flask import Flask
# 数据库
from flask_sqlalchemy import SQLAlchemy
# 导入配置：导入config.py中的config字典
from config import config

# 变量名不能改变
bootstrap = Bootstrap()
moment = Moment()


# 创建login_manager对象：login_manager通过操作session来控制用户的登陆状态
# 通过session的判断来决定用户能够访问的视图函数
from flask_login import LoginManager
login_manager = LoginManager()
# strong，Flask-Login记录客户端IP地址和浏览器的用户代理信息，有异动就退出登录
login_manager.session_protection = 'strong'
# 指定登陆路由，在蓝本auth中的login，访问登陆后才能访问的页面时候重定向的auth.login
login_manager.login_view = 'auth.login'




mail = Mail()
# 访问数据库
db = SQLAlchemy()

# 设置匿名用户类，当匿名访问时，login_manager会创建Anonymouser类型的对象
# current_user会代理这个匿名用户对象
# 导入app/models.py中AnonymousUser类（匿名用户类）
from app.models import AnonymousUser
login_manager.anonymous_user = AnonymousUser

# 提供一个创建app的函数
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 绑定app
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝本
    # 在此可以注册蓝本：使项目变的简单
    # mian蓝本，一个app可以包含多个蓝本，每个蓝本实现不同的功能
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .manager import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')

    return app


