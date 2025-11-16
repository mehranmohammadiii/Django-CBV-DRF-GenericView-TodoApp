from rest_framework.response import Response
from .serializers import LoginSerializer, RegisterSerializer, CustomTokenObtainPairSerializer, ChangePasswordSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
# --------------------------------------------------------------------------------------------------
class LogoutApiView(generics.GenericAPIView):
    
    @swagger_auto_schema(
        operation_summary="خروج کاربر",
        operation_description="کاربر از سیستم خارج می‌شود، session و token حذف می‌شوند",
        responses={
            200: openapi.Response(
                description='کاربر با موفقیت خارج شد',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='successfully logged out'
                        ),
                    }
                )
            ),
            401: openapi.Response(
                description='کاربر احراز هویت نشده',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Authentication credentials were not provided.'
                        ),
                    }
                )
            ),
        },
        tags=['Accounts']
    )
    # --------------------------------
    def post(self, request, *args, **kwargs):
        """
        Logout class - حذف Token و Session
        """
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        logout(request)
        return Response(
            {"message": "successfully logged out"},
            status=status.HTTP_200_OK,
        )
# --------------------------------------------------------------------------------------------------
class RegisterApiView(generics.GenericAPIView):

    @swagger_auto_schema(
        operation_summary="ثبت‌نام کاربر جدید",
        operation_description="یک کاربر جدید ثبت می‌کند و وارد سیستم می‌کند",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='نام کاربری',
                    example='ali_developer'
                ),
                'password1': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='رمز عبور',
                    example='SecurePass123'
                ),
                'password2': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='تایید رمز عبور',
                    example='SecurePass123'
                ),
            },
            required=['username', 'password1', 'password2']
        ),
        responses={
            201: openapi.Response(
                description='کاربر با موفقیت ثبت‌نام شد',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='ali_developer'
                        ),
                        'token': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='توکن احراز هویت',
                            example='1234567890abcdef'
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description='خطای اعتبارسنجی',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'non_field_errors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=['Passwords must be equal', 'User already exists', 'This password is too short...']
                        ),
                        'password1': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=['Password validation error']
                        ),
                    }
                )
            ),
        },
        tags=['Accounts']
    )
    # ------------------------------------
    def post(self, request, *args, **kwargs):
        """
        Register class
        """

        serializer = RegisterSerializer(data=request.data, many=False)

        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password1"]
            user = User.objects.create_user(
                    username=username, password=password
                        )
            authenticate(request, username=username, password=password)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'username': user.username,
                    'token': token.key
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# --------------------------------------------------------------------------------------------------
class LoginApiView(generics.GenericAPIView):

    @swagger_auto_schema(
        operation_summary="ورود کاربر",
        operation_description="کاربر با نام کاربری و رمز عبور وارد سیستم می‌شود",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='نام کاربری',
                    example='ali_developer'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='رمز عبور',
                    example='SecurePass123'
                ),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response(
                description='کاربر با موفقیت وارد شد',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='ali_developer'
                        ),
                        'token': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='توکن احراز هویت',
                            example='1234567890abcdef'
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description='خطای اعتبارسنجی یا اطلاعات نادرست',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'non_field_errors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=['Unable to log in with provided credentials.', 'Must include "username" and "password".']
                        ),
                    }
                )
            ),
        },
        tags=['Accounts']
    )
    # --------------------------------
    def post(self, request, *args, **kwargs):
        """
        Login view to get user credentials
        """
        serializer = LoginSerializer(data=request.data, many=False)

        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            if user is not None and user.is_active:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'username': user.username,
                        'token': token.key
                    },
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# --------------------------------------------------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = CustomTokenObtainPairSerializer
    
    @swagger_auto_schema(
        operation_summary="دریافت JWT Token",
        operation_description="توسط نام کاربری و رمز عبور، access و refresh token را دریافت کنید",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='نام کاربری',
                    example='ali_developer'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description='رمز عبور',
                    example='SecurePass123'
                ),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response(
                description='توکن‌ها با موفقیت دریافت شدند',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Access Token (مدت‌زمان محدود)',
                            example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Refresh Token (برای تجدید Access)',
                            example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                        ),
                        'username': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='نام کاربری',
                            example='ali_developer'
                        ),
                        'user_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='شناسه کاربر',
                            example=1
                        ),
                    }
                )
            ),
            401: openapi.Response(
                description='اطلاعات نادرست',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='No active account found with the given credentials'
                        ),
                    }
                )
            ),
        },
        tags=['JWT']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
# --------------------------------------------------------------------------------------------------
class ChangePasswordView(generics.GenericAPIView):

    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    # --------------------------------
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    # --------------------------------
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password1"))
            self.object.save()

            return Response({'message': 'Password updated successfully',}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# --------------------------------------------------------------------------------------------------
class SendEmailView(generics.GenericAPIView):
    
    def get(self, request, *args, **kwargs):
        send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )
        return Response("send email")
    #smtp4dev
    #django email templates 
    #Django Mail Templated
# --------------------------------------------------------------------------------------------------
