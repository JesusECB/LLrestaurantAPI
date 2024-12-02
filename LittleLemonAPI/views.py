from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group, User
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, MenuItem, Order, OrderItem
from .serializers import MenuItemSerializer
from django.http import HttpResponse
from rest_framework.exceptions import NotFound



def home(request):
    return HttpResponse("""
        <html>
            <head><title>Little Lemon API</title></head>
            <body>
                <h1 style="text-align: center; color: #4CAF50;">Bienvenido a Little Lemon API</h1>
                <p style="text-align: center;">Explora nuestro menú utilizando los endpoints disponibles.</p>
            </body>
        </html>
    """)


class MenuItemList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_staff:  # Solo los administradores pueden agregar ítems
            return Response(
                {"error": "You do not have permission to add menu items"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            raise NotFound(detail="Menu item not found")  # 404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if not request.user.is_staff:  # Solo los administradores pueden eliminar ítems
            return Response(
                {"error": "You do not have permission to delete menu items"},
                status=status.HTTP_403_FORBIDDEN
            )
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manager_group = get_object_or_404(Group, name='Manager')
        managers = manager_group.user_set.all()
        data = [{"id": user.id, "username": user.username, "email": user.email} for user in managers]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        manager_group = get_object_or_404(Group, name='Manager')
        manager_group.user_set.add(user)
        return Response({"message": f"User {user.username} added to Manager group"}, status=status.HTTP_201_CREATED)

    def delete(self, request, userId):
        manager_group = get_object_or_404(Group, name='Manager')
        user = get_object_or_404(User, id=userId)
        manager_group.user_set.remove(user)
        return Response({"message": f"User {user.username} removed from Manager group"}, status=status.HTTP_200_OK)


class DeliveryCrewGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        delivery_group = get_object_or_404(Group, name='Delivery Crew')
        crew_members = delivery_group.user_set.all()
        data = [{"id": user.id, "username": user.username, "email": user.email} for user in crew_members]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        delivery_group = get_object_or_404(Group, name='Delivery Crew')
        delivery_group.user_set.add(user)
        return Response({"message": f"User {user.username} added to Delivery Crew group"}, status=status.HTTP_201_CREATED)

    def delete(self, request, userId):
        delivery_group = get_object_or_404(Group, name='Delivery Crew')
        user = get_object_or_404(User, id=userId)
        delivery_group.user_set.remove(user)
        return Response({"message": f"User {user.username} removed from Delivery Crew group"}, status=status.HTTP_200_OK)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        data = [
            {
                "menu_item": cart_item.menu_item.name,
                "quantity": cart_item.quantity,
                "price": float(cart_item.menu_item.price) * cart_item.quantity,
            }
            for cart_item in cart_items
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        menu_item_id = request.data.get("menu_item_id")
        quantity = request.data.get("quantity", 1)
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menu_item=menu_item,
            defaults={"quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return Response(
            {"message": f"{menu_item.name} added to cart."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        data = [
            {
                "id": order.id,
                "status": order.status,
                "total": order.total,
                "date": order.date,
                "items": [
                    {
                        "menu_item": item.menu_item.name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "price": item.price,
                    }
                    for item in order.items.all()
                ],
            }
            for order in orders
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        total = sum(cart_item.menu_item.price * cart_item.quantity for cart_item in cart_items)
        order = Order.objects.create(user=request.user, total=total)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.menu_item.price,
                price=cart_item.menu_item.price * cart_item.quantity,
            )
        cart_items.delete()
        return Response({"message": "Order placed successfully."}, status=status.HTTP_201_CREATED)

class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        data = [
            {
                "id": order.id,
                "status": order.status,
                "total": order.total,
                "date": order.date,
                "items": [
                    {
                        "menu_item": item.menu_item.name,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "price": float(item.price),
                    }
                    for item in order.items.all()
                ],
            }
            for order in orders
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        cart_items = request.user.cart_items.all()
        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(cart_item.menu_item.price * cart_item.quantity for cart_item in cart_items)
        order = Order.objects.create(user=request.user, total=total)

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.menu_item.price,
                price=cart_item.menu_item.price * cart_item.quantity,
            )

        cart_items.delete()
        return Response({"message": "Order placed successfully."}, status=status.HTTP_201_CREATED)

class OrderDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Obtener detalles de una orden específica
        order = get_object_or_404(Order, pk=pk, user=request.user)
        data = {
            "id": order.id,
            "status": order.status,
            "total": order.total,
            "date": order.date,
            "items": [
                {
                    "menu_item": item.menu_item.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "price": float(item.price),
                }
                for item in order.items.all()
            ],
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        # Actualizar el estado o el delivery crew de la orden
        order = get_object_or_404(Order, pk=pk)
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                {"error": "You do not have permission to modify this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
        status = request.data.get("status")
        delivery_crew_id = request.data.get("delivery_crew_id")
        if status is not None:
            order.status = status
        if delivery_crew_id is not None:
            order.delivery_crew = get_object_or_404(User, id=delivery_crew_id)
        order.save()
        return Response({"message": "Order updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Eliminar una orden (solo para administradores o managers)
        order = get_object_or_404(Order, pk=pk)
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                {"error": "You do not have permission to delete this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
