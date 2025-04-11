from django.core.paginator import Paginator
from hortifruti.models import VendasModel
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count  
from django.utils import timezone
from datetime import datetime, timedelta



class Repository:


  def listarUltimasVendas(self, request):
        lista_vendas = VendasModel.objects.all().order_by('-id_venda')  # Ordena por ID decrescente

        # Configurar a paginação - 10 itens por página
        paginator = Paginator(lista_vendas, 11)  # Você pode ajustar o número de itens por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'vendas': page_obj,
            'paginator': paginator,
            'is_paginated': True,
        }
        return context

  def registrarVendas(self, request):

        nova_venda = VendasModel()
        nova_venda.id_venda = request.POST.get('id_venda')
        nova_venda.valor = request.POST.get('valor')
        nova_venda.data = request.POST.get('data')
        nova_venda.save()

        return nova_venda


  def obterVenda(self, id_venda):
        """Obtém uma venda específica pelo ID para edição"""
        return get_object_or_404(VendasModel, id_venda=id_venda)


  def editarVenda(self, request, id_venda):
      """Atualiza os dados de uma venda existente"""
      venda = self.obterVenda(id_venda)
      venda.valor = request.POST.get('valor')
      venda.data = request.POST.get('data')
      venda.save()

      return venda


  def removerVenda(self, id_venda):
      """Remove uma venda pelo ID"""
      venda = self.obterVenda(id_venda)
      venda.delete()

      return True


  def relatorioVendas(self, request):
        """
        Gera relatório de vendas com filtro opcional por período
        Suporta DateTime para filtragem precisa incluindo horas
        """
        # Obtém parâmetros do request
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')

        # Inicializa a query
        queryset = VendasModel.objects.all().order_by('-data')

        # Aplica filtros se fornecidos
        if data_inicial:
            try:
                # Converte a string para datetime
                data_inicial_dt = datetime.fromisoformat(data_inicial.replace('T', ' '))
                queryset = queryset.filter(data__gte=data_inicial_dt)
            except (ValueError, TypeError):
                # Em caso de erro de formato, ignora o filtro
                pass

        if data_final:
            try:
                # Converte a string para datetime e adiciona 1 dia para incluir o dia final completo
                data_final_dt = datetime.fromisoformat(data_final.replace('T', ' '))
                # Adiciona 23:59:59 para incluir o dia inteiro
                data_final_dt = data_final_dt.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(data__lte=data_final_dt)
            except (ValueError, TypeError):
                # Em caso de erro de formato, ignora o filtro
                pass

        # Calcula estatísticas se houver vendas
        estatisticas = {}
        if queryset.exists():
            resultado = queryset.aggregate(
                qtd_vendas=Count('id_venda'),
                valor_total=Sum('valor'),
                valor_medio=Avg('valor')
            )
            estatisticas = {
                'qtd_vendas': resultado['qtd_vendas'],
                'valor_total': resultado['valor_total'],
                'valor_medio': resultado['valor_medio']
            }
        else:
            estatisticas = {
                'qtd_vendas': 0,
                'valor_total': 0,
                'valor_medio': 0
            }

        # Configurar a paginação
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Prepara contexto para o template
        context = {
            'vendas': page_obj,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'is_paginated': True,
            'qtd_vendas': estatisticas['qtd_vendas'],
            'valor_total': estatisticas['valor_total'],
            'valor_medio': estatisticas['valor_medio']
        }

        return context