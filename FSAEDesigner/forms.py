import django.contrib.auth.forms as auth
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginForm(auth.AuthenticationForm):
    # ログインフォーム

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            # placeholderにフィールドのラベルを入れる
            field.widget.attrs['placeholder'] = field.label


class PasswordResetForm(auth.PasswordResetForm):
    # パスワード忘れたときのフォーム
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class SetPasswordForm(auth.SetPasswordForm):
    # パスワード再設定用フォーム(パスワード忘れて再設定)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(auth.UserCreationForm):
    # ユーザー登録用フォーム
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
