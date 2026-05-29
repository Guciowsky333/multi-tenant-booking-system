# Register your models here.
from django.contrib import admin

from memberships.models import MemberShip


@admin.register(MemberShip)
class MemberShipAdmin(admin.ModelAdmin):
    list_display = (
        "user__email",
        "restaurant__name",
        "role",
    )
