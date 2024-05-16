import csv

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse

from .models import FlowerList, Cart, Order, Promocode
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(FlowerList)
class FlowerAdmin(admin.ModelAdmin):
    search_fields = "name", "id"
    actions = [
        mark_archived,
        mark_unarchived,
    ]

    list_display = "pk", "name", "description_short", "archived", "number_of_uses"
    list_display_links = "pk", "name"
    ordering = ("id",)

    fieldsets = [
        (None, {
           "fields": ("name", "description")
        }),
        ("Price options", {
            "fields": ("price", "number_of_uses")
        }),
        ("Extra options", {
            "fields": ("archived", "category", "image"),
            "classes": ("collapse",),
            "description": "Дополнительные опции"
        }),
    ]

    def description_short(self, obj: FlowerList) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."



@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    search_fields = ("products__name", "products__id",)
    list_display = "pk", "user", "display_products"
    list_display_links = "pk", "user"
    ordering = ("id",)

    def display_products(self, obj):
        return ', '.join(product.name for product in obj.products.all())

    display_products.short_description = 'Товары в корзине'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shop_app/products_changelist.html"
    search_fields = ("products__name", "products__id",)
    list_display = "pk", "delivery_adress", "phone", "created_at", "final_sum"
    list_display_links = "pk",
    ordering = ("id",)


class CustomUserAdmin(UserAdmin):
    list_display = ('pk', 'username', 'email', 'get_orders')
    list_display_links = ("pk", "username")

    def get_orders(self, obj):
        return Order.objects.filter(user=obj).count()

    def orders_list(self, obj):
        orders = Order.objects.filter(user=obj)
        orders_info = []
        for order in orders:
            order_info = ', '.join(f"ID: {product.pk}, {product.name}" for product in order.products.all().selected_related("user").prefetch_related("products"))
            orders_info.append(f"Состав заказа: {order.pk} - {order_info}\n")
        return ''.join(orders_info)

    get_orders.short_description = 'Количество заказов'

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('orders_list',),
        }),
    )

    readonly_fields = ('orders_list',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Promocode)