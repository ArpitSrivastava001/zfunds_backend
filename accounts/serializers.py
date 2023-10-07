from rest_framework import serializers
from accounts.models import User, UserType

user_type_choices = (
    (UserType.ADVISOR, 'Advisor'),
    (UserType.CLIENT, 'Client'),
)

class SendOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=10, min_length=10)
    user_type = serializers.ChoiceField(choices=user_type_choices)

class VerifyOTPSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, min_length=3, required=False)
    mobile_number = serializers.CharField(max_length=10, min_length=10)
    otp = serializers.CharField(max_length=6, min_length=6)
    user_type = serializers.ChoiceField(choices=user_type_choices)
    is_new_user = serializers.BooleanField()

    def validate(self,data):
        is_new_user = data.get('is_new_user')
        name = data.get('name')

        if is_new_user and not name:
            raise serializers.ValidationError("Name is required for new user")

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "mobile_number",
            "user_type",
        )