import re
from wtforms import Form, BooleanField, StringField, PasswordField, validators, FileField


class RegistrationForm(Form):
    username = StringField(u'用户名：', [validators.Length(min=4, max=128)])
    region = StringField(u'地区：', [validators.Length(min=0, max=128)])
    password = PasswordField(u'新密码：', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message=u'两次输入的密码必须一致')
    ])
    confirm = PasswordField(u'再次输入密码：')
    accept_tos = BooleanField(u'我接受协议', [validators.DataRequired()])

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)
            print(field.data)
