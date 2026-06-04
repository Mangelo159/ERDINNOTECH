from django.urls import path, include
from diagrams.views import editor

urlpatterns = [
    path('', editor, name='editor'),
    path('api/', include('diagrams.urls')),
]
