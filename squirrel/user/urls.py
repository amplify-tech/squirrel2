from django.urls import path
from . import views

urlpatterns = [
    path('<user_id>', views.dashboard, name='dashboard'),
    path('<user_id>/chat/<ricvr_id>', views.chat, name='chat'),
    path('<user_id>/myfrnd', views.myfrnd, name='myfrnd'),
    path('<user_id>/findfrnd', views.findfrnd, name='findfrnd'),
    path('<user_id>/send_msz/', views.send_msz, name='send_msz'),
    path('<user_id>/check_msz/', views.check_msz, name='check_msz'),
    path('<user_id>/saveprofile/', views.saveprofile, name='saveprofile'),
    path('<user_id>/update_pic/', views.update_pic, name='update_pic'),
    path('<user_id>/update_status/', views.update_status, name='update_status'),
    path('<user_id>/following/', views.following, name='following'),
    path('<user_id>/likes/', views.likes, name='likes'),
    path('<user_id>/makeprivate/', views.makeprivate, name='makeprivate'),
    path('<user_id>/find_all_liker/', views.find_all_liker, name='find_all_liker'),
    path('<user_id>/del_status/', views.del_status, name='del_status'),
    path('<user_id>/del_prof_pic/', views.del_prof_pic, name='del_prof_pic'),
    path('<user_id>/chat_del/<ricvr_id>', views.chat_del, name='chat_del'),
    path('<user_id>/prof_del/', views.prof_del, name='prof_del'),
    path('<user_id>/delete_flwing/', views.delete_flwing, name='delete_flwing'),
    path('<user_id>/delete_flwer/', views.delete_flwer, name='delete_flwer'),
    path('<user_id>/viewprofile/<ricvr_id>', views.viewprofile, name='viewprofile'),
]