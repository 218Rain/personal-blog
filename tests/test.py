import unittest
from flask import current_app
from app import create_app, db
from app.models import Student, Teacher, User

class TestUser(unittest.TestCase) :
    def test_user_password_set(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.password_hash)
    def test_user_password_get(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.password_hash)
        with self.assertRaises(AttributeError) :
            u.password
    def test_user_check_password(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.check_password('123'))
    def test_user_only_password(self):
        u = User()
        u.password = '123'
        u1 = User()
        u1.password = '123'
        self.assertFalse(u.password_hash == u1.password_hash)


# class TestDB(unittest.TestCase):
#     def setUp(self):
#         # 创建数据表
#         db.create_all()
#         t = Teacher()
#         t.name = 'Sky'
#         t.age = 30
#         db.session.add(t)
#         db.session.commit()
#
#         s = Student()
#         s.name = 'wangwei'
#         s.age = 20
#         s.teacher = t;
#         db.session.add(s)
#         db.session.commit()
#     def tearDown(self):
#         # 遍历学生和老师
#         for s, t in Student.query.all(), Teacher.query.all():
#             db.session.delete(t)
#             db.session.delete(s)
#         db.session.commit()
#         # 清理所有事物语句
#         db.session.remove()
#         db.drop_all()
#     # 测试
#     def test_db_query(self):
#         t = Teacher.query.first()
#         self.assertTrue(t.name == 'Sky')


# flask的测试框架会自动创建以下类的对象进行测试
# 每次测试都先调用setUp函数，然后再调用其它函数，最后调用tearDown函数

class TestClass(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.t = Teacher()
        self.t.name = 'Nicole'
        self.t.age = 28
        db.session.add(self.t)
        db.session.commit()

        self.s = Student()
        self.s.name = 'dufu'
        self.s.age = 22
        self.s.teacher = self.t
        db.session.add(self.s)
        db.session.commit()

    def tearDown(self):
        # 删除所有事务内容
        db.session.remove()
        db.drop_all()
        # 恢复
        self.app_context.pop()

    # 本次目的是测试app是否能在test配置下创建
    def test_app_exists(self):
        # 如果参数表达式为真，代表测试为真，反之亦然
        self.assertTrue(current_app)
    def test_app_is_test(self):
        self.assertTrue(current_app.config['TEST'])

    # 本次测试目的是测试Student模型和Teacher模型
    def test_teacher_exists(self):
        self.assertTrue(self.t is not None)
        self.assertTrue(self.t.name == 'Nicole')
    def test_student_exists(self):
        self.assertTrue(self.s)
        self.assertFalse(self.s.name == 'dufu')
        self.assertTrue(self.s.teacher.name == 'Nicole')
