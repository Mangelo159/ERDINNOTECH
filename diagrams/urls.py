from django.urls import path
from . import views

urlpatterns = [
    path('diagrams/', views.diagram_list, name='diagram-list'),
    path('diagrams/<int:pk>/', views.diagram_detail, name='diagram-detail'),
    path('diagrams/<int:pk>/sql/', views.diagram_sql, name='diagram-sql'),
]
