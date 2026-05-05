from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_2 = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        password = data["password"]
        password_2 = data["password_2"]

        if password != password_2:
            raise serializers.ValidationError("Passwords do not match")

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if not any(x.isupper() for x in password):
            raise serializers.ValidationError("Password must contain at least one uppercase character")

        return data
