from django.contrib import admin
from django.urls import path, include
from LittleLemonAPI.views import (
    MenuItemDetail,
    MenuItemList,
    home,
    ManagerGroupView,
    DeliveryCrewGroupView,
    CartView,
    OrderList,
    OrderDetail
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta al panel de administración
    path('', home, name='home'),  # Ruta para la raíz
    path('api/menu-items/', MenuItemList.as_view(), name='menu-item-list'),  # Lista todos los menú items y permite POST
    path('api/menu-items/<int:pk>/', MenuItemDetail.as_view(), name='menu-item-detail'),  # Detalle, GET, DELETE
    path('api/groups/manager/users/', ManagerGroupView.as_view(), name='manager-group'),  # Manager group
    path('api/groups/manager/users/<int:userId>/', ManagerGroupView.as_view(), name='manager-group-detail'),  # Manager group detalle
    path('api/groups/delivery-crew/users/', DeliveryCrewGroupView.as_view(), name='delivery-crew-group'),  # Delivery crew group
    path('api/groups/delivery-crew/users/<int:userId>/', DeliveryCrewGroupView.as_view(), name='delivery-crew-group-detail'),  # Delivery crew detalle
    path('api/cart/menu-items/', CartView.as_view(), name='cart-management'),  # Gestión del carrito
    path('api/orders/', OrderList.as_view(), name='order-list'),  # Lista y creación de órdenes
    path('api/orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),  # Detalle y actualización de órdenes
    path('api/auth/', include('djoser.urls')),  # Rutas básicas de Djoser
    path('api/auth/', include('djoser.urls.authtoken')),  # Rutas de autenticación con tokens
]
