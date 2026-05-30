from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from accounts.models import CustomUser
from memberships.models import MemberShip


class MemberShipSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = MemberShip
        fields = ["id", "restaurant", "email", "user", "role"]
        extra_kwargs = {
            "email": {"write_only": True},
            "user": {"read_only": True},
        }

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
            self.context["user"] = user
            return value
        except ObjectDoesNotExist:
            raise serializers.ValidationError("user with provided email does not exist")

    def validate(self, data):

        restaurant = data["restaurant"]
        user = self.context["user"]

        if MemberShip.objects.filter(user=user, restaurant=restaurant).exists():
            raise serializers.ValidationError("User with provided email already has membership in this restaurant")

        if restaurant.owner == user:
            raise serializers.ValidationError("Owner cannot be a member of their own restaurant.")
        return data

    def create(self, validated_data):
        validated_data.pop("email")
        user = self.context["user"]
        return MemberShip.objects.create(user=user, **validated_data)


class MembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberShip
        fields = ["id", "restaurant", "user", "role"]
        extra_kwargs = {
            "restaurant": {"read_only": True},
            "user": {"read_only": True},
        }
