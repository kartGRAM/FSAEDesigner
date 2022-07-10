from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os
from django.conf import settings
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
import secrets
import glob


class CustomUserManager(UserManager):
    # ユーザーマネージャー
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # ユーザー名（Emailアドレスを使用する）
    email = models.EmailField(_('email address'), unique=True)

    # アバター
    def get_avatar_path(self, filename):
        dir = self.get_public_dir(abs=False)+'avatar/'
        name = self.id
        extension = os.path.splitext(filename)[-1]
        return dir + str(name) + extension
    avatar = ProcessedImageField(upload_to=get_avatar_path,
                                 processors=[ResizeToFill(120, 120)],
                                 format='png',
                                 options={'quality': 100})

    # 通知設定
    push_by_email = models.BooleanField(
        default=False,
        verbose_name=_("Eメールでのpush通知を受け取る"),
    )
    push_by_browser = models.BooleanField(
        default=False,
        verbose_name=_("ブラウザでのpush通知を受け取る"),
    )

    # 非公開オブジェクトの格納フォルダのハッシュ値
    private_dir_hash = models.CharField(
        blank=True, max_length=16,
        verbose_name=_('フォルダ名'),
        help_text=_('フォルダ')
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    # ユーザーの追加日時
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # カスタムマネージャー
    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def clean(self, *args, **kwargs):
        """
        if self.favorites.count() > 10:
            raise ValidationError(f"登録可能な個数は{MAXFAVORITES}です。")
        """
        super().clean(*args, **kwargs)

    def get_public_dir(self, abs=False):
        root = ""
        if abs:
            root = settings.MEDIA_ROOT.replace(os.sep, '/') + "/"

        dir = f"{root}public/{self.id}/"
        if abs and not os.path.exists(dir):
            os.mkdir(dir)
        return dir

    def get_private_dir(self, abs=False):
        if self.dir_hash == "":
            self.dir_hash = secrets.token_urlsafe(16)
            self.save()
        root = ""
        if abs:
            root = settings.MEDIA_ROOT.replace(os.sep, '/') + "/"

        dir = f"{root}private/{self.dir_hash}/"
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir

    @ property
    def username(self):
        return self.email

class GeometryDesignerFile(models.Model):
    def get_image_path(self, filename):
        prefix = 'geometry-designer-data/' + str(self.user.id) + "-"
        root = settings.MEDIA_ROOT.replace(os.sep, '/') + "/"
        print(root+prefix)
        folders = glob.glob(root+prefix+"??????????????????????")
        if len(folders) > 0:
            dir_hash = folders[0].split("-")[-1]
            print(dir_hash)
        else:
            dir_hash = secrets.token_urlsafe(16)
        prefix = prefix + dir_hash + "/"
        if not os.path.exists(root+prefix):
            os.mkdir(root + prefix)
        return prefix + filename

        prefix = "robot_log/" + str(self.id)+"-"
        root = settings.MEDIA_ROOT.replace(os.sep, '/') + "/"
        if self.dir_hash == "":
            folders = glob.glob(root+prefix+"????????????????")
            if len(folders) > 0:
                self.dir_hash = folders[0].split("-")[-1]
            else:
                self.dir_hash = secrets.token_urlsafe(16)
            self.save()
        prefix = prefix + self.dir_hash + "/"
        if not os.path.exists(root+prefix):
            os.mkdir(root + prefix)
        return prefix

    name = models.CharField(verbose_name="name",max_length=256)
    note = models.CharField(verbose_name="note",max_length=1024*4,blank=True)

    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )

    # 公開するか
    is_public= models.BooleanField(
        _('public'),
        default=False,
    )

    # サムネイル
    thumbnail = ProcessedImageField(upload_to=get_image_path,
                                 processors=[ResizeToFill(512, 512)],
                                 format='png',
                                 blank=True,
                                 options={'quality': 100})
    # JSONの中身(ファイル本体)
    content = models.TextField(verbose_name="content")
    # 作成日時
    created = models.DateTimeField(_('created'), default=timezone.now)
    # 更新日時
    lastUpdated = models.DateTimeField(_('last updated'), default=timezone.now)

    class Meta:
        verbose_name = _('GeometryDesignerFile')
        verbose_name_plural = _('GeometryDesignerFile')

    def clean(self, *args, **kwargs):
        """
        if self.favorites.count() > 10:
            raise ValidationError(f"登録可能な個数は{MAXFAVORITES}です。")
        """
        super().clean(*args, **kwargs)
