from django import forms


class ContactForm(forms.Form):

    name = forms.CharField(
        label='お名前', max_length=50,
        required=False, help_text='※任意'
    )

    email = forms.EmailField(
        label = 'メールアドレス', required=False, help_text='※任意'
    )

    text = forms.CharField(
        label='お問い合わせ内容', widget=forms.Textarea
        )

    category = forms.CharField(
        label='件名', required=False, max_length=100, help_text='※任意'
        )
