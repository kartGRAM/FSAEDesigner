from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import redirect, resolve_url
from django.template.loader import render_to_string
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetConfirmView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import (
    LoginForm, PasswordResetForm, SetPasswordForm, UserCreateForm,
)
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
User = get_user_model()

class CommonMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["title"] = self.title
        except:
            pass
        return context

class ParentUserTestMixin(UserPassesTestMixin):
    def test_model(self, TestModel):
        user = self.request.user
        try:
            instance = None
            if user.is_superuser:
                instance = TestModel.objects.get(id=self.kwargs['pk'])
            else:
                instance = TestModel.objects.get(
                    user=user, id=self.kwargs['pk'])
            if instance is not None:
                return True
        except:
            return False

class Login(CommonMixin, LoginView):
    # ログインページ
    title = _("ログイン")
    form_class = LoginForm
    template_name = 'FSAEDesigner/login.html'

    def post(self, request, *args, **kwargs):
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return super().post(request, *args, **kwargs)

class Logout(LogoutView):
    # ログアウトページ
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _("ログアウトしました"))
        return super().dispatch(request, *args, **kwargs)

class PasswordReset(SuccessMessageMixin, PasswordResetView):
    # パスワード変更用URLの送付ページ
    subject_template_name = 'FSAEDesigner/mail_template/password_reset/subject.txt'
    email_template_name = 'FSAEDesigner/mail_template/password_reset/message.txt'
    template_name = 'FSAEDesigner/password_reset_form.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('FSAEDesigner:password_reset')
    success_message = _("メールを送信しました")

class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    # 新パスワード入力ページ
    form_class = SetPasswordForm
    template_name = 'FSAEDesigner/password_reset_confirm.html'
    success_url = reverse_lazy('FSAEDesigner:login')
    success_message = _("パスワードが変更されました")

class UserCreate(CommonMixin, SuccessMessageMixin, generic.CreateView):
    title = "新規登録"
    # ユーザー仮登録
    template_name = 'FSAEDesigner/user_create.html'
    success_url = reverse_lazy('FSAEDesigner:user_create')
    success_message = _("登録用メールを送信しました")
    form_class = UserCreateForm

    def form_valid(self, form):
        # 仮登録と本登録用メールの発行.
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string(
            'FSAEDesigner/mail_template/create/subject.txt', context)
        message = render_to_string(
            'FSAEDesigner/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return super().form_valid(form)

def UserCreateComplete(request, token):

    timeout_seconds = getattr(
        settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  #1日以内

    # tokenが正しければ本登録.
    try:
        user_pk = loads(token, max_age=timeout_seconds)

    # 期限切れ
    except SignatureExpired:
        return HttpResponseBadRequest()

    # tokenが間違っている
    except BadSignature:
        return HttpResponseBadRequest()

    # tokenは問題なし
    else:
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not user.is_active:
                # 問題なければ本登録とする
                user.is_active = True
                user.save()
                messages.success(request, _("登録が完了しました"))
                #ログイン画面へリダイレクト
                return redirect('FSAEDesigner:login')

        return HttpResponseBadRequest()

@login_required
def EmailChangeComplete(request, token):
    """メールアドレスが変更されたらログインページへリダイレクトする"""
    timeout_seconds = getattr(
        settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*1)  # デフォルトでは1日以内

    try:
        new_email = loads(token, max_age=timeout_seconds)

    # 期限切れ
    except SignatureExpired:
        return HttpResponseBadRequest()

    # tokenが間違っている
    except BadSignature:
        return HttpResponseBadRequest()

    # tokenは問題なし
    else:
        User.objects.filter(email=new_email, is_active=False).delete()
        request.user.email = new_email
        request.user.save()
        messages.success(request, _("メールアドレスが変更されました"))
        return redirect('FSAEDesigner:login')

class Top(CommonMixin, LoginRequiredMixin, generic.TemplateView):
    title = _("")
    template_name = 'FSAEDesigner/top.html'
    """
    def get(self, request, *args, **kwargs):
        self.url = reverse_lazy('FSAEDesigner:top')
        return super().get(request, *args, **kwargs)
    """
