from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from proyecto_tiendify_api.serializers import *
from proyecto_tiendify_api.models import *

class ProductsView(APIView):

    def get(self, request, *args, **kwargs):
        q = (request.GET.get('q') or '').strip()
        qs = Producto.objects.all()
        if q != '':
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(clave__icontains=q)
            )
        qs = qs.order_by('nombre', 'clave')
        data = ProductoSerializer(qs, many=True).data
        return Response(data, 200)
    def post(self, request, *args, **kwargs):
        s = ProductoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, 201)

class ProductDetailView(APIView):
    # GET /product/?id=123
    def get(self, request, *args, **kwargs):
        prod = get_object_or_404(Producto, id=request.GET.get('id'))
        data = ProductoSerializer(prod).data
        return Response(data, 200)

class ProductsEditView(APIView):
    # PUT /products-edit/  { id, ...campos }
    def put(self, request, *args, **kwargs):
        prod = get_object_or_404(Producto, id=request.data['id'])
        s = ProductoSerializer(prod, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, 200)

    # DELETE /products-edit/?id=123
    def delete(self, request, *args, **kwargs):
        prod = get_object_or_404(Producto, id=request.GET.get('id'))
        prod.delete()
        return Response({ 'details': 'Producto eliminado' }, 200)
