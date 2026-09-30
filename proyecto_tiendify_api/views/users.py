from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from proyecto_tiendify_api.serializers import *
from proyecto_tiendify_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class AdminAll(generics.CreateAPIView):
    # Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active=1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    # Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data

        return Response(admin, 200)
    
    # Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Todas estas líneas hasta la 80 es para guardar en la tabla authUser
        user = UserSerializer(data=request.data)
        if user.is_valid():
            # Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            # Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message": "Username " + email + ", is already taken"}, 400)

            user = User.objects.create(username=email,
                                       email=email,
                                       first_name=first_name,
                                       last_name=last_name,
                                       is_active=1)

            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # Guardamos los datos adicionales en la tabla correspondiente
            # Create a profile for the user
            admin = Administradores.objects.create(user=user,
                                                   clave_admin=request.data["clave_admin"],
                                                   telefono=request.data["telefono"],
                                                   rfc=request.data["rfc"].upper(),
                                                   edad=request.data["edad"],)
            admin.save()

            return Response({"admin_created_id": admin.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminsViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    # Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # Obtener total de admins
        admin = Administradores.objects.filter(user__is_active=1).order_by("id")
        lista_admins = AdminSerializer(admin, many=True).data
        total_admins = len(lista_admins)

        # Obtener total de master
        master = Master.objects.filter(user__is_active=1).order_by("id")
        lista_master = MasterSerializer(master, many=True).data
        if not lista_master:
            return Response({}, 400)
        for master in lista_master:
            total_master = len(lista_master)

        # Obtener total de Trabajadores
        trabajadores = Trabajadores.objects.filter(user__is_active=1).order_by("id")
        lista_trabajadores = TrabajadoresSerializer(trabajadores, many=True).data
        total_trabajadores = len(lista_trabajadores)

        return Response({'admins': total_admins, 'master': total_master, 'trabajadores': total_trabajadores}, 200)
    
    # Editar administrador
    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.save()
        temp = admin.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = AdminSerializer(admin, many=False).data

        return Response(user, 200)
    
    # Eliminar administrador
    def delete(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            admin.user.delete()
            return Response({"details": "Administrador eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)