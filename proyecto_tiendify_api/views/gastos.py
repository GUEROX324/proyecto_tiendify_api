from datetime import datetime
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from ..models import Gasto
from ..serializers import GastoSerializer


def _parse_date(param: str):
    if not param:
        return None
    try:
        return datetime.strptime(param, "%Y-%m-%d").date()
    except Exception:
        return None


class GastosView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        s = GastoSerializer(data=request.data)
        if s.is_valid():
            gasto = s.save()  
            return Response(GastoSerializer(gasto).data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


class GastosAll(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        q = (request.GET.get('q') or '').strip()
        tipo = (request.GET.get('tipo') or '').strip()   
        start = _parse_date(request.GET.get('start'))
        end   = _parse_date(request.GET.get('end'))

        qs = Gasto.objects.all().order_by('-fecha')

        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(notas__icontains=q))
        if tipo:
            qs = qs.filter(tipo__iexact=tipo)
        if start:
            qs = qs.filter(fecha__date__gte=start)
        if end:
            qs = qs.filter(fecha__date__lte=end)

        data = GastoSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class GastosEditView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_obj(self, request):
        try:
            _id = int(request.GET.get('id'))
        except Exception:
            _id = None
        if not _id:
            return None
        try:
            return Gasto.objects.get(id=_id)
        except Gasto.DoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        obj = self.get_obj(request)
        if not obj:
            return Response({'detail': 'id inválido'}, status=status.HTTP_400_BAD_REQUEST)

        s = GastoSerializer(obj, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(s.data, status=status.HTTP_200_OK)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        obj = self.get_obj(request)
        if not obj:
            return Response({'detail': 'id inválido'}, status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
