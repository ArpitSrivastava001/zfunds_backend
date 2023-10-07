from rest_framework import viewsets
from products.models import Product, Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from products.serializers import ProductSerializer, OrderCreateSerializer, OrderSerializer
from base.pagination import CustomPagination
from accounts.models import UserType
import logging


logger = logging.getLogger('django')


class ProductViewSet(viewsets.ViewSet):
    model = Product
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        try:
            category = request.query_params.get('category')
            queryset = self.model.objects.all()
            if category:
                queryset = queryset.filter(category=category)
            logger.info("Product list")
            paginator = CustomPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = ProductSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = ProductSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Product list error: {str(e)}")
            return Response({
                "success": False,
                "message": f"Someting went wrong. {str(e)}",
                "data": {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class OrderViewSet(viewsets.ViewSet):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            order = self.model.objects.get(unique_link=kwargs['pk'], is_active=True)
            logger.info("Order detail")
            return Response({
                "success": True,
                "message": "Order detail",
                "data": OrderSerializer(order).data
            },
            status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Order detail error: {str(e)}")
            return Response({
                "success": False,
                "message": "Order not found",
                "data": {}
            },
            status=status.HTTP_404_NOT_FOUND
        )


    def create(self, request):
        try:
            if request.user.user_type != UserType.CLIENT:
                logger.error(f"Order create error: Only client can create order")
                return Response({
                    "success": False,
                    "message": "Only client can create order",
                    "data": {}
                },
                status=status.HTTP_403_FORBIDDEN
            )
            serializer = OrderCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            order = Order.objects.create(
                product=product,
                quantity=quantity,
                user=request.user
            )
            logger.info("Order created successfully")
            return Response({
                "success": True,
                "message": "Order created successfully",
                "data": OrderSerializer(order).data
            },
            status=status.HTTP_201_CREATED
        )
        except Exception as e:
            logger.error(f"Order create error: {str(e)}")
            return Response({
                "success": False,
                "message": f"Someting went wrong. {str(e)}",
                "data": {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def list(self, request):
        try:
            user = request.user
            if user.user_type == UserType.CLIENT:
                queryset = self.model.objects.filter(user=user, is_active=True)
            elif user.user_type == UserType.ADVISOR:
                queryset = self.model.objects.filter(user__created_by=user, is_active=True)
            logger.info("Order list")
            paginator = CustomPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = OrderSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = OrderSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Order list error: {str(e)}")
            return Response({
                "success": False,
                "message": f"Someting went wrong. {str(e)}",
                "data": {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )