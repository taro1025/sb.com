from django import forms

from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from django.contrib.auth import get_user_model
from .models import Message, Char
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()
#ModelMultipleChoiceField

class PrivateForm(forms.Form):
    user_account_number = forms.CharField(label='口座番号', max_length=128)
    user_routing_number = forms.CharField(label='銀行コード＋支店コード', max_length=128)
    user_holder_name = forms.CharField(label='口座名義', max_length=32)


    user_postal_code = forms.CharField(label='郵便番号', max_length=128)

    user_state_kana = forms.CharField(label='都道府県（カナ）', max_length=32)
    user_city_kana = forms.CharField(label='区市町村（カナ）', max_length=32)
    user_town_kana = forms.CharField(label='町名（カナ）', max_length=32)
    user_line1_kana = forms.CharField(label='番地、号（カナ）', max_length=32)
    user_line2_kana = forms.CharField(label='建物・部屋番号・その他（任意）（カナ）', max_length=32, required=False)

    user_state_kanji = forms.CharField(label='都道府県（漢字）', max_length=32)
    user_city_kanji = forms.CharField(label='区市町村（漢字）', max_length=32)
    user_town_kanji = forms.CharField(label='町名（漢字）', max_length=32)
    user_line1_kanji = forms.CharField(label='番地、号（漢字）', max_length=32)
    user_line2_kanji = forms.CharField(label='建物・部屋番号・その他（任意）（漢字）', max_length=32, required=False)

    user_day = forms.IntegerField(label='生年月日（日）')
    user_month = forms.IntegerField(label='生年月日（月）')
    user_year = forms.IntegerField(label='生年月日（年）')

    user_phone_number = forms.CharField(label='電話番号', max_length=128)
    #user_tos_date = forms.DateTimeField(label='タイムスタンプ', initial=timezone.now, required=False)

    GENDER = (
        (1, '男'),
        (2, '女'),
    )

    user_last_name_kanji = forms.CharField(label='性（漢字）', max_length=32)
    user_last_name_kana = forms.CharField(label='性（かな）', max_length=32)
    user_first_name_kanji = forms.CharField(label='名（漢字）', max_length=32)
    user_first_name_kana = forms.CharField(label='名（かな）', max_length=32)
    user_gender = forms.ChoiceField(label='性別', widget=forms.RadioSelect, choices=GENDER)
    user_verification_front = forms.ImageField(label='本人確認（表）')
    user_verification_back = forms.ImageField(label='本人確認（裏）')

class SearchForm(forms.Form):
    key_word = forms.CharField(
        label='キーワード', required=False,
        widget=forms.TextInput(attrs={'class':'form-control'})
        )
    char = forms.ModelMultipleChoiceField(
        label='キャラの選択',required=False,
        queryset=Char.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-control'})
        )


class CreateCharForm(forms.ModelForm):
    class Meta:
        model = Char
        fields = ('char',)

class SendMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text',)

class LoginForm(AuthenticationForm):
    #ログインフォーム

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

"""
class AccountUpdateForm(forms.ModelForm):

     class Meta:
        model = User
        fields = (
            'user_account_number','user_routing_number','user_holder_name',
            'user_postal_code', 'user_state_kana','user_state_kanji','user_city_kana', 'user_city_kanji','user_town_kana','user_town_kanji','user_line1_kana','user_line1_kanji', 'user_line2_kana','user_line2_kanji',
            'user_day','user_month','user_year','user_phone_number','user_last_name_kana','user_last_name_kanji','user_first_name_kana','user_first_name_kanji','user_gender', 'user_verification_front','user_verification_back'
            )
"""
class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class UserUpdateForm(forms.ModelForm):

    template = """コースの内容, コースを終える基準, コース履行中の連絡手段など"""


    describe1 = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': template
    }))
    describe2 = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': template
    }))
    describe3 = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': template
    }))



    class Meta:
        model = User
        fields = ('last_name','first_name','my_profile','user_char','user_img','menter','course1','course2','course3','describe1','describe2','describe3','busy')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


    def clean(self):
        cd = self.cleaned_data

        course1 = cd.get('course1')
        course2 = cd.get('course2')
        course3 = cd.get('course3')

        if course1:
            if course1 < 3000:
                raise ValidationError("料金は3000円以上です。")
        if course2:
            if course2 < 3000:
                raise ValidationError("料金は3000円以上です。")
        if course3:
            if course3 < 3000:
                raise ValidationError("料金は3000円以上です。")

        return cd
