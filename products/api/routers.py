from rest_framework.routers import DefaultRouter
from products.api.viewsets import ProductViewSet, OrderViewSet


router = DefaultRouter()


router.register(r'products', ProductViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')