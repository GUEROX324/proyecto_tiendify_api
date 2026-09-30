from rest_framework import serializers
from rest_framework.authtoken.models import Token
from proyecto_tiendify_api.models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

class TrabajadoresSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Trabajadores
        fields = "__all__"

class MasterSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Master
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'
class GastoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Gasto
        fields = '__all__'
        
class VentaDetalleSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    class Meta:
        model = VentaDetalle
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    detalles = VentaDetalleSerializer(many=True, source='ventadetalle_set', read_only=True)
    class Meta:
        model = Venta
        fields = '__all__'