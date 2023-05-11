from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse,HttpResponseNotAllowed,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount,Comment,Chat
from itertools import chain
import random
import datetime
from .helpers import sendMail
from django.utils import timezone

@csrf_exempt
@login_required(login_url='signin')
def saveLastLogin(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user_profile.lastlogin = timezone.now()
    user_profile.save()
    return JsonResponse({})

@csrf_exempt
@login_required(login_url='signin')
def message(request,username):
    return render(request, 'message.html' ,{"username":request.user.username,"user_profile":get_info(request)["user_profile"],"username2":username} )

@csrf_exempt
@login_required(login_url='signin')
def send_message(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        message = request.POST.get('message')
        print(nickname,message)
        user1 = request.user
        user2 = User.objects.get(username=nickname)
        new_chat = Chat.objects.create(sender=user1,receiver=user2,message=message)
        new_chat.save()
        return JsonResponse({})
    else:
        return JsonResponse({})

@csrf_exempt
@login_required(login_url='signin')
def get_list_message(request):
    if request.method == 'POST':
        username2 = request.POST.get('username2')
        if username2 != "Default":
            user = request.user
            chats = Chat.objects.filter(Q(sender=user) | Q(receiver=user))
            profiles = Profile.objects.filter(Q(user__in=[chat.sender_id if chat.receiver == user else chat.receiver_id for chat in chats]))
            unique_profiles = profiles.distinct().order_by('-id')
            list_id = []
            list_nickname = []
            list_avt = []
            list_chats = []
            list_active = []
            for i in unique_profiles:
                list_id.append(i.id_user)
                list_nickname.append(i.user.username)
                list_avt.append(i.profileimg.url)
                date_str = str(i.lastlogin)
                time_ago_str = time_ago1(date_str)
                list_active.append(time_ago_str)
                list_chat = []
                chat_history = Chat.objects.filter(Q(sender=user, receiver=i.user) | Q(sender=i.user, receiver=user)).order_by('created_at')
                for i in chat_history:
                    if i.sender == user:
                        list_chat.append([i.message,True])
                    else:
                        list_chat.append([i.message,False])
                list_chat.reverse()
                list_chats.append(list_chat)
            if username2 not in list_nickname:
                user = User.objects.get(username=username2)
                list_id.insert(0,Profile.objects.get(user=user).id_user)
                list_nickname.insert(0,username2)
                list_avt.insert(0,Profile.objects.get(user=user).profileimg.url)
                list_chats.insert(0,[])
            else:
                index = list_nickname.index(username2)
                list_id = [list_id[index]] + list_id[:index] + list_id[index+1:]
                list_nickname = [list_nickname[index]] + list_nickname[:index] + list_nickname[index+1:]
                list_avt = [list_avt[index]] + list_avt[:index] + list_avt[index+1:]
                list_chat = [list_chat[index]] + list_chat[:index] + list_chat[index+1:]
            return JsonResponse({'list_id':list_id,
                                'list_nickname': list_nickname,
                                'list_avt': list_avt,
                                'list_chats':list_chats,
                                'list_active':list_active})
        else:
            user = request.user
            chats = Chat.objects.filter(Q(sender=user) | Q(receiver=user))
            profiles = Profile.objects.filter(Q(user__in=[chat.sender_id if chat.receiver == user else chat.receiver_id for chat in chats]))
            unique_profiles = profiles.distinct().order_by('-id')
            list_id = []
            list_nickname = []
            list_avt = []
            list_chats = []
            list_active = []
            for i in unique_profiles:
                list_id.append(i.id_user)
                list_nickname.append(i.user.username)
                list_avt.append(i.profileimg.url)
                list_chat = []
                date_str = str(i.lastlogin)
                time_ago_str = time_ago1(date_str)
                list_active.append(time_ago_str)
                chat_history = Chat.objects.filter(Q(sender=user, receiver=i.user) | Q(sender=i.user, receiver=user)).order_by('created_at')
                for i in chat_history:
                    if i.sender == user:
                        list_chat.append([i.message,True])
                    else:
                        list_chat.append([i.message,False])
                list_chat.reverse()
                list_chats.append(list_chat)
            return JsonResponse({'list_id':list_id,
                                'list_nickname': list_nickname,
                                'list_avt': list_avt,
                                'list_chats':list_chats,
                                'list_active':list_active})
    else:
        return JsonResponse({})

@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html', get_info(request))


@login_required(login_url='signin')
def post_list_post(request):
    return JsonResponse(get_list_post(request))

@login_required(login_url='signin')
def post_list_suggestions(request):
    return JsonResponse(get_list_suggestions(request))

@login_required(login_url='signin')
@csrf_exempt
def comment(request):
    if request.method == 'POST':
        user = request.user
        post_id = request.POST.get('post_id')
        print(post_id)
        post = Post.objects.get(id=post_id)
        post.no_of_cmts = post.no_of_cmts + 1
        print(post.no_of_cmts)
        post.save()
        text = request.POST.get('text-comment')
        
        new_comment = Comment.objects.create(user=user,post=post,text=text)
        new_comment.save()
        return JsonResponse({})
    else:
        return JsonResponse({})
@login_required(login_url='signin')
@csrf_exempt
def like_post(request):
    if request.method == 'POST':
        username = request.user.username
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)

        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
        if like_filter == None:
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes = post.no_of_likes+1
            post.save()
            return JsonResponse({})
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes-1
            post.save()
            return JsonResponse({})
    else:
        return JsonResponse({})

@login_required(login_url='signin')
@csrf_exempt
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        caption = request.POST.get('caption')
        file_image = request.FILES.get('fileImage')
        print(caption,file_image)
        new_post = Post.objects.create(user=user, image=file_image, caption=caption)
        new_post.save()
        return redirect('/') 
    else:
        return redirect('/')

def signin(request):
    if request.method == 'POST':
        names = ['username','password']
        data = {name: request.POST.get(name) for name in names}
        user = auth.authenticate(username=data['username'], password=data['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'The password is incorrect')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    return

def signup(request):
    if request.method == 'POST':
        names = ['email', 'fullname', 'username', 'password']
        data = {name: request.POST.get(name) for name in names}
        if User.objects.filter(email=data['email']).exists():
            messages.info(request,'Email address already exists')
            return redirect('signup')
        elif User.objects.filter(username=data['username']).exists():
            messages.info(request,'Username already exists')
            return redirect('signup')

        else:
            new_user = User.objects.create_user(username=data['username'],email=data['email'], password=data['password'])
            new_user.save()
            user_login = auth.authenticate(username=data['username'], password=data['password'])
            auth.login(request, user_login)
            user_model = User.objects.get(username=data['username'])
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id,full_name=data['fullname'])
            new_profile.save()
            return redirect('/')
    else:
        return render(request,'signup.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@csrf_exempt
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.user.username
        user = request.POST.get('user')
        if user==follower:
            return
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            print("unfollow")
            return JsonResponse({})
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            print("follow")
            return JsonResponse({})

    else:
        return JsonResponse({})

@csrf_exempt
def profile(request,username):
    return render(request, 'profile.html',{"username":username,"user_profile":get_info(request)["user_profile"]})



def get_info(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    # lấy post của bản thân

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    return {'user_profile': user_profile,'suggestions_username_profile_list': suggestions_username_profile_list[:4]}  

# def get_profile(request):


def get_list_post(request):
    user_object = User.objects.get(username=request.user.username) # user 
    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    # lấy post của bản thân
    feed.append(Post.objects.filter(user=user_object))
    # lấy post của list follow
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    feed_list = list(chain(*feed)) # list post
    feed_list.sort(key=lambda x: int(x.created_at.timestamp()), reverse=True) # sắp xếp theo thời gian
    list_image_avatar = []
    list_nickname = []
    list_created_at = []
    list_image_post = []
    list_caption = []
    list_liked = []
    list_count_like = []
    list_count_cmt = []
    list_post_id = []
    comments = []
    for post in feed_list:
        list_comment = Comment.objects.filter(post=post)
        comment = []
        for _ in list_comment:
            avt = Profile.objects.get(user=_.user).profileimg.url
            nickname = _.user.username
            text = _.text
            comment.append([avt,nickname,text])
        comments.append(comment)
        _user_object = User.objects.get(username=post) # user
        _user_profile = Profile.objects.get(user=_user_object) # my profile
        
        list_image_avatar.append(_user_profile.profileimg.url)
        
        list_nickname.append(_user_profile.user.username)
        
        date_str = str(post.created_at)
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f%z')
        time_ago_str = time_ago(date_str)
        list_created_at.append(time_ago_str)
        
        like_filter = LikePost.objects.filter(post_id=post.id, username=request.user.username).first()
        if like_filter == None:
            list_liked.append(False)
        else:
            list_liked.append(True)
        list_image_post.append(post.image.url)
        list_caption.append(post.caption)
        list_count_like.append(post.no_of_likes)
        list_count_cmt.append(post.no_of_cmts)
        list_post_id.append(post.id)
    return {"list_image_avatar":list_image_avatar,"list_nickname":list_nickname,"list_created_at":list_created_at,"list_liked":list_liked,"list_count_like": list_count_like,"list_image_post":list_image_post,"list_caption":list_caption,"list_post_id":list_post_id,"comments":comments,"list_count_cmt":list_count_cmt}
  
def get_list_suggestions(request):
    
    user_following_list = []
    
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    
    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    suggestions_username_profile_list = suggestions_username_profile_list[:4]
    list_user = []
    list_fullname = []
    list_profileimg = []
    for _ in suggestions_username_profile_list:
        list_user.append(_.user.username)
        list_fullname.append(_.full_name)
        list_profileimg.append(_.profileimg.url)
    return {'list_user':list_user,'list_fullname':list_fullname,'list_profileimg':list_profileimg,"allUsers":getSuggestionShare(request.user.username)}
@login_required(login_url='signin')
def getUsersForShare(request):
        
    
    return JsonResponse({
        "allUsers":getSuggestionShare(request.user.username)
         })
def getSuggestionShare(username):
    profiles = Profile.objects.all()
    users=[]
    for profile in profiles:
        if profile.user.username!=username:
            users.append({
            "username":profile.user.username,
            "imageurl":profile.profileimg.url,
            "name":profile.full_name,
            })
    return users
def time_ago(date):
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    seven_hours = datetime.timedelta(hours=7)
    now = now + seven_hours
    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f%z')
    delta = now - date
    if delta.days > 6:
        weeks = delta.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{delta.seconds} second{'s' if delta.seconds > 1 else ''} ago"

def time_ago1(date):
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f%z')
    delta = now - date
    if delta.days > 6:
        weeks = delta.days // 7
        return f"Active {weeks}w{'s' if weeks > 1 else ''} ago"
    elif delta.days > 0:
        return f"Active {delta.days}d{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"Active {hours}h{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"Active {minutes}m{'s' if minutes > 1 else ''} ago"
    else:
        return f"Active now"
@login_required(login_url='signin')
def get_profile(request,username):
    user_logined = User.objects.get(username=request.user.username)
    user_view = User.objects.get(username=username)
    profile_user_loggined=Profile.objects.get(user=user_logined)
    profile_user_view=Profile.objects.get(user=user_view)
    user_posts = Post.objects.filter(user=user_view.username).order_by('-created_at')

    user_logined_dict = {
        "username":profile_user_loggined.user.username,
        "imageurl":profile_user_loggined.profileimg.url,
        "name":profile_user_loggined.full_name,
    }
    user_view_dict={
        "username":profile_user_view.user.username,
        "name":profile_user_view.full_name,
        "imageurl":profile_user_view.profileimg.url,
        "bio":profile_user_view.bio
    }
    user_posts_dict=[{
        "id":i.id,
        "image":i.image.url,
        "no_of_likes":i.no_of_likes,
        "no_of_cmts": i.no_of_cmts
    } for i in user_posts]
    follower = len(FollowersCount.objects.filter(user=user_view.username))
    following= len(FollowersCount.objects.filter(follower=user_view.username))

    
    return JsonResponse(
        {"user_logined":user_logined_dict,
         "user_view":user_view_dict,
         "follower":follower,
         "following":following,
         "status_follow":getStatusFollow(user_logined,user_view),
         "posts":user_posts_dict})



@login_required(login_url='signin')
def getFollowers(request,username):
    user_logined = User.objects.get(username=request.user.username)
    user_view = User.objects.get(username=username)

    followers=FollowersCount.objects.filter(user=user_view.username)

    followers_dict = []
    for i in followers:
        user = User.objects.get(username=i.follower)
        profile_user=Profile.objects.get(user=user)

        followers_dict.append({
        "username":profile_user.user.username,
        "imageurl":profile_user.profileimg.url,
        "name":profile_user.full_name,
        "status":getStatusFollow(user_logined,user)
        })

    return JsonResponse(
        {"followers":followers_dict})
@login_required(login_url='signin')
def getFollowings(request,username):
    user_logined = User.objects.get(username=request.user.username)
    user_view = User.objects.get(username=username)

    followings=FollowersCount.objects.filter(follower=user_view.username)

    followings_dict = []
    for i in followings:
        user = User.objects.get(username=i.user)
        profile_user=Profile.objects.get(user=user)

        followings_dict.append({
        "username":profile_user.user.username,
        "imageurl":profile_user.profileimg.url,
        "name":profile_user.full_name,
        "status":getStatusFollow(user_logined,user)
        })
    return JsonResponse(
        {"followings":followings_dict})

def getStatusFollow(user_logined,user_view):
    if len(FollowersCount.objects.filter(Q(user=user_logined.username)&Q(follower=user_view.username)))>0:
        status=-1
    else:
        status=0
    if len(FollowersCount.objects.filter(Q(user=user_view.username)&Q(follower=user_logined.username)))>0:
        status=1
    if user_logined.username==user_view.username:
        status=True
    return status

@login_required(login_url='signin')
def getPost(request,postId):
    username=request.user.username
    status_like=len(LikePost.objects.filter(Q(post_id=postId)&Q(username=username)))>0
    post = Post.objects.get(id=postId)
    profile = Profile.objects.get(user=User.objects.get(username=post.user))    
    post_dict={"id":post.id,
        "user":post.user,
        "userAvt":profile.profileimg.url,
        "image":post.image.url,
        "caption":post.caption,
        "created_at":post.created_at,
        "no_of_likes":post.no_of_likes,
        "status_like":status_like
    }

    return JsonResponse(
        {"post":post_dict})

@login_required(login_url='signin')
def getCommentsPost(request,postId):
        
    comments = Comment.objects.filter(post_id=postId)
    comments_dict=[]
    for comment in comments:
        profile = Profile.objects.get(id_user=comment.user_id)
        comments_dict.append({
            "id":comment.id,
            "text":comment.text,
            "created_at":comment.created_at,
            "imgUserUrl":profile.profileimg.url,
            "user":profile.user.username
        })

    return JsonResponse(
        {"commentsOfPost":comments_dict})
@login_required(login_url='signin')
def getNumLikesCmts(request,postId):
        
    likes = LikePost.objects.filter(post_id=postId)
    comments = Comment.objects.filter(post_id=postId)
    username=request.user.username
    status_like=len(LikePost.objects.filter(Q(post_id=postId)&Q(username=username)))>0
    

    return JsonResponse({
        "numOfLikes":len(likes),
        "numOfCmts":len(comments),
        "status_like":status_like,
         })


@csrf_exempt
@login_required(login_url='signin')
def updateProfile(request):
    if request.method == 'POST':
        newName = request.POST.get('newName')
        newPassword = request.POST.get('newPassword')
        oldPassword = request.POST.get('password')
        print(newName,newPassword,oldPassword)  
        user = User.objects.get(username=request.user.username)
        if user.check_password(oldPassword):
            if newName != "":
                user_object = User.objects.get(username=request.user.username)
                user_profile = Profile.objects.get(user=user_object)
                user_profile.full_name = newName
                print("update fullname")
                user_profile.save()
            if newPassword != "":
                print("update password")
                user.set_password(newPassword)
                user.save()
            return JsonResponse({"password":True})
        else:
            return JsonResponse({"password":False})
    else:
        return JsonResponse({})

@csrf_exempt
@login_required(login_url='signin')
def updateAvatar(request):
    if request.method == 'POST':
        file_image = request.FILES.get('fileImage')
        print(file_image)
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        user_profile.profileimg = file_image
        user_profile.save()
        return JsonResponse({"1":1})
    else:
        return JsonResponse({"2":1})
    
import uuid
@csrf_exempt
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            print(email)
            if not User.objects.filter(email = email).first():
                messages.success(request, 'Không tìm thấy địa chỉ email của bạn.')
                print('khong ton tai nguoi nay trong db')
                return redirect('/forget-password/')
            
            user_obj = User.objects.get(email = email)
            print(user_obj.username)
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.get(user = user_obj)
            print('4')
            profile_obj.forget_password_token = token
            profile_obj.save()
            sendMail(user_obj.email , token)
            messages.success(request, 'Liên kết đã được gửi qua email.')
            return redirect('/forget-password/')
                
    except Exception as e:
        print('Loi')
        print(e)
    return render(request , 'forget-password.html')

def ChangePassword(request,token):
    context = {}    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}       
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'Không tìm thấy user id.')
                return redirect(f'/change-password/{token}/')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'Mật khẩu xác nhận không trùng khớp!')
                return redirect(f'/change-password/{token}/')        
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/signin')    
    except Exception as e:
        print(e)
    return render(request , 'change-password.html' , context)

