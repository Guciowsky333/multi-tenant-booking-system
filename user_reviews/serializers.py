from rest_framework import serializers

from user_reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    def get_user_email(self, obj):
        return obj.user.email

    class Meta:
        model = Review
        fields = ["id", "restaurant", "restaurant_name", "user", "user_email", "comment", "rating"]
        read_only_fields = ["restaurant_name", "user_email", "user"]

    def validate(self, data):
        if not self.instance:
            user = self.context["request"].user
            restaurant = data["restaurant"]
            if Review.objects.filter(restaurant=restaurant, user=user).exists():
                raise serializers.ValidationError("You already have writen a review of this restaurant")
        return data

    def validate_restaurant(self, value):
        if self.instance and self.instance.restaurant != value:
            raise serializers.ValidationError("Cannot change restaurant of an existing review")
        return value
