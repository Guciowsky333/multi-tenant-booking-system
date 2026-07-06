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
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        # Set request user as owner of review
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        serializer.save()

    def perform_destroy(self, instance):
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        instance.delete()
