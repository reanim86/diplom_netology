"""
URL configuration for diplom_netology project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend.views import UploadData, CreateUser, UserEnter, ProductAPI, ProductDetail, Basket, OrderViews

router = DefaultRouter()
router.register('products', ProductAPI)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', UploadData.as_view()),
    path('createuser/', CreateUser.as_view()),
    path('enter/', UserEnter.as_view()),
    # path('products/', ProductAPI.as_view()),
    path('api/', include(router.urls)),
    path('productcard/<int:id>/', ProductDetail.as_view()),
    path('basket/<int:id>/', Basket.as_view()),
    path('basket/', Basket.as_view()),
    path('order/', OrderViews.as_view()),
    path('order/<int:id>/', OrderViews.as_view()),
]
