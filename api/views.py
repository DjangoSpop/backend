from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Product, Order, GroupBuy, Notification, Review, OrderItem, GroupBuyParticipation
from .serializers import UserSerializer, RegistrationSerializer, UserLoginSerializer, ProductSerializer, \
    OrderSerializer, \
    GroupBuySerializer, NotificationSerializer, ReviewSerializer, UserLoginSerializer, ProductImageSerializer
from .services import OrderService


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  # Generate refresh token for JWT
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),  # Access token from the JWT
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)  # Generate refresh token
            return Response({
                'refresh': str(refresh),  # Return the refresh token
                'access': str(refresh.access_token),  # Return the access token
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    # Registration action
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'user created', 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Login action using Token Authentication
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                token, created = Token.objects.get_or_create(user=user)  # Generate or get the token
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # User's profile details
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'in_stock', 'brand']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        products = self.get_queryset().filter(name__icontains=query)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def bulk_upload(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        product = self.get_object()
        image_serializer = ProductImageSerializer(data=request.data)
        if image_serializer.is_valid():
            image_serializer.save(product=product)
            return Response(image_serializer.data, status=status.HTTP_201_CREATED)
        return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle custom order creation logic
        """
        order_items_data = request.data.get('items')  # Expecting items in the request data
        if not order_items_data:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)  # Create the Order instance

        total_price = 0
        for item_data in order_items_data:
            try:
                product = Product.objects.get(id=item_data['product'])
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            item_total = item_data['quantity'] * item_data['price']
            total_price += item_total
            OrderItem.objects.create(order=order, product=product, quantity=item_data['quantity'], price=item_data['price'])

        order.total_price = total_price
        order.save()
        serializer = self.get_serializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            order.status = new_status
            order.save()
            return Response({'status': 'order status updated'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        orders = OrderService.search_orders(request.user, query)
        return Response(OrderSerializer(orders, many=True).data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = OrderService.get_order_statistics(request.user)
        return Response(stats)
class GroupBuyViewSet(viewsets.ModelViewSet):
    queryset = GroupBuy.objects.all()
    serializer_class = GroupBuySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Fetch a user instance

    # Action to allow a user to join a group buy
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group_buy = self.get_object()
        user = request.user
        if group_buy.status != 'ACTIVE':
            return Response({'error': 'This group buy is not active'}, status=status.HTTP_400_BAD_REQUEST)
        if group_buy.participants.count() >= group_buy.max_participants:
            return Response({'error': 'This group buy is full'}, status=status.HTTP_400_BAD_REQUEST)
        if GroupBuyParticipation.objects.filter(group_buy=group_buy, user=user).exists():
            return Response({'error': 'You have already joined this group buy'}, status=status.HTTP_400_BAD_REQUEST)

        GroupBuyParticipation.objects.create(group_buy=group_buy, user=user)
        return Response({'success': 'You have successfully joined the group buy'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group_buy = self.get_object()
        user = request.user
        participant = GroupBuyParticipation.objects.filter(group_buy=group_buy, user=user).first()
        if not participant:
            return Response({'error': 'You are not part of this group buy'}, status=status.HTTP_400_BAD_REQUEST)

        participant.delete()
        return Response({'success': 'You have successfully left the group buy'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    # Action to mark a specific notification as read
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'}, status=status.HTTP_200_OK)

    # Action to mark all notifications as read
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        notifications = self.get_queryset().update(is_read=True)
        return Response({'status': f'{notifications} notifications marked as read'}, status=status.HTTP_200_OK)

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # Placeholder for seller analytics data
    @action(detail=False, methods=['get'])
    def seller_analytics(self, request):
        # Example logic for analytics (replace with real logic)
        data = {
            'total_sales': 10000,
            'total_orders': 250,
            'average_order_value': 40.0
        }
        return Response(data, status=status.HTTP_200_OK)