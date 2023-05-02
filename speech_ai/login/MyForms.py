from django import forms


# from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    MY_CHOICES = (
        ('0', '普通用户'),
        ('1', '裁判'),
        # ('2', '管理员'),
    )
    flag = forms.ChoiceField(widget=forms.RadioSelect(attrs={'id': 'MyRadio'}), choices=MY_CHOICES)
    username = forms.CharField(label="用户名", max_length=128,
                               widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "用户名"}))
    password = forms.CharField(label="密码", max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': "密码"}))
    # captcha = CaptchaField(label='验证码')


class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128,
                               widget=forms.TextInput(attrs={'class': 'input', 'placeholder': "用户名"}))
    password = forms.CharField(label="密码", max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': "密码"}))
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': "确认密码"}))
    email = forms.CharField(label="邮箱地址", max_length=256,
                            widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': "邮箱"}))
    # captcha = CaptchaField(label='验证码')
