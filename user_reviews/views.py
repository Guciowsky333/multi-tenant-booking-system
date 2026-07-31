from django.core.cache import cache
from drf_spectacular.utils import OpenApiResponse, extend_schema
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

        if self.action == "destroy":
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Clear cache because average_review_rating depends on reviews
        cache.delete_pattern("restaurants_all*")
        # Clear cache all reviews of the restaurant
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

    @extend_schema(
        summary="Creates review for provided restaurant.",
        description="""
        Creates review for provided restaurant.
        Allowed for any logged-in user.
        
        Business rules:
        - Fields (rating, restaurant) are required field comment is optional
        - Field rating must be between 1 and 10 (inclusive).
        - Restaurant must exist.
        - User can write only one comment for one restaurant.
        - Request user must be authenticated.
        """,
        request=ReviewSerializer,
        responses={
            201: OpenApiResponse(description="Review created"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="User is not authenticated"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Updates review for provided restaurant.",
        description="""
        Updates review for provided restaurant.
        Allowed only for the owner of the review.

        Business rules:
        - Fields (rating, restaurant) are required, field comment is optional.
        - Field rating must be between 1 and 10 (inclusive).
        - Restaurant must exist.
        - Provided review must exist.
        - User cannot change the restaurant of the review.
        - Request user must be authenticated.
        - Request user must be the owner of the provided review.
        """,
        request=ReviewSerializer,
        responses={
            200: OpenApiResponse(description="Review updated"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Review does not exist"),
            401: OpenApiResponse(description="User is not authenticated"),
            403: OpenApiResponse(description="User is not owner of the review"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially updates review for provided restaurant.",
        description="""
        Partially updates review for provided restaurant.
        Only provided fields will be updated, the rest remain unchanged.
        Allowed only for the owner of the review.

        Business rules:
        - Field rating, if provided, must be between 1 and 10 (inclusive).
        - Provided review must exist.
        - User cannot change the restaurant of the review.
        - Request user must be authenticated.
        - Request user must be the owner of the provided review.
        """,
        request=ReviewSerializer,
        responses={
            200: OpenApiResponse(description="Review updated"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Review does not exist"),
            401: OpenApiResponse(description="User is not authenticated"),
            403: OpenApiResponse(description="User is not owner of the review"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Deletes provided review.",
        description="""
        Deletes provided review. Allowed only for the owner of the review or
        for manager or owner of the restaurant which this review is for.

        Business rules:
        - Provided review must exist.
        - Request user must be authenticated.
        - Request user must be the owner of the provided review or manager or owner of the
        restaurant which this review is for.
        """,
        responses={
            204: OpenApiResponse(description="Review deleted"),
            401: OpenApiResponse(description="User is not authenticated"),
            403: OpenApiResponse(description="User does not have permission to delete this review"),
            404: OpenApiResponse(description="Review does not exist"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
