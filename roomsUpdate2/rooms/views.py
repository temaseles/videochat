from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, JsonResponse
import json
import re

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout

from rooms.models import User, Room

def is_correct_email(email):
    if (email.count('@') != 1): return False
    if (' ' in email): return False
    return bool(re.fullmatch(".+@.+\\..+", email))

@require_http_methods(["POST"])
def save_user(request):
    try:
        if (request.user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "authenticated", "message": "Пользователь уже авторизован"}},
                status=403
            )

        data = json.loads(request.body)
        email = data["email"]
        username = data["username"]
        password = data["password"]

        if not (is_correct_email(email)):
            return JsonResponse(
                {"error": {"code": "validation_error", "message": "Переданные данные не прошли проверку", "details": {"email": ["Почта не соответствует требованиям"]}}},
                status=422
            )

        if (len(password) < 8):
            return JsonResponse(
                {"error": {"code": "validation_error", "message": "Переданные данные не прошли проверку", "details": {"password": ["Длина пароля должна быть не менее 8 символов"]}}},
                status=422
            )

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": {"code": "account_already_exists", "message": "Пользователь с такими данными уже существует", "details": {"email": ["Этот email уже используется"]}}},
                status=409
            )

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"error": {"code": "account_already_exists", "message": "Пользователь с такими данными уже существует", "details": {"username": ["Это имя уже используется"]}}},
                status=409
            )

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        new_user.save()

        Room.objects.create(
            title=f"Комната {username}",
            created_by=new_user
        )

        login(request, new_user)

        return JsonResponse({
            "id": new_user.id,
            "email": email,
            "username": username
        }, status=201)

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        email = data["email"]
        password = data["password"]

        if (request.user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "authenticated", "message": "Пользователь уже авторизован"}},
                status=403
            )

        if not (is_correct_email(email)):
            return JsonResponse(
                {"error": {"code": "validation_error", "message": "Проверьте введенные данные", "details": {"email": ["Укажите корректный email"]}}},
                status=422
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return JsonResponse(
                {"error": {"code": "invalid_credentials", "message": "Введен неверный email или пароль"}},
                status=401
            )
            
        login(request, user)
        return HttpResponse(status=200)

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["POST"])
def user_logout(request):
    try:
        if not (request.user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Пользователь не авторизован"}},
                status=401
            )

        logout(request)
        return JsonResponse({"message": "Выход выполнен"}, status=200)

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["DELETE"])
def delete_user_by_id(request, user_id):
    try:
        current_user = request.user
        if not (current_user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Пользователь не авторизован"}},
                status=401
            )

        user_id = int(user_id)
        if (user_id != current_user.id):
            return JsonResponse(
                {"error": {"code": "forbidden", "message": "Недостаточно прав"}},
                status=403
            )

        email = current_user.email
        username = current_user.username

        logout(request)
        current_user.delete()
        
        return JsonResponse({
            "id": user_id,
            "email": email,
            "username": username
        }, status=200)

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["GET"])
def get_user_data(request):
    try:
        current_user = request.user
        if not (current_user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Пользователь не авторизован"}},
                status=401
            )

        return JsonResponse({
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username
        }, status=200)

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["PATCH"])
def update_username(request):
    try:
        current_user = request.user
        if not (current_user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Пользователь не авторизован"}},
                status=401
            )

        username = json.loads(request.body)["username"]

        if User.objects.filter(username=username).exclude(pk=current_user.id).exists():
            return JsonResponse(
                {
                    "error": {
                        "code": "username_already_exists",
                        "message": "Данное имя пользователя уже занято",
                        "details": {"username": ["Выберите другое имя пользователя"]}
                    }
                },
                status=409
            )

        current_user.username = username
        current_user.save()
        
        return JsonResponse(
            {
                "id": current_user.id,
                "email": current_user.email,
                "username": username
            },
            status=200
        )

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["PATCH"])
def update_password(request):
    try:
        current_user = request.user
        if not (current_user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Пользователь не авторизован"}},
                status=401
            )

        data = json.loads(request.body)
        old_password = data["old_password"]
        new_password = data["new_password"]

        if not (current_user.check_password(old_password)):
            return JsonResponse(
                {"error": {"code": "validation_error", "message": "Переданные данные не прошли проверку", "details": {"old_password": ["Неверные данные"]}}},
                status=422
            )

        if (len(new_password) < 8):
            return JsonResponse(
                {"error": {"code": "validation_error", "message": "Переданные данные не прошли проверку", "details": {"new_password": ["Длина пароля должна быть не менее 8 символов"]}}},
                status=422
            )

        current_user.set_password(new_password)
        current_user.save()
        update_session_auth_hash(request, current_user)

        return JsonResponse(
            {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username
            },
            status=200
        )

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["GET"])
def get_room_general(request):
    try:
        if not (request.user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Требуется авторизация"}},
                status=401
            )
        
        try:
            room = Room.objects.get(created_by=request.user)
            return JsonResponse({
                "id": str(room.id),
                "title": room.title
            }, status=200)
        except Room.DoesNotExist:
            return JsonResponse(
                {"error": {"code": "not_found", "message": "Комната для данного пользователя не найдена"}},
                status=404
            )
            
    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)


@require_http_methods(["PATCH"])
def update_room_title(request):
    try:
        if not (request.user.is_authenticated):
            return JsonResponse(
                {"error": {"code": "not_authenticated", "message": "Требуется авторизация"}},
                status=401
            )

        data = json.loads(request.body)
        title = data.get("title", "").strip()

        if not title:
            return JsonResponse(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Переданные данные не прошли проверку",
                        "details": {"username": "Название комнаты не может быть пустым"}
                    }
                },
                status=422
            )

        try:
            room = Room.objects.get(created_by=request.user)
            room.title = title
            room.save()
            
            return JsonResponse({
                "id": str(room.id),
                "title": room.title
            }, status=200)
        except Room.DoesNotExist:
            return JsonResponse(
                {"error": {"code": "not_found", "message": "Комната для данного пользователя не найдена"}},
                status=404
            )

    except Exception as ex:
        return JsonResponse({"error": {"code": "internal_error", "message": "Произошла внутренняя ошибка сервера"}}, status=500)
