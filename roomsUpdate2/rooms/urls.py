from django.urls import path
from rooms import views

urlpatterns = [
    path('api/users/account', views.get_user_data),
    path('api/users/register', views.save_user),
    path('api/users/login', views.user_login),
    path('api/users/logout', views.user_logout),
    path('api/users/edit/username', views.update_username),
    path('api/users/edit/password', views.update_password),
    path('api/users/delete/<int:user_id>', views.delete_user_by_id),
    
    path('api/rooms/general', views.get_room_general),
    path('api/rooms/edit', views.update_room_title),
]
