from rest_framework import serializers
from products.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
        )


class OrderCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_product(self, obj):
        return obj.product.name

    def get_user(self, obj):
        return obj.user.name

    def get_amount(self, obj):
        return obj.product.price * obj.quantity

    class Meta:
        model = Order
        fields = (
            "unique_link",
            "product",
            "user",
            "quantity",
            "amount",
        )