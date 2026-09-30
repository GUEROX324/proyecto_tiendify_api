from decimal import Decimal
from django.db import transaction
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal, InvalidOperation  
from rest_framework import status, permissions  

from proyecto_tiendify_api.models import Producto, Venta, VentaDetalle

class VentasView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data

        # Validación mínima (puedes endurecer si gustas)
        items = data.get('items') or []
        if not items:
            return Response({'detail': 'Sin items.'}, status=status.HTTP_400_BAD_REQUEST)

        ids = [it['producto_id'] for it in items]
        productos = {p.id: p for p in Producto.objects.select_for_update().filter(id__in=ids)}

        # Valida stock suficiente
        for it in items:
            p = productos.get(it['producto_id'])
            if not p:
                return Response({'detail': f"Producto {it['producto_id']} no existe"}, status=400)
            if p.stock < int(it['cantidad']):
                return Response(
                    {'detail': f"Sin stock suficiente para {p.nombre}", 'producto_id': p.id, 'stock': p.stock},
                    status=409
                )

        # Crea la venta
        venta = Venta.objects.create(
            subtotal=Decimal(str(data.get('subtotal', '0'))),
            iva=Decimal(str(data.get('iva', '0'))),
            total=Decimal(str(data.get('total', '0'))),
            recibido=Decimal(str(data.get('recibido', '0'))),
            cambio=Decimal(str(data.get('cambio', '0'))),
        )

        # Crea detalles y **RESTAR** stock
        for it in items:
            p = productos[it['producto_id']]
            cant = int(it['cantidad'])
            precio = Decimal(str(it['precio_unit']))
            importe = precio * cant

            VentaDetalle.objects.create(
                venta=venta, producto=p, cantidad=cant, precio_unit=precio, importe=importe
            )
            Producto.objects.filter(id=p.id).update(stock=F('stock') - cant)

        return Response({'detail': 'Venta registrada', 'venta_id': venta.id}, status=201)
    
class VentasAll(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = Venta.objects.all().order_by('-fecha')

        q = (request.GET.get('q') or '').strip()
        if q:
            try:
                num = Decimal(q)
                qs = qs.filter(total__gte=(num - Decimal('0.01')),
                               total__lte=(num + Decimal('0.01')))
            except (InvalidOperation, TypeError):
                # Si no es número, no se filtra (no hay campo texto para buscar)
                pass

        data = [{
            'id': v.id,
            'subtotal': str(v.subtotal),
            'iva': str(v.iva),
            'total': str(v.total),
            'recibido': str(v.recibido),
            'cambio': str(v.cambio),
            'fecha': v.fecha
        } for v in qs]

        return Response(data, status=status.HTTP_200_OK)