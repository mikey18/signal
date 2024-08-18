from rest_framework import serializers
from .models import User, MT5Account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        email = validated_data.get("email")
        if email:
            validated_data["email"] = email.lower()
        password = validated_data.pop("password", None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6)


class MT5AccountSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source="server.name")

    class Meta:
        model = MT5Account
        fields = [
            "account",
            "password",
            "server_name",
            "activate_automation",
            "verified",
        ]


class BrokersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
