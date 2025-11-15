from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# from django.utils.translation import ugettext_lazy as _
from django.core import exceptions
import django.contrib.auth.password_validation as validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# ------------------------------------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer برای اضافه کردن username و user_id به JWT tokens
    """
    username = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    
    # def get_token(self, user):
    #     token = super().get_token(user)
    #     return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['user_id'] = self.user.id
        return data

# ------------------------------------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        label=("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        max_length=128,
        write_only=True,
    )
    # -----------------------------------
    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )
            if not user:
                msg = ("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = ('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")
        data["user"] = user
        return data

# ------------------------------------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password1 = serializers.CharField(
        label=("Password1"),
        style={"input_type": "password"},
        trim_whitespace=False,
        max_length=128,
        write_only=True,
    )
    password2 = serializers.CharField(
        label=("Password2"),
        style={"input_type": "password2"},
        trim_whitespace=False,
        max_length=128,
        write_only=True,
    )
    # -----------------------------------
    def validate(self, data):
        username = data.get("username")
        password1 = data.get("password1")
        password2 = data.get("password2")

        # django serializer check password complexity
        try:
            validators.validate_password(password=password1)  
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})

        if not password1 == password2:
            msg = ("Passwords must be equal")
            raise serializers.ValidationError(msg, code="authorization")
        if User.objects.filter(username=username).exists():
            msg = ("User already exists pick another username")
            raise serializers.ValidationError(msg, code="authorization")

        return data
# ------------------------------------------------------------------------------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    # -----------------------------------
    def validate(self, data):
        password1 = data.get("new_password1")
        password2 = data.get("new_password2")

        # django serializer check password complexity
        try:
            validators.validate_password(password=password1)  
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password1": list(e.messages)})

        if not password1 == password2:
            msg = ("Passwords must be equal")
            raise serializers.ValidationError(msg, code="authorization")
        return data
# ------------------------------------------------------------------------------------------------------
