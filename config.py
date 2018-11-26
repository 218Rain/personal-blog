class Config():
    # 表单配置
    WTF_CSRF_ENDABLE = True
    SECRET_KEY = 'ios.Rain.com'

    # 邮箱配置
    MAIL_SERVER = 'smtp.163.com'
    MAIL_ROPT = '25'
    MAIL_USE_TLS = True
    MAIL_USERNAME = '15133319929@163.com'  #发送邮箱账号
    MAIL_PASSWORD = 'hhsjbbdz218'   # 授权码

    # 数据库配置：可以设置True来启用在每个请求中自动提交数据库更改
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭状态

# 开发阶段下的数据库：开发
class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@172.25.1.7/develop_db'

# 测试模式下的数据库：测试
class TestConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@172.25.8.96/test_db'

# 上线产品阶段数据库：运维
class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@172.25.8.96/product_db'

config = {
    'develop':DevelopConfig,
    'test':TestConfig,
    'product':ProductConfig,
    'default':DevelopConfig
}