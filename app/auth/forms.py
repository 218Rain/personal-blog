from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from app.models import User
from wtforms.validators import ValidationError

class LoginForm(FlaskForm) :
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6,128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    remember_me = BooleanField(label='记住密码')
    submit = SubmitField(label='登陆')

# 只要表单验证失败就会抛出ValidationError异常
# 这个异常会被表单框架捕获
# 需要在模板中进行显示异常信息
class RegisterForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6, 128)])
    name = StringField(label='昵称', validators=[DataRequired(), Length(2, 128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    password_again = PasswordField(label='确认密码', validators=[EqualTo('password', '两次密码不一致')])
    submit = SubmitField(label='注册')

    # 唯一性验证
    def validate_email(self, field):
        user = User.query.filter_by(email = field.data).first()
        if user is not None:
            # 会被表单捕获
            raise ValidationError('邮箱已存在')