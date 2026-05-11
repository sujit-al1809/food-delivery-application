# Food Delivery Web Application

A full-stack food delivery platform with user authentication, restaurant management, order tracking, and AI-powered delivery time estimation.

## Project Overview

This is a complete food delivery application built with:
- **Backend**: Python Flask, SQLAlchemy ORM, Flask-Security
- **Frontend**: Vue.js 3, Bootstrap, Axios
- **Database**: SQLite (development) / PostgreSQL (production)
- **Background Jobs**: Celery with Redis
- **AI/ML**: scikit-learn for ETA prediction

### Key Features
- User authentication with role-based access control
- Restaurant management and menu items
- Shopping cart and order placement
- Order tracking with real-time status updates
- AI-powered delivery time estimation
- Email notifications for order updates
- Admin dashboard for managing restaurants and orders

## Project Structure

```
food-delivery-app/
├── backend/
│   ├── app.py                 # Flask app factory and setup
│   ├── config.py              # Configuration settings
│   ├── database.py            # SQLAlchemy setup
│   ├── models.py              # Database models
│   ├── requirements.txt        # Python dependencies
│   ├── tasks.py               # Celery background jobs
│   ├── train_model.py         # ML model training script
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── restaurants.py      # Restaurant endpoints
│   │   ├── menu.py            # Menu item endpoints
│   │   ├── orders.py          # Order endpoints
│   │   └── prediction.py      # ETA prediction endpoint
│   └── instance/              # Generated files (models, DB)
│
├── frontend/
│   ├── package.json           # Node dependencies
│   ├── src/
│   │   ├── main.js            # Vue app entry point
│   │   ├── router.js          # Vue Router setup
│   │   ├── App.vue            # Root component
│   │   ├── pages/             # Route components
│   │   │   ├── Home.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── RestaurantDetail.vue
│   │   │   ├── Cart.vue
│   │   │   ├── MyOrders.vue
│   │   │   ├── OrderDetail.vue
│   │   │   ├── ETAPredictor.vue
│   │   │   ├── AdminDashboard.vue
│   │   │   └── NotFound.vue
│   │   └── components/        # Reusable components
│
├── .env.example               # Environment variables template
└── README.md
```

## Database Models

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `password`: String (Hashed)
- `fs_uniquifier`: String (Flask-Security)
- `first_name`, `last_name`: String
- `phone`, `address`: String
- `active`: Boolean
- `roles`: Many-to-Many relationship with Role
- `created_at`: DateTime

### Restaurant
- `id`: Integer (Primary Key)
- `name`: String
- `cuisine`: String
- `location`: Text
- `owner_id`: Integer (FK to User)
- `rating`: Float
- `is_active`: Boolean
- `phone`, `hours_open`: String
- `created_at`, `updated_at`: DateTime

### MenuItem
- `id`: Integer (Primary Key)
- `name`: String
- `description`: Text
- `price`: Float
- `category`: String (Appetizer, Main, Dessert, etc.)
- `restaurant_id`: Integer (FK to Restaurant)
- `is_available`: Boolean
- `preparation_time`: Integer (minutes)
- `created_at`: DateTime

### Order
- `id`: Integer (Primary Key)
- `user_id`: Integer (FK to User)
- `restaurant_id`: Integer (FK to Restaurant)
- `total_price`: Float
- `status`: String (Pending, Confirmed, Preparing, Out for Delivery, Delivered, Cancelled)
- `delivery_address`: Text
- `special_instructions`: Text
- `estimated_delivery_time`: Integer (minutes)
- `created_at`, `updated_at`: DateTime

### OrderItem
- `id`: Integer (Primary Key)
- `order_id`: Integer (FK to Order)
- `menuitem_id`: Integer (FK to MenuItem)
- `quantity`: Integer
- `price`: Float (price at time of order)
- `special_instructions`: Text

### DeliveryAgent
- `id`: Integer (Primary Key)
- `user_id`: Integer (FK to User, Unique)
- `is_available`: Boolean
- `current_location`: String
- `vehicle_type`: String
- `license_plate`: String
- `rating`: Float
- `total_deliveries`: Integer
- `created_at`: DateTime

### Role
- `id`: Integer (Primary Key)
- `name`: String (Customer, RestaurantOwner, DeliveryAgent, Admin)
- `description`: Text

## User Roles

1. **Customer**: Browse restaurants, place orders, track deliveries
2. **RestaurantOwner**: Manage restaurant and menu items
3. **DeliveryAgent**: Accept and manage deliveries
4. **Admin**: Manage all restaurants, orders, and users

## REST API Endpoints

### Authentication

```
POST /api/auth/register
  Request:  { email, password, role, first_name?, last_name?, phone? }
  Response: { message, user_id, email, role }

POST /api/auth/login
  Request:  { email, password }
  Response: { message, token, user: { id, email, roles, ... } }

GET /api/auth/profile
  Headers:  Authorization: Bearer <token>
  Response: { id, email, first_name, last_name, phone, address, roles }

PUT /api/auth/profile
  Headers:  Authorization: Bearer <token>
  Request:  { first_name?, last_name?, phone?, address? }
  Response: { message, user: { ... } }
```

### Restaurants

```
GET /api/restaurants?page=1&per_page=10&cuisine=Italian&search=query
  Response: { restaurants: [...], total, pages, current_page }

GET /api/restaurants/<id>
  Response: { id, name, cuisine, location, rating, phone, hours_open, menu_items: [...] }

POST /api/restaurants
  Headers:  Authorization: Bearer <token> (RestaurantOwner only)
  Request:  { name, cuisine, location, phone?, hours_open? }
  Response: { message, id, name }

PUT /api/restaurants/<id>
  Headers:  Authorization: Bearer <token>
  Request:  { name?, cuisine?, location?, phone?, hours_open?, is_active? }
  Response: { message, id, name }

DELETE /api/restaurants/<id>
  Headers:  Authorization: Bearer <token>
  Response: { message }

GET /api/restaurants/<id>/menu?category=Main
  Response: { menu_items: [...] }

POST /api/restaurants/<id>/menu
  Headers:  Authorization: Bearer <token> (RestaurantOwner only)
  Request:  { name, price, category, description?, preparation_time? }
  Response: { message, id, name }
```

### Menu Items

```
GET /api/menu/<id>
  Response: { id, name, description, price, category, restaurant_id, ... }

PUT /api/menu/<id>
  Headers:  Authorization: Bearer <token>
  Request:  { name?, price?, category?, description?, preparation_time?, is_available? }
  Response: { message, id, name }

DELETE /api/menu/<id>
  Headers:  Authorization: Bearer <token>
  Response: { message }

GET /api/menu/search?q=pizza&cuisine=Italian&category=Main&min_price=5&max_price=20&page=1
  Response: { items: [...], total, pages, current_page }
```

### Orders

```
POST /api/orders
  Headers:  Authorization: Bearer <token>
  Request:  {
    restaurant_id,
    items: [{ menuitem_id, quantity }, ...],
    delivery_address,
    special_instructions?
  }
  Response: { message, order_id, total_price, status }

GET /api/orders/<id>
  Response: {
    id, user_id, restaurant_id, restaurant_name,
    items: [{ id, menuitem_id, name, quantity, price, subtotal }, ...],
    total_price, status, delivery_address, special_instructions,
    estimated_delivery_time, created_at, updated_at
  }

PUT /api/orders/<id>/status
  Headers:  Authorization: Bearer <token>
  Request:  { status }
  Response: { message, order_id, status }

GET /api/orders/user/my-orders?page=1&status=Delivered
  Headers:  Authorization: Bearer <token>
  Response: { orders: [...], total, pages, current_page }

GET /api/orders?page=1&status=Pending&restaurant_id=5
  Headers:  Authorization: Bearer <token> (Admin/RestaurantOwner)
  Response: { orders: [...], total, pages, current_page }
```

### ETA Prediction (AI Feature)

```
POST /api/predict-eta
  Request:  { distance_km: 5, order_items: 3, hour_of_day: 14 }
  Response: { estimated_minutes: 32, distance_km, order_items, hour_of_day }

POST /api/predict-eta/batch
  Request:  {
    orders: [
      { distance_km, order_items, hour_of_day },
      ...
    ]
  }
  Response: { predictions: [{ estimated_minutes, ... }, ...] }
```

## AI/ML Features

### ETA Prediction Model

The application includes a trained Linear Regression model that predicts delivery time based on:
- **Distance (km)**: Distance from restaurant to delivery location
- **Order Items**: Number of items in the order
- **Hour of Day**: Current hour (0-23) to account for peak hour surcharges

**Model Training:**
- Trained on 1000+ synthetic samples
- Features: distance, item count, time of day
- Target: estimated delivery time in minutes
- Minimum estimate: 15 minutes, Maximum: 120 minutes

**Peak Hours:** Orders placed during peak hours (11am-2pm, 6pm-9pm) receive a +10 minute surcharge.

## Celery Background Jobs

### send_order_status_email
- **Trigger**: When order status changes to "Out for Delivery"
- **Action**: Sends email notification to customer
- **Details**: Order ID, restaurant name, delivery address, estimated time

### send_order_confirmation_email
- **Trigger**: When order is placed
- **Action**: Sends confirmation email to customer
- **Details**: Order summary, items, total price

### cleanup_old_orders (Optional)
- **Trigger**: Scheduled maintenance task
- **Action**: Deletes orders older than 90 days (Delivered/Cancelled only)

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- Redis (for Celery)
- Git

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   python -c "from app import create_app; app = create_app(); app.cli.invoke('init_db_command')"
   ```

5. **Train ML Model**
   ```bash
   python train_model.py
   ```

6. **Create Sample Data (Optional)**
   ```bash
   python -c "from app import create_app; app = create_app(); app.cli.invoke('create_sample_data')"
   ```

7. **Run Flask Server**
   ```bash
   python app.py
   # Server runs at http://localhost:5000
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create Environment File**
   ```bash
   echo 'VUE_APP_API_URL=http://localhost:5000/api' > .env.local
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   # Frontend runs at http://localhost:5173 (or similar)
   ```

### Celery Setup

1. **Start Redis Server**
   ```bash
   redis-server
   # Or use Docker: docker run -d -p 6379:6379 redis:latest
   ```

2. **Start Celery Worker**
   ```bash
   cd backend
   celery -A tasks celery_app worker --loglevel=info
   ```

3. **Start Celery Beat (Optional - for scheduled tasks)**
   ```bash
   celery -A tasks celery_app beat --loglevel=info
   ```

## 📝 Example API Usage

### Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepass123",
    "role": "Customer",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepass123"
  }'
```

### Get All Restaurants
```bash
curl -X GET 'http://localhost:5000/api/restaurants?cuisine=Italian&search=pizza'
```

### Create a New Restaurant (RestaurantOwner)
```bash
curl -X POST http://localhost:5000/api/restaurants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "The Pizza Palace",
    "cuisine": "Italian",
    "location": "123 Main Street, City",
    "phone": "555-0123",
    "hours_open": "11AM-11PM"
  }'
```

### Add Menu Item
```bash
curl -X POST http://localhost:5000/api/restaurants/1/menu \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Margherita Pizza",
    "price": 12.99,
    "category": "Pizza",
    "description": "Fresh mozzarella, basil, tomato",
    "preparation_time": 15
  }'
```

### Place an Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "restaurant_id": 1,
    "items": [
      { "menuitem_id": 1, "quantity": 2 },
      { "menuitem_id": 3, "quantity": 1 }
    ],
    "delivery_address": "456 Oak Avenue, City",
    "special_instructions": "Extra cheese on pizza"
  }'
```

### Predict Delivery Time
```bash
curl -X POST http://localhost:5000/api/predict-eta \
  -H "Content-Type: application/json" \
  -d '{
    "distance_km": 5,
    "order_items": 3,
    "hour_of_day": 14
  }'
```

### Get User's Orders
```bash
curl -X GET 'http://localhost:5000/api/orders/user/my-orders' \
  -H "Authorization: Bearer <token>"
```

### Update Order Status
```bash
curl -X PUT http://localhost:5000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"status": "Out for Delivery"}'
```

## Testing

### Manual Testing
1. Open browser and navigate to `http://localhost:5173`
2. Register as a Customer/RestaurantOwner
3. Browse restaurants and place orders
4. Check delivery time with ETA Predictor
5. Login as Admin to manage restaurants and orders

### Test Credentials
- **Admin**: admin@fooddelivery.com / admin123456

## Docker Setup (Optional)

### Backend Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Frontend Docker
```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=sqlite:///fooddelivery.db
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  celery:
    build: ./backend
    command: celery -A tasks celery_app worker --loglevel=info
    depends_on:
      - redis
```

## 🔒 Security Considerations

1. **Change default credentials** in production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Implement rate limiting** on API endpoints
5. **Validate all user inputs** on backend
6. **Use strong password hashing** (already done with bcrypt)
7. **Implement JWT token expiration**
8. **Set up CORS properly** for production domains

## Technologies Used

### Backend
- **Flask** 2.3.0 - Web framework
- **SQLAlchemy** 2.0.0 - ORM
- **Flask-Security** 5.1.0 - Authentication & authorization
- **Celery** 5.3.0 - Task queue
- **Redis** - Message broker & cache
- **scikit-learn** 1.2.2 - ML model
- **PyJWT** 2.6.0 - JWT tokens

### Frontend
- **Vue.js** 3.3.0 - UI framework
- **Vue Router** 4.2.0 - Routing
- **Axios** 1.4.0 - HTTP client
- **Bootstrap** 5.3.0 - CSS framework

### Database
- **SQLite** (development)
- **PostgreSQL** (production - recommended)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Support

For issues or questions, please create an issue on GitHub or contact support@fooddelivery.com

---

**Happy coding!**
