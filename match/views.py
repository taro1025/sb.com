from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from .models import User, Message, BuyingHistory, Char
from django.views import generic
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse_lazy
from .forms import LoginForm, UserCreateForm, UserUpdateForm, SendMessage, AccountUpdateForm, CreateCharForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
import stripe
from ipware import get_client_ip
stripe.api_key = settings.STRIPE_SECRET_KEY
import os

import tweepy
consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#auth.set_access_token(access_token,access_secret)
api = tweepy.API(auth)
from django.db.models import Q

import boto3
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME  # バケット名


def About(request):
    return render(request, 'match/about.html')

class Top(generic.ListView):
    model = User
    template_name = 'match/menber_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET or None)
        if form.is_valid():
            key_word = form.cleaned_data.get('key_word')
            if key_word:
                queryset = queryset.filter(
                    Q(last_name__icontains=key_word)|Q(first_name__icontains=key_word)
                    |Q(my_profile__icontains=key_word)|Q(user_char__char__icontains=key_word)
                    |Q(describe1__icontains=key_word)|Q(describe2__icontains=key_word)
                    |Q(describe3__icontains=key_word)
                    ).distinct()
            char = form.cleaned_data.get('char')
            if char:
                queryset = queryset.filter(user_char__in=char).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.get_queryset()
        context['form'] = SearchForm(self.request.GET or None)
        return context



class MenberDetail(generic.DetailView):
    #メンターの詳細プロフ
    model = User
    context_object_name = 'menber_detail'
    template_name = 'match/menber_detail.html'



class AccountUpdate(generic.UpdateView):
    model = User
    template_name = 'match/account_update.html'
    form_class = AccountUpdateForm

    def get(self, request, *args, **kwargs):
        #self.object = None
        self.object = get_object_or_404(User, pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, pk=self.kwargs['pk'])
        self.object_list = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        return self.create_account(form)

    def create_account(self, form):
        menter_pk = self.kwargs['pk']


        menter_form = form.save(commit=False)


        account = stripe.Account.create(
            country='JP',
            type='custom',
            requested_capabilities=['transfers','card_payments'],
            business_type='individual',
        )
        #print("これがアカウントID{}".format(account.id))
        account = stripe.Account.retrieve(id=account.id)
    #    print("アカウント{}".format(account))
        get_ip = get_client_ip(self.request)
        ip = get_ip[0]

        if menter_form.user_gender == 1:
            gender='male'
        else:
            gender='female'
        menter_form.user_phone_number = '+81' + str(menter_form.user_phone_number)
        account = stripe.Account.modify(
            account.id,
            individual={
                'first_name_kana':menter_form.user_first_name_kana,
                'first_name_kanji':menter_form.user_first_name_kanji,
                'last_name_kana':menter_form.user_last_name_kana,
                'last_name_kanji':menter_form.user_last_name_kanji,
                'phone':menter_form.user_phone_number,
                'gender':gender, #male or female
                'address_kanji':{
                    "country":"JP",
                    "state":menter_form.user_state_kanji,
                    "city":menter_form.user_city_kanji,
                    "town":menter_form.user_town_kanji,
                    "line1":menter_form.user_line1_kanji,
                    "line2":menter_form.user_line2_kanji,
                    "postal_code":menter_form.user_postal_code,
                },
                'address_kana':{
                    "country":"JP",
                    "state":menter_form.user_state_kana,
                    "city":menter_form.user_city_kana,
                    "town":menter_form.user_town_kana,
                    "line1":menter_form.user_line1_kana,
                    "line2":menter_form.user_line2_kana,
                    "postal_code":menter_form.user_postal_code,
                },
                'dob':{
                    "day":menter_form.user_day,
                    "month":menter_form.user_month,
                    "year":menter_form.user_year,
                },
            },
            tos_acceptance={
                'date':menter_form.user_tos_date,
                'ip': ip,
            }
        )
        account.external_accounts.create(external_account= {
            'object':'bank_account',
            'account_number': menter_form.user_account_number,
            'routing_number': menter_form.user_routing_number, #銀行コード+支店コード
            'account_holder_name':menter_form.user_holder_name,                    'currency':'jpy',
            'country':'jp',
            }
        )

        """フォームセーブ"""
        menter_form.user_account_id = account.id
        menter_form.save()

        menter = get_object_or_404(User, pk=menter_pk)

        """身分証のアップロード"""
        key1 =  str(menter.user_verification_front)
        key2 =  str(menter.user_verification_back)
        front = 'front-img'
        back = 'back-img'
        print("fgjlag{}".format(front))
        self.upload_identity(account.id, front, back, key1, key2)

        account.save()

        return redirect('match:user_detail', pk=menter_pk)

    def upload_identity(self, acct_id, img_path_front, img_path_back, key1, key2):
        s3 = boto3.client('s3')
        print("this is key1!{}".format(key1))
        #s3.Object(BUCKET_NAME,str(front_key)).download_file(str(front_key))
        a = s3.get_object(Bucket=BUCKET_NAME, Key=key1)

        with open(img_path_front,"wb") as f:
            f.write(a['Body'].read())


        #表側
        with open(img_path_front, "rb") as fp:
            res = stripe.FileUpload.create(
                purpose='identity_document',
                file=fp,
                stripe_account=acct_id
            )
            verification_id = res["id"]

            res = stripe.Account.modify(
            acct_id,
            individual = { "verification" :{
                "document":{
                "front": verification_id
                }
            }})

        os.remove(img_path_front)
        #os.remove(img_path_front)
        s3.delete_object(Bucket=BUCKET_NAME, Key=key1)



        #裏側
        b = s3.get_object(Bucket=BUCKET_NAME, Key=key2)

        with open(img_path_back,"wb") as f:
            f.write(b['Body'].read())

        with open(img_path_back, "rb") as fp:
            res = stripe.FileUpload.create(
                purpose='identity_document',
                file=fp,
                stripe_account=acct_id
            )
            verification_id = res["id"]

            res = stripe.Account.modify(
                acct_id,
                individual = { "verification" :{
                    "document":{
                    "back": verification_id
                    }
                }})
        os.remove(img_path_back)
        #os.remove(img_path_back)
        s3.delete_object(Bucket=BUCKET_NAME, Key=key2)


class Buy(generic.DetailView):
    model = User
    template_name = 'match/buy.html'
    context_object_name = 'menter'

    def post(self, request, *args, **kwargs):
        """コースフラグ、メンターのPK、トークンの準備"""
        flag = self.kwargs['num']
        menter_pk=self.kwargs['pk']
        menter = get_object_or_404(User, pk=menter_pk)
        token = request.POST['stripeToken']  # フォームでのサブミット後に自動で作られる
        #購入処理
        return self.charge(flag, menter_pk, token)

    def get_context_data(self, **kwargs):
        """STRIPE_PUBLIC_KEYを渡したいだけ"""
        context = super().get_context_data(**kwargs)
        context['publick_key'] = settings.STRIPE_PUBLIC_KEY
        context['select_course'] = self.kwargs['num']
        return context


    def charge(self, flag, menter_pk, token):
        menter = get_object_or_404(User, pk=menter_pk)
        try:
            # 購入処理
            if flag == 1:
                charge = stripe.Charge.create(
                    amount=menter.course1,
                    currency='jpy',
                    #application_fee_amount=int(menter.course1*0.1),
                    source=token,
                    description='メール:{} 選んだコース:{}円のコース'.format(self.request.user.email, menter.course1),
                    transfer_data={
                        'amount': int(menter.course1*0.9),
                        'destination': menter.user_account_id,
                    }
                )
            elif flag == 2:
                charge = stripe.Charge.create(
                    amount=menter.course2,
                    currency='jpy',
                    source=token,
                    description='メール:{} 選んだコース:{}円のコース'.format(self.request.user.email, menter.course2),
                    transfer_data={
                        'amount': int(menter.course2*0.9),
                        'destination': menter.user_account_id,
                    }
                )
            elif flag == 3:
                charge = stripe.Charge.create(
                    amount=menter.course3,
                    currency='jpy',
                    source=token,
                    description='メール:{} 選んだコース:{}円のコース'.format(self.request.user.email, menter.course3),
                    transfer_data={
                        'amount': int(menter.course3*0.9),
                        'destination': menter.user_account_id,
                    }
                )
        except stripe.error.CardError as e:
            # カード決済が上手く行かなかった(限度額超えとか)ので、メッセージと一緒に再度ページ表示
            context = self.get_context_data()
            context['message'] = 'Your payment cannot be completed. The card has been declined.'
            return render(self.request, 'match/menber_detail.html', context)
        else:
            print("lkjhbvg")
            # 上手く購入できた。Django側にも購入履歴を入れておく
            BuyingHistory.objects.create(course=menter, user=self.request.user, stripe_id=charge.id)
            return redirect('match:message_list', pk=menter_pk)


class Room(generic.ListView):
    model = User
    template_name = 'match/room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """distinctでフィールドを指定できないので代わりの処理"""
        pks = Message.objects.filter(
            to_user__pk=self.request.user.pk
            ).order_by('room').distinct()
        pklist = []
        for i in pks:
            if i.room.pk in pklist:
                continue
            pklist.append(i.room.pk)

        get_user = User.objects.in_bulk(pklist)
        users = []
        for j in get_user:
            users.append(get_user[j])

        """usersはこのメンターとやりとりしてる人たち"""
        context['users'] = users



        return context

class MessageList(generic.ListView, ModelFormMixin):
    model = Message
    form_class = SendMessage
    ordering = 'created_at'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['menter'] = get_object_or_404(User, pk=self.kwargs['pk'])
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        print(request.user.busy)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        """"メッセージの処理"""
        self.object = None
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        to_user_pk = self.kwargs['pk']

        message = form.save(commit=False)
        print("これ！{}".format(to_user_pk))
        message.room = self.request.user
        message.to_user = get_object_or_404(User, pk=to_user_pk)
        message.created_at = timezone.now()
        message.save()
        return redirect('match:message_list', pk=to_user_pk)

class Login(LoginView):
    #ログインページ
    form_class = LoginForm
    template_name = 'match/login.html'

class Logout(LogoutView):
    #ログアウトページ
    template_name = 'match/menber_list.html'


User = get_user_model()

class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'match/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
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

        subject = render_to_string('match/subject.txt', context).strip()
        message = render_to_string('match/message.txt', context)

        user.email_user(subject, message)
        return redirect('match:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'match/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'match/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            print("3")
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            print("2")
            return HttpResponseBadRequest()


        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                print("1")
                return HttpResponseBadRequest()

            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser



class OnlySuperUser(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk ==  user.is_superuser


class Refund(OnlySuperUser,generic.ListView):
    """返金処理"""
    model = User
    template_name = 'match/refund.html'


    def post(self, request, *args, **kwargs):
        id = request.POST.get('charge_id')
        refund = stripe.Refund.create(
            charge=id,
            reverse_transfer=True,
        )
        return HttpResponse("ok")

class CreateChar(OnlySuperUser, generic.CreateView):
    """adminになぜかアクセスできないからその代わり"""
    model = Char
    template_name = 'match/create_char.html'
    form_class = CreateCharForm

    def get_success_url(self):
        return resolve_url('match:create_char')

    def get_context_data(self, **kwargs):
        kwargs['char_list'] = Char.objects.all()
        return super().get_context_data(**kwargs)


def RelateTwitter(request):
        user = get_object_or_404(User, pk=request.user.pk)
        oauth_token = ''

        url = request.GET
        if 'oauth_token' in url:
            oauth_token = request.GET['oauth_token']
        if 'oauth_verifier' in url:
            oauth_verifier = request.GET.get('oauth_verifier')
        consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
        consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET



        token = request.session['request_token']
        del request.session['request_token']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.request_token = { 'oauth_token' : token,
                         'oauth_token_secret' : oauth_verifier }

        auth.get_access_token(oauth_verifier)


        api = tweepy.API(auth)

        twitter = api.me()
        user.user_img = twitter.profile_image_url_https
        user.twitter_url = 'https://twitter.com/'+twitter.screen_name
        user.geted = True
        user.save()
        return redirect('match:top')

def Withdrawal(request):
    """退会処理"""
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save()

        return render(request, 'match/complete_withdrawal.html')

    return render(request, 'match/withdrawal.html')

class UserDetail(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'match/user_detail.html'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, pk=self.request.user.pk)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        if 'request_token' in self.request.session:
            del self.request.session['request_token']
        if user.geted == False:
            re_url = auth.get_authorization_url()
            kwargs['re_url'] = re_url
            self.request.session['request_token'] = auth.request_token['oauth_token']
            return super().get_context_data(**kwargs)
        else:
            kwargs['re_url'] = None
            return super().get_context_data(**kwargs)


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'match/user_form.html'



    def get_success_url(self):
        return resolve_url('match:user_detail', pk=self.kwargs['pk'])
