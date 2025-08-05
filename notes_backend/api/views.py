from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from .models import Note, Category
from .serializers import (
    UserSerializer, RegisterUserSerializer, LoginUserSerializer,
    NoteSerializer, CategorySerializer, NoteSearchResultSerializer
)

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Simple health check endpoint."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """
    Registers a new user.
    """
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "Registration successful."
        }, status=status.HTTP_201_CREATED)

# PUBLIC_INTERFACE
class LoginView(APIView):
    """
    Logs a user in and returns user info.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.data['username'], password=serializer.data['password'])
        if user:
            login(request, user)
            data = {
                "message": "Login successful.",
                "user": UserSerializer(user).data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

# PUBLIC_INTERFACE
class LogoutView(APIView):
    """
    Logs out the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

# PUBLIC_INTERFACE
class NoteViewSet(viewsets.ModelViewSet):
    """
    CRUD API for personal notes.
    List and retrieve only notes for the requesting user.
    """
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# PUBLIC_INTERFACE
class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for note categories, only for the current user.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# PUBLIC_INTERFACE
class NoteSearchView(generics.ListAPIView):
    """
    Search endpoint for notes.
    """
    serializer_class = NoteSearchResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.request.query_params.get('q', '')
        cat = self.request.query_params.get('category', None)
        qs = Note.objects.filter(user=user)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
        if cat:
            qs = qs.filter(category__id=cat)
        return qs.order_by('-updated_at')
