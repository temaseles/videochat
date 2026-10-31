from django.contrib import admin
from django.urls import path
from rooms.views import (
    save_user,
    get_user_data,
    delete_user_by_id,
    update_username,
    update_password,
    user_login,
    user_logout,
    get_room_general,
    update_room_title
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/register', save_user),
    path('api/users/login', user_login),
    path('api/users/logout', user_logout),
    path('api/users/delete/<int:user_id>', delete_user_by_id),
    path('api/users/account', get_user_data),
    path('api/users/edit/username', update_username),
    path('api/users/edit/password', update_password),
    path('api/rooms/general', get_room_general),
    path('api/rooms/edit', update_room_title),
]
