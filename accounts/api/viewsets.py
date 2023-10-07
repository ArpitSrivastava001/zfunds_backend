from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, UserType
from accounts.serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer
from base.pagination import CustomPagination
from django.contrib.auth.hashers import make_password, check_password
import random
from django.utils import timezone
import logging


logger = logging.getLogger('django')


class AccountViewSet(viewsets.ViewSet):
    model = User
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        try:
            is_new_user = False
            serializer = SendOTPSerializer(data=request.data)
            if serializer.is_valid():
                mobile_number = serializer.validated_data['mobile_number']
                user_type = serializer.validated_data['user_type']
                logger.info(f'Send OTP: {mobile_number} {user_type}')
                otp = str(random.randint(100000, 999999))
                otp_created_at = timezone.now()
                hashed_otp = make_password(otp)
                try:
                    user = self.model.objects.get(mobile_number=mobile_number, user_type=user_type, is_active=True)
                    user.otp_secret_key = hashed_otp
                    user.otp_created_at = otp_created_at
                    user.otp_verified = False
                    user.save()
                except User.DoesNotExist:
                    logger.info(f'New user: {mobile_number} {user_type}')
                    self.model.objects.create(mobile_number=mobile_number, user_type=user_type ,otp_secret_key=hashed_otp, otp_created_at=otp_created_at, otp_verified=False)
                    is_new_user = True
                return Response(
                    {
                        "success": True,
                        "message": "OTP sent successfully",
                        "data": {
                            "mobile_number": serializer.validated_data['mobile_number'],
                            "user_type": user_type,
                            "otp": otp,
                            "is_new_user": is_new_user
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f'Invalid data: {serializer.errors}')
                return Response(
                    {
                        "success": False,
                        "message": "Invalid Data",
                        "data": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f'Error in send otp: {str(e)}')
            return Response(
                {
                    "success": False,
                    "message": f"Something went wrong with {str(e)}",
                    "data": {}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid():
                mobile_number = serializer.validated_data['mobile_number']
                otp = serializer.validated_data['otp']
                name = serializer.validated_data.get('name', None)
                user_type = serializer.validated_data['user_type']
                is_new_user = serializer.validated_data['is_new_user']
                logger.info(f'Verify OTP: {mobile_number} {user_type}')
                try:
                    user = self.model.objects.get(mobile_number=mobile_number, user_type=user_type, is_active=True)
                except User.DoesNotExist:
                    logger.error(f'User not found: {mobile_number} {user_type}')
                    return Response(
                        {
                            "success": False,
                            "message": "Invalid Mobile Number",
                            "data": {}
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if check_password(otp, user.otp_secret_key):
                    if (timezone.now() - user.otp_created_at).seconds > 300:
                        logger.error(f'OTP expired: {mobile_number} {user_type}')
                        return Response(
                            {
                                "success": False,
                                "message": "OTP expired",
                                "data": {}
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    user.otp_verified = True
                    if is_new_user:
                        user.name = name.title()
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    logger.info(f'OTP verified: {mobile_number} {user_type}')
                    return Response(
                        {
                            "success": True,
                            "message": "OTP verified successfully",
                            "data": {
                                "access_token": str(refresh.access_token),
                                "refresh_token": str(refresh),
                                "user": UserSerializer(user).data
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.error(f'Invalid OTP: {mobile_number} {user_type}')
                    return Response(
                        {
                            "success": False,
                            "message": "Invalid OTP",
                            "data": {}
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(f'Invalid data: {serializer.errors}')
                return Response(
                    {
                        "success": False,
                        "message": "Invalid Data",
                        "data": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f'Error in verify otp: {str(e)}')
            return Response(
                {
                    "success": False,
                    "message": f"Something went wrong with {str(e)}",
                    "data": {}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdvisorViewSet(viewsets.ViewSet):
    model = User
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.all()

    def check_advisor(self, user):
        status = False
        if user.user_type == UserType.ADVISOR:
            status = True
        logger.info(f'Check advisor: {user.name} {status}')
        return status

    @action(detail=False, methods=['get'], url_path='get-clients')
    def get_clients(self, request):
        try:
            user = request.user
            advisor_id = request.query_params.get('advisor_id', user.id)
            if not self.check_advisor(user):
                logger.error(f'Not an advisor: {user.name}')
                return Response(
                    {
                        "success": False,
                        "message": "You are not an advisor",
                        "data": {}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            paginator = CustomPagination()
            logger.info(f'Get clients: {user.name}')
            clients = self.model.objects.filter(user_type=UserType.CLIENT, created_by__id=advisor_id).order_by('-created_at')
            page = paginator.paginate_queryset(clients, request)
            if page is not None:
                serializer = UserSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = UserSerializer(clients, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in get clients: {str(e)}')
            return Response(
                {
                    "success": False,
                    "message": f"Something went wrong with {str(e)}",
                    "data": {}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='add-client')
    def add_client(self, request):
        try:
            user = request.user
            if not self.check_advisor(user):
                logger.error(f'Not an advisor: {user.name}')
                return Response(
                    {
                        "success": False,
                        "message": "You are not an advisor",
                        "data": {}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                mobile_number = serializer.validated_data['mobile_number']
                name = serializer.validated_data['name']
                try:
                    client = self.model.objects.get(mobile_number=mobile_number, user_type=UserType.CLIENT)
                    logger.error(f'Client already exists: {client.name}')
                    return Response(
                        {
                            "success": False,
                            "message": "Client already exists",
                            "data": {}
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except User.DoesNotExist:
                    logger.info(f'Add client: {name}')
                    client = self.model.objects.create(mobile_number=mobile_number, name=name.title(), user_type=UserType.CLIENT, created_by=user)
                    return Response(
                        {
                            "success": True,
                            "message": "Client added successfully",
                            "data": UserSerializer(client).data
                        },
                        status=status.HTTP_200_OK
                    )
            else:
                logger.error(f'Invalid data: {serializer.errors}')
                return Response(
                    {
                        "success": False,
                        "message": "Invalid Data",
                        "data": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f'Error in add client: {str(e)}')
            return Response(
                {
                    "success": False,
                    "message": f"Something went wrong with {str(e)}",
                    "data": {}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )