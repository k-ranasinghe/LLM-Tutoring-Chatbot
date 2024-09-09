from django.urls import path
from .views import upload_material, view_material, view_recent_materials, search_materials, delete_material, add_mentor_notes

urlpatterns = [
    path('material/upload/', upload_material, name='Upload Material'),
    path('material/view/', view_material, name='View Material'),
    path('material/recent/', view_recent_materials, name='View Recent Material'),
    path('material/search/', search_materials, name='Search Material'),
    path('material/delete/<int:pk>/', delete_material, name='Delete Material'),
    path('material/notes/', add_mentor_notes, name='Add Mentor Notes'),
]