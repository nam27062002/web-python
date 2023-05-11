from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('message/<str:username>',views.message,name='message'),
    path('saveLastLogin',views.saveLastLogin,name='saveLastLogin'),
    path('get_list_message',views.get_list_message,name='get_list_message'),
    path('send_message',views.send_message,name='send_message'),
    path('',views.index,name='index'),
    path('logout',views.logout,name='logout'),
    path('upload',views.upload,name='upload'),
    path('like_post',views.like_post,name='like_post'),
    path('post_list_post',views.post_list_post,name='post_list_post'),
    path('follow',views.follow,name='follow'),
    path('post_list_suggestions',views.post_list_suggestions,name='post_list_suggestions'),
    path('comment',views.comment,name='comment'),
    path('get_profile/<str:username>',views.get_profile,name='get_profile'),
    path('getFollowers/<str:username>',views.getFollowers,name="getFollowers"),
    path('getFollowings/<str:username>',views.getFollowings,name="getFollowings"),
    path('getUsersForShare',views.getUsersForShare,name="getUsersForShare"),
    path('getPost/<str:postId>',views.getPost,name="getFollowings"),
    path('getCommentsPost/<str:postId>',views.getCommentsPost,name='getCommentsPost'),
    path('getNumLikesCmts/<str:postId>',views.getNumLikesCmts,name='getNumLikesCmtsPost'),
    path('updateProfile',views.updateProfile,name='updateProfile'),
    path('updateAvatar',views.updateAvatar,name='updateAvatar'),
    path('<str:username>',views.profile,name='profile'),

]
