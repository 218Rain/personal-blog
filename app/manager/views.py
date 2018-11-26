from flask import render_template, url_for, redirect, flash, request
from app import db
from . import manager
from app.decorators import decorator_admin, decorator_permission
from app.models import Permission
from .forms import EditUserForm
from flask import abort
from app.models import User

# 管理员编辑个人信息
@manager.route('/edit_user', methods=['GET', 'POST'])
@decorator_admin
def edit_user() :
    id = request.args.get('id')
    if id is None :
        abort(404)
    user = User.query.filter_by(id=id).first()
    if user is None :
        abort(404)

    form = EditUserForm()
    if form.validate_on_submit() :
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.location = form.location.data
        user.role_id = form.role_id.data
        user.about_me = form.about_me.data
        if len(form.password.data) != 0 :
            user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.user_info', id=user.id))

    form.name.data = user.name
    form.email.data = user.email
    form.location.data = user.location
    form.role_id.data = user.role_id
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    return render_template('manager/edit_user.html', form=form)

# 管理员主页
@manager.route('/index')
@decorator_admin
def index() :
    return 'i am admin'

@manager.route('/manager_comment')
@decorator_permission(Permission.MODE_COMMENT)
def manager_comment() :
    return 'i am moderator or admin'