from decimal import Decimal
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Q
from rest_framework import status, permissions

from proyecto_tiendify_api.models import Venta, Gasto, CajaMovimiento

class CajaResumenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        vendido = Venta.objects.aggregate(s=Sum('total'))['s'] or Decimal('0')
        gastado = Gasto.objects.aggregate(s=Sum('monto'))['s'] or Decimal('0')
        ingresos_directos = CajaMovimiento.objects.filter(tipo='INGRESO').aggregate(s=Sum('monto'))['s'] or Decimal('0')
        retiros = CajaMovimiento.objects.filter(tipo='RETIRO').aggregate(s=Sum('monto'))['s'] or Decimal('0')

        # Caja disponible = ventas + ingresos directos - gastos - retiros
        saldo = vendido + ingresos_directos - gastado - retiros

        return Response({
            'vendido': str(vendido),
            'gastado': str(gastado),
            'ingresos_directos': str(ingresos_directos),
            'retiros': str(retiros),
            'saldo': str(saldo),
        }, status=status.HTTP_200_OK)


class CajaIngresoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        monto = request.data.get('monto')
        nota = (request.data.get('nota') or '').strip()

        try:
            monto = Decimal(str(monto))
        except Exception:
            return Response({'detail': 'monto inválido'}, status=status.HTTP_400_BAD_REQUEST)

        if monto <= 0:
            return Response({'detail': 'monto debe ser > 0'}, status=status.HTTP_400_BAD_REQUEST)

        # ¡Forzamos tipo=INGRESO! (ignoramos cualquier "tipo" que mande el cliente)
        mov = CajaMovimiento.objects.create(
            monto=monto,
            tipo='INGRESO',
            nota=nota or None
        )
        return Response({'id': mov.id, 'monto': str(monto), 'tipo': mov.tipo}, status=status.HTTP_201_CREATED)

def _parse_date(param: str):
    if not param:
        return None
    try:
        return datetime.strptime(param, "%Y-%m-%d").date()
    except Exception:
        return None

class IngresosAll(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        q = (request.GET.get('q') or '').strip()
        start = _parse_date(request.GET.get('start'))
        end   = _parse_date(request.GET.get('end'))

        qs = CajaMovimiento.objects.filter(tipo='INGRESO').order_by('-fecha')
        if q:
            qs = qs.filter(
                Q(nota__icontains=q)
                | Q(monto__icontains=q)
                | Q(fecha__icontains=q)
            )
        if start:
            qs = qs.filter(fecha__date__gte=start)
        if end:
            qs = qs.filter(fecha__date__lte=end)

        data = [{
            'id': m.id,
            'monto': str(m.monto),
            'nota': m.nota,
            'fecha': m.fecha.isoformat()
        } for m in qs]

        return Response(data, status=status.HTTP_200_OK)