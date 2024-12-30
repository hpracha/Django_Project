from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('balance_inquiry/', views.balance_inquiry_view, name='balance_inquiry'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('fund_transfer/', views.fund_transfer_view, name='fund_transfer'),
    path('account_info/', views.account_info_view, name='account_info'),
    path('user_update/', views.user_update_view, name='user_update'),
    path('delete_user/', views.delete_user_view, name='delete_user'),
    path('logout/', views.logout_view, name='logout'),
    path('recent_transactions/', views.recent_transactions_view, name='recent_transactions'),


]
