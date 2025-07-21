from django.shortcuts import render
from rest_framework.views import APIView
from users.permissions import IsAdmin
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from django.core.cache import cache
from app.filters import ProductFilter  # You must create this
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from users.models import CustomerProfile

class CategoryAPIView(APIView):
    permission_classes = [IsAdmin]
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def patch(self, request):
        category_id = request.data.get('category_id')
        try:
            category = Category.objects.get(id=category_id, created_by=request.user)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteCategory(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request):
        category_id = request.query_params.get('id')
        if not category_id:
            return Response({'error': 'Category ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id, created_by=request.user)
            category.delete()
            return Response({'message': 'Category deleted successfully.'}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)
        
class ListCategory(APIView):
    def get(self, request):
        cache_key = "category_list"
        data = cache.get(cache_key)

        if not data:
            queryset = Category.objects.all()
            serializer = CategorySerializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=60 * 60)

        return Response(data, status=status.HTTP_200_OK)

    
    
class ProductAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user) 
            cache.delete("product_list")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        product_id = request.data.get('id')
        try:
            product = Product.objects.get(id=product_id, created_by=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete("product_list")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class DeleteProduct(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request):
        product_id = request.query_params.get('id')
        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Product.objects.get(id=product_id, created_by=request.user)
            category.delete()
            cache.delete("product_list")
            return Response({'message': 'Product deleted successfully.'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found or access denied.'}, status=status.HTTP_404_NOT_FOUND)



class ProductListAPIView(APIView):
    def get(self, request):
        # Caching based on URL and query parameters
        cache_key = f"product_list:{request.get_full_path()}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # Base queryset
        queryset = Product.objects.select_related('category').all()

        # Apply filters using custom ProductFilter
        product_filter = ProductFilter(request.GET, queryset=queryset)
        filtered_qs = product_filter.qs

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(filtered_qs, request)

        # Serialize paginated results
        serializer = ProductSerializer(result_page, many=True)
        response_data = {
            "total_pages": paginator.page.paginator.num_pages,
            "current_page": paginator.page.number,
            "total_products": paginator.page.paginator.count,
            "results": serializer.data
        }

        # Cache final response
        cache.set(cache_key, response_data, timeout=60 * 60)  # Cache for 1 hour
        return Response(response_data)


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        try:
            profile = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=404)

        product_data = request.data.get('products')  # list of {product_id, quantity}
        if not product_data:
            return Response({"error": "No products provided"}, status=400)

        order = Order.objects.create(user=profile, total_price=0)

        total_price = 0
        for item in product_data:
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                return Response({"error": f"Product {item['product_id']} not found"}, status=404)

            quantity = int(item.get('quantity', 1))
            if product.stock < quantity:
                return Response({"error": f"Insufficient stock for product {product.name}"}, status=400)

            product.decrease_stock(quantity)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price  
            )

            total_price += product.price * quantity

        order.total_price = total_price
        order.save()

        return Response({"message": "Order placed successfully", "order_id": str(order.id)}, status=201)
    

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request):
        order_id = request.data.get("order_id")
        new_status = request.data.get("status")

        if new_status not in ['pending', 'shipped', 'delivered']:
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Business rule
        if order.status == "pending" and new_status == "shipped":
            order.status = "shipped"
        elif order.status == "shipped" and new_status == "delivered":
            order.status = "delivered"
        elif order.status == new_status:
            return Response({"error": "Order already in this status"}, status=400)
        else:
            return Response({"error": f"Cannot change status from {order.status} to {new_status}"}, status=400)

        order.save()

        # ✅ Send real-time WebSocket message to the user
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{order.user.user.id}",  # user.id, not profile.id
            {
                "type": "order_status_update",
                "message": f"Your order {order.id} is now {order.status}"
            }
        )

        return Response({"message": f"Order status updated to {new_status}"})
    
    
class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = CustomerProfile.objects.get(user=request.user)
        orders = Order.objects.filter(user=profile).prefetch_related("orderitem_set__product")

        # Setup pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # or any page size you prefer
        paginated_orders = paginator.paginate_queryset(orders, request)

        serializer = OrderListSerializer(paginated_orders, many=True)
        
        return paginator.get_paginated_response(serializer.data)
