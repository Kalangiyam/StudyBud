from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('register/',views.registerPage,name='register'),
    path('room/<str:pk>/',views.room,name='room'),
    path('profile/<str:pk>/',views.userProfile,name='user-profile'),
    path('create-room/',views.createRoom,name='create-room'),
    path('update-room/<str:pk>',views.updateRoom,name='update-room'),
    path('delete-room/<str:pk>',views.deleteRoom,name='delete-room'),
    path('delete-message/<str:pk>',views.deleteMessage,name='delete-message'),
    path('update-profile/',views.updateProfile,name='update-profile'),
    path('topics/',views.topicsPage,name='topics'),
    path('activities/',views.activitiesPage,name='activities'),
    
]