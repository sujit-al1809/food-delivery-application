# Quick Start Guide

Get the Food Delivery app running in 5 minutes!

## Prerequisites
- Python 3.8+
- Node.js 14+
- Redis (optional, for background jobs)

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train ML model
python train_model.py

# Run Flask app
python app.py
```

Backend should now run at: **http://localhost:5000**

## Step 2: Frontend Setup (2 minutes)

In a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend should now run at: **http://localhost:5173**

## Step 3: Test the App (1 minute)

1. Open browser: **http://localhost:5173**

2. **Register or Login with demo account:**
   - Email: `admin@fooddelivery.com`
   - Password: `admin123456`

3. **Try these features:**
   - View restaurants on homepage
   - Click "View Menu" on a restaurant
   - Add items to cart
   - Place an order
   - Check delivery time with ETA Predictor

## Optional: Setup Celery (for email notifications)

In a new terminal:

```bash
# Start Redis
redis-server

# In another terminal, start Celery worker
cd backend
celery -A tasks celery_app worker --loglevel=info
```

## API Documentation

Quick reference for important endpoints:

### Get All Restaurants
```bash
curl http://localhost:5000/api/restaurants
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@fooddelivery.com","password":"admin123456"}'
```

### Predict Delivery Time
```bash
curl -X POST http://localhost:5000/api/predict-eta \
  -H "Content-Type: application/json" \
  -d '{"distance_km":5,"order_items":3,"hour_of_day":14}'
```

## Key Features to Try

### 👤 User Roles
- **Customer** - Browse and order
- **RestaurantOwner** - Manage restaurant
- **DeliveryAgent** - Track deliveries
- **Admin** - Manage everything

### 🏪 Restaurant Features
- Create/Edit restaurants
- Add menu items
- Manage availability

### 🛒 Order Features
- Browse restaurants by cuisine
- Search menu items
- Manage shopping cart
- Place orders
- Track order status

### 🤖 AI Features
- Predict delivery time based on:
  - Distance
  - Number of items
  - Time of day

## Database Models Created

```
User (customer, owner, driver, admin)
  ↓
Restaurant (owned by RestaurantOwner)
  ↓
MenuItem (part of restaurant menu)
  ↓
Order (placed by Customer)
  ↓
OrderItem (items in the order)
```

## Useful Commands

```bash
# Create sample restaurants and menu items
python -c "from app import create_app; app = create_app(); app.cli.invoke('create_sample_data')"

# Reset database
rm instance/fooddelivery.db
python -c "from app import create_app; app = create_app(); app.cli.invoke('init_db_command')"

# Run with specific config
FLASK_ENV=development python app.py
```

## Frontend Pages

| Route | Purpose | Auth Required |
|-------|---------|---------------|
| `/` | Home & Restaurant List | No |
| `/login` | User Login | No |
| `/register` | New User Registration | No |
| `/restaurant/:id` | Restaurant Details & Menu | No |
| `/cart` | Shopping Cart | Yes |
| `/orders` | Order History | Yes |
| `/order/:id` | Order Details | Yes |
| `/eta-predictor` | Delivery Time Estimator | No |
| `/admin` | Admin Dashboard | Yes (Admin role) |

## Project Structure at a Glance

```
food-delivery-app/
├── backend/          ← Flask API server
│   ├── app.py        ← Main app
│   ├── models.py     ← Database models
│   ├── routes/       ← API endpoints
│   └── train_model.py ← ML model training
├── frontend/         ← Vue.js app
│   ├── src/
│   │   ├── pages/    ← UI pages
│   │   ├── App.vue   ← Root component
│   │   └── router.js ← Routing config
│   └── package.json  ← Dependencies
└── README.md         ← Full documentation
```

## Common Issues & Solutions

### "Connection refused" on http://localhost:5000
- Flask server not running - check backend terminal
- Run: `python app.py` in backend directory

### "npm ERR! missing required argument"
- Missing dependencies - run: `npm install`
- Wrong directory - navigate to frontend folder first

### "ModuleNotFoundError: No module named 'flask'"
- Virtualenv not activated
- Run: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

### "No such table: user"
- Database not initialized
- Run: `python -c "from app import create_app; app = create_app(); app.cli.invoke('init_db_command')"`

### Port already in use
- Flask: Change port in app.py or use `python app.py --port 5001`
- Frontend: Change port in vite.config.js or use `npm run dev -- --port 5174`

## Next Steps

1. **Explore the codebase** - Start with `app.py` and main components
2. **Read full documentation** - Check `README.md`
3. **Try the API** - Use curl/Postman to test endpoints
4. **Customize** - Add your own features and styling
5. **Deploy** - Follow deployment guide in `DEPLOYMENT.md`

## Need Help?

- Check full `README.md` for detailed docs
- See `DEPLOYMENT.md` for production setup
- Review source code comments
- Check error messages in terminal

---

**Enjoy building! 🚀**
