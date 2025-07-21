from django.urls import path, include
from .views import CategoryAPIView,  DeleteCategory, ListCategory, ProductAPIView, ProductListAPIView, DeleteProduct, PlaceOrderView, UpdateOrderStatusView, UserOrderListView


urlpatterns = [
    path('category/', CategoryAPIView.as_view()),
    path('list-category/', ListCategory.as_view()),
    path('delete-category/', DeleteCategory.as_view()),
    
    path('product/', ProductAPIView.as_view()),               # Cache Set
    path('delete-product/', DeleteProduct.as_view()),         # Cache Delete
    path('list-product/', ProductListAPIView.as_view()),      # Pagination + Cache
    
    path('place-order/',PlaceOrderView.as_view()),
    
    path('update-order-status/', UpdateOrderStatusView.as_view()),    # Notification System
    
    path('list-user-order/', UserOrderListView.as_view())
]
