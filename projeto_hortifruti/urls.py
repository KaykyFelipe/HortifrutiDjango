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
    path('relatorio/', views.relatorioPage, name='relatorio_Page'),  # Nome corrigido para corresponder ao template
    path('vendas/editar/<int:id_venda>/', views.editar_venda, name='editar_venda'),
    path('vendas/remover/<int:id_venda>/', views.remover_venda, name='remover_venda'),
    path('vendas/', views.listar_vendas, name='listar_vendas'),
]