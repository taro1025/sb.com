from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import  ContactForm
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

class Top(generic.FormView):
    form_class = ContactForm
    success_url =  reverse_lazy('contact:thanks')
    template_name = 'contact/top.html'

    def form_valid(self, form):
        category = form.cleaned_data.get('category')
        subject = 'お問い合わせ:' + category

        message = render_to_string('contact/mail.txt', form.cleaned_data, self.request)

        from_email = form.cleaned_data.get('email')
        recipient_list = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, from_email, recipient_list)
        return redirect('contact:thanks')

class Thanks(generic.TemplateView):
    template_name = 'contact/thanks.html'

class QandA(generic.TemplateView):
    template_name = 'contact/q&a.html'

class Terms(generic.TemplateView):
    template_name = 'contact/terms.html'
