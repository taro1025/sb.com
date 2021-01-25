from django.urls import path
from . import views

app_name = 'contact'

urlpatterns=[
    path('', views.Top.as_view(), name='top'),
    path('q&a/', views.QandA.as_view(), name='q&a'),
    path('thanks/', views.Thanks.as_view(), name='thanks'),
    path('terms/', views.Terms.as_view(), name='terms'),
]
