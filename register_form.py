
from wtforms import Form, BooleanField, StringField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('用户名：', [validators.Length(min=4, max=128)])
    region = StringField('地区：', [validators.Length(min=0, max=128)])
    password = PasswordField('新密码：', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='两次输入的密码必须一致')
    ])
    confirm = PasswordField('再次输入密码：')
    accept_tos = BooleanField('我接受协议', [validators.DataRequired()])
