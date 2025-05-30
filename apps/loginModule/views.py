import random
import uuid
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def loginPage(request):
    return render(request, 'LoginModule/login.html')
def registerPage(request):
    return render(request, 'LoginModule/register.html')
def forgotPassword(request):
    return render(request, 'LoginModule/forgotPassword.html')
@csrf_exempt
def sendEmail(request):
    """发送消息内容到邮箱，message是一个6位验证码"""
    if request.method == "POST":
        user_email = request.POST.get("userEmail")
        if not user_email:
            return JsonResponse({"status": "fail", "message": "Email is required"}, status=400)

        # 生成6位数验证码
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        message = f'<p>Your authentication code is: <strong>{code}</strong>It is valid for only five minutes</p>'
        key = f"email_code_:{user_email}"
        cache.set(key, str(code),timeout=300)  # 5分钟过期
        print(cache.get(key))
        try:
            send_mail(
                subject="Authentication code",
                message=code,
                from_email=settings.EMAIL_FROM,
                recipient_list=[user_email],
                html_message=message
            )
            return JsonResponse({"status": "success", "message": "Email sent successfully"})
        except Exception as e:
            return JsonResponse({"status": "fail", "message": str(e)}, status=500)

    return JsonResponse({"status": "fail", "message": "Invalid request method"}, status=405)

@csrf_exempt
def registerCheck(request):
    if request.method == "POST":
        user_email = request.POST.get("userEmail")
        password = request.POST.get("userRepeatPwd")
        input_code = request.POST.get("authCode")

        if not all([user_email, password, input_code]):
            return JsonResponse({"status": "fail", "message": "Missing required fields."}, status=400)

        key = f"email_code_:{user_email}"
        real_code = cache.get(key)

        if real_code is None:
            return JsonResponse({"status": "fail", "message": "Verification code expired or not found."}, status=400)

        if input_code != real_code:
            return JsonResponse({"status": "fail", "message": "Incorrect verification code."}, status=400)

        with connection.cursor() as cursor:
            # 先查是否存在
            cursor.execute("SELECT * FROM User WHERE userName = %s", [user_email])
            if cursor.fetchone():
                return JsonResponse({"status": "fail", "message": "Account is existed."}, status=400)
            # 不存在就插入
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = "1"
            cursor.execute(
                "INSERT INTO User (userName, password, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                [user_email, password, status, now, now]
            )

        return JsonResponse({"status": "success", "message": "Registration successful."})

    return JsonResponse({"status": "fail", "message": "Invalid request method."}, status=405)


@csrf_exempt
def loginCheck(request):
    if request.method == "POST":
        email = request.POST.get("A_name")
        password = request.POST.get("A_pwd")

        if not email or not password:
            return JsonResponse({"status": "fail", "message": "Email and password are required."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM User WHERE userName = %s", [email])
            result = cursor.fetchone()

        if result:
            db_password = result[0]
            if db_password == password:
                request.session['user_email'] = email
                return JsonResponse({"status": "success", "message": "Login successful."})
            else:
                return JsonResponse({"status": "fail", "message": "Incorrect password."})
        else:
            return JsonResponse({"status": "fail", "message": "Account does not exist."})

    return JsonResponse({"status": "fail", "message": "Invalid request method."})