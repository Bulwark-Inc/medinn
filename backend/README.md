# 🏥 MedInn

**MedInn** is a medical e-commerce web application built with Django REST Framework (for backend) and Next.js (for frontend).  
It provides secure user authentication, product listings, cart, checkout, and order management for medical products.

---

## 🚀 Features
- User Accounts & Authentication (JWT)
- Product Listings with filter features
- Shopping Cart & Checkout
- Order Management
- Payment Integration (Stripe or Flutterwave or Paystack or monnify)
- Admin Dashboard

---

## 🛠️ Tech Stack
**Backend:** Django, Django REST Framework  
**Database:** PostgreSQL (recommended), sqlite3 (for development) 
**Frontend:** Next.js (separate repo or folder)  
**Deployment:** Docker + GitHub Actions + Cloud Provider (e.g., Render - frontend, Railway, or AWS - backend)

---

## ⚙️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/Bulwark-inc/medinn.git
cd medinn/backend/
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
``` bash
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```

Access the app at: http://localhost:8000


## 🧩 Environment Variables

Create a .env file in the root directory:

```bash
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/medinn
```

## 🧾 License

This project is licensed under the MIT License.