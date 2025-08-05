from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Note, Category

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """User serializer - exposes username and id."""
    class Meta:
        model = User
        fields = ('id', 'username')

# PUBLIC_INTERFACE
class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

# PUBLIC_INTERFACE
class LoginUserSerializer(serializers.Serializer):
    """Serializer for logging a user in."""
    username = serializers.CharField()
    password = serializers.CharField()

# PUBLIC_INTERFACE
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories (CRUD)."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']

# PUBLIC_INTERFACE
class NoteSerializer(serializers.ModelSerializer):
    """Serializer for notes."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at', 'category', 'category_id', 'user'
        ]

# PUBLIC_INTERFACE
class NoteSearchResultSerializer(serializers.ModelSerializer):
    """Search result serializer for Note."""
    class Meta:
        model = Note
        fields = ["id", "title", "content", "category", "created_at", "updated_at"]
