from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Room,Topic,Message
from .forms import RoomForm, UserForm

# Create your views here.
# rooms = [
#     {'id':1,'name':"Let's learn python!"},
#     {'id':2,'name':"Let's learn flask!"},
#     {'id':3,'name':"Let's learn django!"},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('base:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)           
        except:
            messages.error(request,'User dose not exist')
            
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('base:home')
        else:
            messages.error(request,'Username or Password is wrong')            
    context={'page':page}
    return render(request,'base/login_register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('base:home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)           
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('base:home')
    context = {'form':form}
    return render(request,'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username=q)
        
    )
    topics = Topic.objects.all()    
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)|Q(room__host__username=q))[:5]
        
    rooms_count = rooms.count()

    paginator = Paginator(rooms,5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

  
    context={'page_obj':page_obj,'topics':topics,'rooms_count':rooms_count,
                'room_messages':room_messages,'is_paginated': True if paginator.num_pages > 1 else False}
    return render(request,'base/home.html',context)
 
def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants  = room.participants.all()
   
    if request.method == 'POST':
        print(request.user)
        message=Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('base:room',pk=room.id)
    
    context= {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    p_user = User.objects.get(id=pk)    
    room_messages = p_user.message_set.all()[:5]
    rooms = p_user.room_set.all()
    topics = Topic.objects.all()

    paginator = Paginator(rooms,3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 

 
    context= {'page_obj':page_obj,'room_messages':room_messages,
              'topics':topics,'puser':p_user,'is_paginated': True if paginator.num_pages > 1 else False}
    return render(request,'base/profile.html',context)

    
    
@login_required(login_url='base:login')
def updateProfile(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('base:user-profile',pk=user.id)
    return render(request,'base/update_profile.html',{'form':form})

@login_required(login_url='base:login')
def createRoom(request):
    form = RoomForm()
    topics=Topic.objects.all()
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('base:home')
    
    context = {
        'form':form,'topics':topics
    }
    return render(request,'base/room_form.html',context)

@login_required(login_url='base:login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)   
    topics = Topic.objects.all() 
    
    if request.user != room.host:
        return HttpResponse('Yore not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic') 
        # print(topic_name)       
        topic,created = Topic.objects.get_or_create(name=topic_name)
        # print(topic)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('base:home')
        
    context={'form': form,'room':room,'topics':topics}
    return render(request,'base/room_form.html',context)
    
@login_required(login_url='base:login')
def deleteRoom(request,pk):    
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Yore not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('base:home')
    
    context = {'obj':room}
    return render(request,'base/delete.html',context)

@login_required(login_url='base:login')
def deleteMessage(request,pk):      
    message = Message.objects.get(id=pk)    

    if request.user != message.user:
        return HttpResponse('Yore not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('base:home')
    
    context = {'obj':message}
    return render(request,'base/delete.html',context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context={ 'topics':topics}
    return render(request,'base/topics.html',context)

def activitiesPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''   
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q) |
                                           Q(room__name__icontains=q) |
                                           Q(user__username__icontains=q)
                                           )
    paginator = Paginator(room_messages,5)

    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)