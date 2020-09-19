
from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    username = StringField('用户名：', [validators.Length(min=4, max=128)])
    password = PasswordField('密码：', [
        validators.DataRequired()
    ])
