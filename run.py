# python虚拟环境
# 意义：不怕被损坏，每个项目一个虚拟环境，使每个项目之间不会受到影响

# 实现步骤：
#   1、制作pyhton虚拟环境
#       * 创建一个文件夹 vevn
#       * python -m venv venv
#   2、每次包装的时候要装到虚拟环境中
#       * vene\Scripts\pip.exe install flask-wtf    ...
#   3、每次装包完成后都要生成需求文件
#       * venv\Scripts\pip.exe freeze > requirements.txt

# 开发中venv中的虚拟环境被损坏，修复步骤：
#   1、删掉venv中的所有文件
#   2、重新创建python虚拟环境
#       * python -m venv venv
#   3、安装原来项目需要的包
#       * venv\Scripts\pip.exe install -r requirements.txt
#   4、成功恢复python虚拟环境

# 蓝本：本质就是一个包，通常一个app包中包含多个蓝本
# 意义：可以把不同功能的代码分别写到不同蓝本中，减少代码耦合性，便于合作。

# 导入app/__init__.py下create_app函数
from app import create_app
from app import db
# flask_script包含一个运行开发用的服务器，一个定制的Python shell，设置数据库的脚本，及其他运行在Web应用之外的命令行任务；使得脚本和系统分开。
from flask_script import Manager, Shell
# 导入app/models.py下Student类、Teacher类、User类（创建三个表）
from app.models import Student, Teacher, User
import pymysql
# 创建数据库相应模块
from flask_migrate import Migrate, MigrateCommand

pymysql.install_as_MySQLdb()
app = create_app('develop')

# 必须在app之后
manager = Manager(app)
migrate = Migrate(app, db)  # 创建一个数据库迁移对象（修改表）
manager.add_command('db', MigrateCommand)   # 增加一条命令叫做db
# 输入库迁移具体步骤：
# 1、创建数据库迁移需要的目录和脚本文件
#       venv\Scripts\python.exe run.py db init
# 2、统计数据模型和表之间的区别
#       venv\Scripts\python.exe run.py db migrate
# 3、第二步统计到的区别更新数据库（修改表）
#       venv\Scripts\python.exe run.py db upgrade


def make_context():
    return dict(Student=Student, Techer=Teacher, db=db, User=User)
manager.add_command('shell', Shell(make_context=make_context))

# 测试单元
@manager.command
def test():
    import unittest
    t = unittest.TestLoader()
    t = t.discover('tests')
    unittest.TextTestRunner().run(t)

# 导入app/models.py的Role类（角色类）
from app.models import Role
@manager.command
def init() :
    # 执行创建角色
    Role.create_roles()

manager.run()

#app.run(debug = True)