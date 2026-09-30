from datetime import datetime
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from ..models import Venta, Gasto


def _parse_date(param: str):
    if not param:
        return None
    try:
        return datetime.strptime(param, "%Y-%m-%d").date()
    except Exception:
        return None


class StatsVentasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start = _parse_date(request.GET.get('start'))
        end   = _parse_date(request.GET.get('end'))

        ventas = Venta.objects.all()
        if start:
            ventas = ventas.filter(fecha__date__gte=start)
        if end:
            ventas = ventas.filter(fecha__date__lte=end)

        agg = ventas.aggregate(
            subtotal=Sum('subtotal'),
            iva=Sum('iva'),
            total=Sum('total')
        )
        subtotal = float(agg.get('subtotal') or 0)
        iva      = float(agg.get('iva') or 0)
        total    = float(agg.get('total') or 0)

        data = {
            "rango": {
                "start": start.isoformat() if start else None,
                "end":   end.isoformat() if end else None,
            },
            "sin_iva": round(subtotal, 2),
            "iva":     round(iva, 2),
            "con_iva": round(total, 2),
        }
        return Response(data, status=status.HTTP_200_OK)


class StatsIngresosEgresosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start = _parse_date(request.GET.get('start'))
        end   = _parse_date(request.GET.get('end'))

        ventas = Venta.objects.all()
        gastos = Gasto.objects.all()

        if start:
            ventas = ventas.filter(fecha__date__gte=start)
            gastos = gastos.filter(fecha__date__gte=start)
        if end:
            ventas = ventas.filter(fecha__date__lte=end)
            gastos = gastos.filter(fecha__date__lte=end)

        agg_v = ventas.aggregate(
            subtotal=Sum('subtotal'),
            iva=Sum('iva'),
            total=Sum('total')
        )
        agg_g = gastos.aggregate(
            egresos=Sum('monto')
        )

        subtotal = float(agg_v.get('subtotal') or 0)
        iva      = float(agg_v.get('iva') or 0)
        total    = float(agg_v.get('total') or 0)
        egresos  = float(agg_g.get('egresos') or 0)

        data = {
            "rango": {
                "start": start.isoformat() if start else None,
                "end":   end.isoformat() if end else None,
            },
            "ventas_sin_iva": round(subtotal, 2),
            "iva":             round(iva, 2),
            "ventas_con_iva":  round(total, 2),
            "egresos":         round(egresos, 2),
            "utilidad_neta":   round(total - egresos, 2)
        }
        return Response(data, status=status.HTTP_200_OK)
