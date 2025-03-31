"""
URL configuration for projeto_hortifruti project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.views.generic import TemplateView
from hortifruti import views
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('registrar/', views.registrarVendas, name='registrar_vendas'),
    path('gerenciadorvendas/', views.gerenciadorPage, name='gerenciador_Page'),
    path('vendas/editar/<int:id_venda>/', views.editar_venda, name='editar_venda'),
    path('vendas/remover/<int:id_venda>/', views.remover_venda, name='remover_venda'),
    path('vendas/', views.listar_vendas, name='listar_vendas'),
]
