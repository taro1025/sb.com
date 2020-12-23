from django import forms

from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from django.contrib.auth import get_user_model
from .models import Message, Char

User = get_user_model()

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

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'user_account_number','user_routing_number','user_holder_name',
            'user_postal_code', 'user_state_kana','user_state_kanji','user_city_kana', 'user_city_kanji','user_town_kana','user_town_kanji','user_line1_kana','user_line1_kanji', 'user_line2_kana','user_line2_kanji',
            'user_day','user_month','user_year','user_phone_number','user_last_name_kana','user_last_name_kanji','user_first_name_kana','user_first_name_kanji','user_gender', 'user_verification_front','user_verification_back'
            )

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

    class Meta:
        model = User
        fields = ('last_name','first_name', 'email','user_char','user_img','menter','course1','course2','course3','describe1','describe2','describe3','busy')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
