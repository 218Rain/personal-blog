from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import TextAreaField

# 用户修改资料类
class EditUserForm(FlaskForm):
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(1, 128)])
    name = StringField(label='昵称', validators=[DataRequired(), Length(1, 128)])
    location = StringField(label='位置', validators=[DataRequired(), Length(1, 64)])
    about_me = TextAreaField(label='签名', validators=[DataRequired(), Length(1, 256)])
    password = PasswordField(label='密码')
    password_again= PasswordField(label='确认密码', validators=[EqualTo('password', '两次密码不一致')])
    submit = SubmitField(label='确认编辑')

# 管理员资料修改
class PostNewsForm(FlaskForm):
    title = StringField(label='标题', validators=[DataRequired(), Length(1, 128)])
    body = TextAreaField(label='正文', validators=[DataRequired()])
    private = BooleanField(label='私有', default=False)
    submit = SubmitField(label='发表')

# 发表评论
class PostCommentForm(FlaskForm):
    body = TextAreaField(label="", validators=[DataRequired()])
    submit = SubmitField(label="发表")

