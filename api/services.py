# api/services.py

from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, Product
from .serializers import OrderSerializer
class AnalyticsService:
    @staticmethod
    def get_seller_analytics(seller):
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=30)

        total_sales = Order.objects.filter(
            seller=seller,
            created_at__range=(start_date, end_date)
        ).aggregate(total=Sum('total_price'))['total'] or 0

        total_orders = Order.objects.filter(
            seller=seller,
            created_at__range=(start_date, end_date)
        ).count()

        top_products = Product.objects.filter(
            seller=seller,
            order__created_at__range=(start_date, end_date)
        ).annotate(total_sales=Sum('order__total_price')).order_by('-total_sales')[:5]

        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'top_products': top_products,
        }

    @staticmethod
    def get_sales_over_time(seller, period='month'):
        end_date = timezone.now()
        if period == 'month':
            start_date = end_date - timezone.timedelta(days=30)
            date_trunc = 'day'
        elif period == 'year':
            start_date = end_date - timezone.timedelta(days=365)
            date_trunc = 'month'
        else:
            raise ValueError("Invalid period. Use 'month' or 'year'.")

        sales = Order.objects.filter(
            seller=seller,
            created_at__range=(start_date, end_date)
        ).extra(select={'date': f"date_trunc('{date_trunc}', created_at)"}
        ).values('date').annotate(total=Sum('total_price')).order_by('date')

        return list(sales)
class OrderService:
    @staticmethod
    def get_seller_orders(seller):
        return Order.objects.filter(seller=seller).order_by('-created_at')

    @staticmethod
    def get_order_details(order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValueError("Order not found")

    @staticmethod
    def update_order_status(order_id, new_status):
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            return order
        except Order.DoesNotExist:
            raise ValueError("Order not found")

    @staticmethod
    def add_tracking_number(order_id, tracking_number):
        try:
            order = Order.objects.get(id=order_id)
            order.tracking_number = tracking_number
            order.save()
            return order
        except Order.DoesNotExist:
            raise ValueError("Order not found")

    @staticmethod
    def search_orders(seller, query):
        return Order.objects.filter(
            Q(seller=seller) &
            (Q(id__icontains=query) | Q(user__username__icontains=query) | Q(status__icontains=query))
        ).order_by('-created_at')

    @staticmethod
    def get_order_statistics(seller):
        total_orders = Order.objects.filter(seller=seller).count()
        pending_orders = Order.objects.filter(seller=seller, status='pending').count()
        completed_orders = Order.objects.filter(seller=seller, status='completed').count()

        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
        }
