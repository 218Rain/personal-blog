# 导入蓝本类
from flask import Blueprint
main = Blueprint('main', __name__)

# 导入views,errors模块
from . import views, errors
