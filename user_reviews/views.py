from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from user_reviews.models import Review
from user_reviews.permisions import IsReviewOwnerOrRestaurantOwnerOrManager
from user_reviews.serializers import ReviewSerializer

# Create your views here.


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrRestaurantOwnerOrManager]

    def get_queryset(self):
        """
        This endpoint returns only reviews that belongs to the user.
        To see all reviews some restaurant see api/restaurants/{restaurant_id}/reviews/

        Additionally: Owner or managers of the restaurant are also allowed to destroy reviews per their restaurant.
        """

        # Destroy method returns all objects and then permission mange who has access and who does not
        if self.action == "destroy":
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set request user as owner
        serializer.save(user=self.request.user)
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        # Cleat cache all reviews of the restaurant
        cache.delete_pattern(f"restaurant_{serializer.validated_data['restaurant'].id}_reviews_*")

    def perform_update(self, serializer):
        serializer.save()
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        # Cleat cache all reviews of the restaurant
        restaurant_id = serializer.instance.restaurant.id
        cache.delete_pattern(f"restaurant_{restaurant_id}_reviews_*")

    def perform_destroy(self, instance):
        restaurant_id = instance.restaurant.id
        instance.delete()
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        # Cleat cache all reviews of the restaurant
        cache.delete_pattern(f"restaurant_{restaurant_id}_reviews_*")
