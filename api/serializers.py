from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import CustomUser, Product, Order, GroupBuy, Review, Notification, OrderItem ,GroupBuyParticipation,ProductImage,ProductInventory,ProductSize


# User Serializer for Profile and General Use
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'phone', 'address']
        read_only_fields = ['id']

# Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'role', 'phone', 'address', 'shop_name', 'shop_description']
        extra_kwargs = {
            'shop_name': {'required': False},
            'shop_description': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'buyer'),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            shop_name=validated_data.get('shop_name', ''),
            shop_description=validated_data.get('shop_description', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Login Serializer

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data

# Product Serializer
class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'name']

class ProductInventorySerializer(serializers.ModelSerializer):
    size = ProductSizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ProductSize.objects.all(), source='size')

    class Meta:
        model = ProductInventory
        fields = ['size', 'size_id', 'quantity']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    inventory = ProductInventorySerializer(many=True, source='productinventory_set')
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price','discountedprice', 'barcode', 'category', 'subcategory',
                  'brand', 'quantity', 'in_stock', 'rating', 'review_count', 'sizes', 'colors',
                  'images', 'uploaded_images', 'seller']
        read_only_fields = ['seller']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images')
        sizes = validated_data.pop('sizes', [])
        colors = validated_data.pop('colors', [])
        product = Product.objects.create(**validated_data)

        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        product.sizes = sizes
        product.colors = colors
        product.save()

        return product

    def update(self, instance, validated_data):
        inventory_data = validated_data.pop('productinventory_set', [])
        uploaded_images = validated_data.pop('uploaded_images', [])

        instance = super().update(instance, validated_data)

        for inv_item in inventory_data:
            ProductInventory.objects.update_or_create(
                product=instance,
                size=inv_item['size'],
                defaults={'quantity': inv_item['quantity']}
            )

        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)

        return instance
# class GroupBuySerializer(serializers.ModelSerializer):
#     participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta:
#         model = GroupBuy
#         fields = '__all__'
# class UserLoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=255)
#     password = serializers.CharField(max_length=128, write_only=True)
#
#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#
#         if not username:
#             raise serializers.ValidationError('A username is required to log in.')
#
#         if not password:
#             raise serializers.ValidationError('A password is required to log in.')
#
#         user = authenticate(username=username, password=password)
#
#         if user is None:
#             raise serializers.ValidationError('Invalid username or password.')
#
#         if not user.is_active:
#             raise serializers.ValidationError('This user has been deactivated.')
#
#         return {'username': user.username, 'email' : user.email, 'password': user.password }
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # Nested relationship to OrderItemSerializer
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Read-only total_price

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'tracking_number', 'items']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'items', 'total_price']

    def create(self, validated_data):
        order_items_data = self.context['request'].data.get('items')  # Expecting items in the request data
        order = Order.objects.create(**validated_data)  # Create the Order instance

        total_price = 0  # Initialize total price

        for item_data in order_items_data:
            product = Product.objects.get(id=item_data['product'])
            item_total = item_data['quantity'] * item_data['price']
            total_price += item_total  # Add to total price
            OrderItem.objects.create(order=order, product=product, quantity=item_data['quantity'],
                                     price=item_data['price'])

        order.total_price = total_price  # Set total price after calculating
        order.save()  # Save the order with the total price

        return order
# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(user=user, product=validated_data['product'], **validated_data)

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

# Analytics Serializer
class AnalyticsSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    top_products = ProductSerializer(many=True)

class GroupBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBuy
        fields = '__all__'
        read_only_fields = ['current_particpants', 'status']

class GroupBuyParticipantSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = GroupBuyParticipation
        fields = '__all__'
        read_only_fields = ['joined_at']