from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('health/', views.health, name='Health'),

    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    # CRUD for notes and categories
    path('', include(router.urls)),

    # Search
    path('notes/search/', views.NoteSearchView.as_view(), name='notes-search'),
]
