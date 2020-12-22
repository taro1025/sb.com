from django.urls import path
from . import views

app_name = 'match'

urlpatterns=[

    path('menber_detail/<int:pk>/', views.MenberDetail.as_view(), name='menber_detail'),
    path('login/',views.Login.as_view(), name='login'),
    path('logout/',views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('message/<int:pk>/', views.MessageList.as_view(), name='message_list'),
    path('message/<int:pk>/<int:num>/', views.Buy.as_view(), name='buy'),
    path('account/<int:pk>/', views.AccountUpdate.as_view(), name='account_update'),
    path('refund/', views.Refund.as_view(), name='refund'),
    #path('select_course/<int:pk>/', views.CourseList.as_view(), name='course_list'),
    path('', views.Top.as_view(), name='top'),
]
