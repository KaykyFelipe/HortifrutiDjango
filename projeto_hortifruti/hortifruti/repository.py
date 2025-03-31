from django.core.paginator import Paginator
from hortifruti.models import VendasModel
from django.shortcuts import get_object_or_404



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