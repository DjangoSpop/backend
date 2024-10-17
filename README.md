UserViewSet:

GET /api/users/ - List all users
POST /api/users/ - Create a new user
GET /api/users/{id}/ - Retrieve a specific user
PUT /api/users/{id}/ - Update a specific user
PATCH /api/users/{id}/ - Partially update a specific user
DELETE /api/users/{id}/ - Delete a specific user
GET /api/users/me/ - Retrieve the current user's profile


ProductViewSet:

GET /api/products/ - List all products
POST /api/products/ - Create a new product
GET /api/products/{id}/ - Retrieve a specific product
PUT /api/products/{id}/ - Update a specific product
PATCH /api/products/{id}/ - Partially update a specific product
DELETE /api/products/{id}/ - Delete a specific product
GET /api/products/{id}/reviews/ - List all reviews for a specific product
GET /api/products/search/ - Search for products
GET /api/products/recommendations/ - Get product recommendations


OrderViewSet:

GET /api/orders/ - List all orders (filtered by user for non-staff)
POST /api/orders/ - Create a new order
GET /api/orders/{id}/ - Retrieve a specific order
PUT /api/orders/{id}/ - Update a specific order
PATCH /api/orders/{id}/ - Partially update a specific order
DELETE /api/orders/{id}/ - Delete a specific order


GroupBuyViewSet:

GET /api/group-buys/ - List all group buys
POST /api/group-buys/ - Create a new group buy
GET /api/group-buys/{id}/ - Retrieve a specific group buy
PUT /api/group-buys/{id}/ - Update a specific group buy
PATCH /api/group-buys/{id}/ - Partially update a specific group buy
DELETE /api/group-buys/{id}/ - Delete a specific group buy
POST /api/group-buys/{id}/join/ - Join a specific group buy


ReviewViewSet:

GET /api/reviews/ - List all reviews
POST /api/reviews/ - Create a new review
GET /api/reviews/{id}/ - Retrieve a specific review
PUT /api/reviews/{id}/ - Update a specific review
PATCH /api/reviews/{id}/ - Partially update a specific review
DELETE /api/reviews/{id}/ - Delete a specific review


NotificationViewSet:

GET /api/notifications/ - List all notifications for the current user
GET /api/notifications/{id}/ - Retrieve a specific notification
POST /api/notifications/{id}/mark_as_read/ - Mark a specific notification as read


AnalyticsViewSet:

GET /api/analytics/sales_overview/ - Get sales overview
GET /api/analytics/top_products/ - Get top selling products