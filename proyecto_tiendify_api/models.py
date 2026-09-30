from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"

class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin "+self.first_name+" "+self.last_name

class Trabajadores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_trabajador = models.CharField(max_length=255,null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del trabajador "+self.first_name+" "+self.last_name

class Master(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_master = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del master "+self.first_name+" "+self.last_name

class Producto(models.Model):
    id = models.BigAutoField(primary_key=True)
    clave = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=80, blank=True, null=True)
    contenido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unidad = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f'{self.clave} - {self.nombre}'

class Venta(models.Model):
    id = models.BigAutoField(primary_key=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    recibido = models.DecimalField(max_digits=10, decimal_places=2)
    cambio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

class VentaDetalle(models.Model):
    id = models.BigAutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unit = models.DecimalField(max_digits=10, decimal_places=2)
    importe = models.DecimalField(max_digits=10, decimal_places=2)

class Gasto(models.Model):
    id = models.BigAutoField(primary_key=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=40)
    nombre = models.CharField(max_length=120, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

class CajaMovimiento(models.Model):
    id = models.BigAutoField(primary_key=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=16)
    nota = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

class Limpieza(models.Model):
    id= models.BigAutoField(primary_key=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return "Perfil del master "+self.first_name+" "+self.last_name