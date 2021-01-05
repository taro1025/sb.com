from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

class Char(models.Model):
    char = models.CharField('キャラ',max_length=255)

    def __str__(self):
        return self.char



class Message(models.Model):
    text = models.TextField('メッセージ')
    room = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='メッセージの持ち主',blank=True, null=True,related_name='room')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='メッセージの宛先',blank=True, null=True,related_name='to_user')
    created_at = models.DateTimeField('送信日時間', default=timezone.now, blank=True)



class BuyingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='購入者', related_name='buyer')
    course = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='メッセージの宛先', related_name='course')
    stripe_id = models.CharField('タイトル', max_length=200)
    created_at = models.DateTimeField('日付', default=timezone.now)

    def __str__(self):
        return '{} {} {}'.format(self.user, self.course)

class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
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
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)

    MENTER = (
        (1, 'メンター'),
        (2, '弟子'),
    )



    my_profile = models.TextField('自己紹介',blank=True, null=True)
    user_img = models.ImageField('プロフ画像',  blank=True)
    user_char = models.ManyToManyField(Char, verbose_name='使用キャラ', blank=True)
    menter = models.IntegerField('会員形式', default=0, choices=MENTER)
    #以下はメンターが入力する項目
    course1 = models.IntegerField('コース1', blank=True, null=True)
    course2 = models.IntegerField('コース2', blank=True, null=True)
    course3 = models.IntegerField('コース3', blank=True, null=True)

    describe_text="""(以下はテンプレートです。)
    ・値段

    ・コースの内容
    （対戦してフィードバックする、リプレイを送ってもらってフィードバックする、
    質問をする権利を○日まで与える。。。などコース内容は自由に決めても良いですが、
    永久コンサル、戦闘力〇〇まで上げる等はトラブルの元になりやすいのでなるべくお控えください。）


    ・コースを終える基準（〜日まで、○回戦するまで、○本のリプレイを送ってもらうまで、等。
    明確な終了条件を設けるようにお願いします。）"""

    describe1 = models.TextField('コース1の説明' ,blank=True, default=describe_text)
    describe2 = models.TextField('コース2の説明', blank=True, default=describe_text)
    describe3 = models.TextField('コース3の説明', blank=True, default=describe_text)

    busy = models.BooleanField('忙しい', default=True)
    #決済に使う情報
    user_account_id = models.CharField('決済に使うID', max_length=255, blank=True, null=True)

    """with twitter api"""
    twitter_url = models.CharField('ツイッターのURL', max_length=255, null=True)
    user_img = models.ImageField('プロフ画像',  blank=True)
    geted = models.BooleanField('認証住み', default=False)

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
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email
