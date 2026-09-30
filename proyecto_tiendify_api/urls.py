"""point_experts_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from proyecto_tiendify_api.views import bootstrap
from proyecto_tiendify_api.views import users
from proyecto_tiendify_api.views import auth
from proyecto_tiendify_api.views import trabajadores
from proyecto_tiendify_api.views import master
from proyecto_tiendify_api.views import productos
from proyecto_tiendify_api.views import ventas
from proyecto_tiendify_api.views import gastos
from proyecto_tiendify_api.views import stats
from proyecto_tiendify_api.views import caja

urlpatterns = [
    #Version
        path('bootstrap/version', bootstrap.VersionView.as_view()),
    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        path('admins-edit/', users.AdminsViewEdit.as_view()),
    #Create Trabajador
        path('trabajadores/', trabajadores.TrabajadoresView.as_view()),
    #Trabajador Data
        path('lista-trabajadores/', trabajadores.TrabajadoresAll.as_view()),
    #Edit Trabajador
        path('trabajadores-edit/', trabajadores.TrabajadoresViewEdit.as_view()),
    #Create Master
        path('master/', master.MasterView.as_view()),
    #Master Data
        path('lista-master/', master.MasterAll.as_view()),
    #Edit Master
        path('master-edit/', master.MasterViewEdit.as_view()),
    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view()),
    #Get lista
        path('products/', productos.ProductsView.as_view()),
    #Get por id       
        path('product/', productos.ProductDetailView.as_view()),
    #Edit    
        path('products-edit/', productos.ProductsEditView.as_view()),
    #Ventas
        path('ventas/', ventas.VentasView.as_view()),

        path('lista-ventas/', ventas.VentasAll.as_view()),

        path('gastos/', gastos.GastosView.as_view()), 

        path('lista-gastos/', gastos.GastosAll.as_view()), 

        path('gastos-edit/', gastos.GastosEditView.as_view()), 

        path('stats-ventas/', stats.StatsVentasView.as_view()),     

        path('stats-ingresos-egresos/', stats.StatsIngresosEgresosView.as_view()),

        path('caja/resumen/', caja.CajaResumenView.as_view()),

        path('caja/ingreso/', caja.CajaIngresoView.as_view()),

        path('lista-ingresos/', caja.IngresosAll.as_view()), 
]