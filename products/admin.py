from django.contrib import admin
from .models import Category, Product, Order


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'category', 'is_active')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    fields = ('name', 'description', 'price', 'category', 'is_active')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'user', 'unique_link', 'is_active')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    fields = ('product', 'quantity', 'user', 'unique_link', 'is_active')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)