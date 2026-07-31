# Create your views here.
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from available_rules.permisions import IsRestaurantOwnerOrManager
from available_rules.serializers import (
    AvailableRuleSerializer,
    RestaurantBreakSerializer,
    RestaurantExceptionSerializer,
    RestaurantTableSerializer,
)


class AvailableRuleViewSet(viewsets.ModelViewSet):
    """
    This endpoint is allowed only for owner or members of the restaurant.
    For public available rules date use GET /api/restaurants/{id}/ which returns available rules
    assigned to provided restaurant.
    """

    serializer_class = AvailableRuleSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return AvailableRule.objects.filter(restaurant__owner=self.request.user) | AvailableRule.objects.filter(
            restaurant__memberships__user=self.request.user
        )

    @extend_schema(
        summary="Create available rule per day of week",
        description="""
        Create available rule per day of week at provided restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.
        
        Business rules:
        - Fields (restaurant, opening_time, closing_time, day_of_week) are required.
        - Restaurant must exist.
        - closing_time must be greater than opening_time.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - Combination of restaurant and day_of_week must be unique (one rule per day per restaurant).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=AvailableRuleSerializer,
        responses={
            201: OpenApiResponse(description="Available rules created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update available rule per day of week",
        description="""
        Updates available rule per day of week at provided restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.

        Business rules:
        - Fields (restaurant, opening_time, closing_time, day_of_week) are required.
        - Restaurant must exist.
        - closing_time must be greater than opening_time.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - Combination of restaurant and day_of_week must be unique (one rule per day per restaurant).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=AvailableRuleSerializer,
        responses={
            200: OpenApiResponse(description="Available rule updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Available rule not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update available rule per day of week",
        description="""
        Partially updates available rule per day of week at provided restaurant.
        Only provided fields will be updated, the rest remain unchanged.
        This endpoint is allowed only for owner or manager of the restaurant.
        
        If only one of opening_time/closing_time is provided, the other one is taken 
        from the existing rule for validation.

        Business rules:
        - Restaurant must exist.
        - closing_time must be greater than opening_time.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - Combination of restaurant and day_of_week must be unique (one rule per day per restaurant).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=AvailableRuleSerializer,
        responses={
            200: OpenApiResponse(description="Available rule updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Available rule not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class RestaurantTableViewSet(viewsets.ModelViewSet):
    """
    The same access rules as AvailableRuleViewSet.
    For public data use GET /api/restaurants/{id}/
    """

    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return RestaurantTable.objects.filter(restaurant__owner=self.request.user) | RestaurantTable.objects.filter(
            restaurant__memberships__user=self.request.user
        )

    @extend_schema(
        summary="Create restaurant table",
        description="""
        Creates restaurant table at provided restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.
        
        Business rules:
        - Fields (restaurant, table_number, seats) are required.
        - Restaurant must exist.
        - seats must be greater than 0.
        - Combination of restaurant and table_number must be unique (table_number is assigned to specific table).
        """,
        request=RestaurantTableSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant table created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update restaurant table",
        description="""
            Updates restaurant table at provided restaurant.
            This endpoint is allowed only for owner or manager of the restaurant.

            Business rules:
            - Fields (restaurant, table_number, seats) are required.
            - Restaurant must exist.
            - seats must be greater than 0.
            - Combination of restaurant and table_number must be unique (table_number is assigned to specific table).
            - Request user must be authenticated.
            - Request user has to be owner or manager of the restaurant.
            """,
        request=RestaurantTableSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant table updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant table not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update restaurant table",
        description="""
            Partially updates restaurant table at provided restaurant.
            Only provided fields will be updated, the rest remain unchanged.
            This endpoint is allowed only for owner or manager of the restaurant.

            Business rules:
            - Restaurant must exist.
            - seats must be greater than 0.
            - Combination of restaurant and table_number must be unique (table_number is assigned to specific table).
            - Request user must be authenticated.
            - Request user has to be owner or manager of the restaurant.
            """,
        request=RestaurantTableSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant table updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant table not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class RestaurantBreakViewSet(viewsets.ModelViewSet):
    """
    The same access rules as AvailableRuleViewSet.
    """

    serializer_class = RestaurantBreakSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return RestaurantBreak.objects.filter(restaurant__owner=self.request.user) | RestaurantBreak.objects.filter(
            restaurant__memberships__user=self.request.user
        )

    @extend_schema(
        summary="Create restaurant break",
        description="""
        Creates restaurant break at provided restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.
        
        Business rules:
        - Fields (restaurant, day_of_week, start, end) are required.
        - Restaurant must exist.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - end must be greater than start.
        - Provided day_of_week must have an AvailableRule defined for that day..
        - start and end must be consistent with AvailableRule opening/closing times for that day.
        - Restaurant breaks at the same day cannot overlap each other.
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=RestaurantBreakSerializer,
        responses={
            201: OpenApiResponse(description="Restaurant break created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update restaurant break",
        description="""
        Updates restaurant break at provided restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.

        Business rules:
        - Fields (restaurant, day_of_week, start, end) are required.
        - Restaurant must exist.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - end must be greater than start.
        - Provided day_of_week must have an AvailableRule defined for that day.
        - start and end must be consistent with AvailableRule opening/closing times for that day.
        - Restaurant breaks at the same day cannot overlap each other.
        """,
        request=RestaurantBreakSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant break updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant break not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update restaurant break",
        description="""
        Partially updates restaurant break at provided restaurant.
        Only provided fields will be updated, the rest remain unchanged.
        This endpoint is allowed only for owner or manager of the restaurant.

        Validation always checks the full, resulting set of fields (missing fields are taken from the existing instance).

        Business rules:
        - Restaurant must exist.
        - Allowed day_of_week values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday.
        - end must be greater than start.
        - Provided day_of_week must have an AvailableRule defined for that day.
        - start and end must be consistent with AvailableRule opening/closing times for that day.
        - Restaurant breaks at the same day cannot overlap each other.
        """,
        request=RestaurantBreakSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant break updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant break not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class RestaurantExceptionViewSet(viewsets.ModelViewSet):
    """
    The same access rules as AvailableRuleViewSet.
    """

    serializer_class = RestaurantExceptionSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return RestaurantException.objects.filter(
            restaurant__owner=self.request.user
        ) | RestaurantException.objects.filter(restaurant__memberships__user=self.request.user)

    @extend_schema(
        summary="Create restaurant exception",
        description="""
        Creates restaurant exception at provided date and restaurant.
        Model RestaurantException is used in special days when owner/manager want to change basic
        opening and closing time to different one or close whole restaurant at that day.
        This endpoint is allowed only for owner or manager of the restaurant.

        Business rules:
        - Fields (restaurant, date, type) are required.
        - Restaurant must exist.
        - Date cannot be in the past.
        - Allowed type values: "closed", "special_hours".
        - If type = "special_hours" fields (opening_time, closing_time) are required.
        - If type = "closed" fields (opening_time, closing_time) must be empty.
        - Combination of the restaurant and date must be unique (only one exception per day).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=RestaurantExceptionSerializer,
        responses={
            201: OpenApiResponse(description="Restaurant exception created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update restaurant exception",
        description="""
        Updates restaurant exception at provided date and restaurant.
        This endpoint is allowed only for owner or manager of the restaurant.

        Business rules:
        - Fields (restaurant, date, type) are required.
        - Restaurant must exist.
        - Date cannot be in the past.
        - Allowed type values: "closed", "special_hours".
        - If type = "special_hours" fields (opening_time, closing_time) are required.
        - If type = "closed" fields (opening_time, closing_time) must be empty.
        - Combination of the restaurant and date must be unique (only one exception per day).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=RestaurantExceptionSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant exception updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant exception not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update restaurant exception",
        description="""
        Partially updates restaurant exception at provided date and restaurant.
        Only provided fields will be updated, the rest remain unchanged.
        This endpoint is allowed only for owner or manager of the restaurant.

        If type is not being changed, opening_time/closing_time are taken from the existing instance
        when not provided in the request body.

        If type is being changed, opening_time and closing_time are not taken from the existing
        instance - they must be explicitly provided in the request body when changing to
        "special_hours", or explicitly left empty when changing to "closed". This prevents stale
        hours from the previous type leaking into the new one.

        Business rules:
        - Restaurant must exist.
        - Date cannot be in the past.
        - Allowed type values: "closed", "special_hours".
        - If resulting type = "special_hours" fields (opening_time, closing_time) are required.
        - If resulting type = "closed" fields (opening_time, closing_time) must be empty.
        - Combination of the restaurant and date must be unique (only one exception per day).
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=RestaurantExceptionSerializer,
        responses={
            200: OpenApiResponse(description="Restaurant exception updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Restaurant exception not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
