from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('upload',views.upload,name='upload'),
    path('like_post',views.like_post,name='like_post'),
    path('post_list_post',views.post_list_post,name='post_list_post'),
    path('follow',views.follow,name='follow'),
    path('post_list_suggestions',views.post_list_suggestions,name='post_list_suggestions')
]
