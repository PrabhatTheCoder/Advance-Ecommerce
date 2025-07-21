# 🚀 Advance Ecommerce System

A Django REST Framework powered, full-featured e-commerce backend built with scalable components like Redis caching, WebSocket notifications, JWT authentication, and containerized via Docker.

---

## ✍️ Features

- 🔐 **JWT Authentication**  
  Secure login, registration, token refresh, and logout with blacklist support.

- 🛍️ **Product & Category Management**  
  Add, list, update, and delete products and categories.

- 🛒 **Shopping Cart & Order Flow**  
  Users can add items to cart, place orders, and view past orders.

- 📦 **Order Status Workflow**  
  Order lifecycle: `Pending → Shipped → Delivered`.

- ⚡ **Real-time Notifications**  
  WebSocket-based updates using Django Channels + Redis.

- 📄 **Pagination & Caching**  
  Efficient API responses with DRF pagination and Redis cache.

---

## 🛠️ Tech Stack

| Layer       | Technology                 |
|-------------|----------------------------|
| Backend     | Django, Django REST Framework |
| Auth        | JWT (SimpleJWT)            |
| Realtime    | Django Channels + Redis    |
| Database    | PostgreSQL                 |
| Caching     | Redis                      |
| Deployment  | Docker, Docker Compose, AWS (EC2) |

---


## 🚀 Postman Collection

You can use the provided Postman collection to test the entire API.

- [📥 Download Postman Collection](https://github.com/PrabhatTheCoder/Advance-Ecommerce/blob/main/Advance%20Ecommerce.postman_collection.json)

### 🔥 How to use
1. Open Postman > Import > Upload `recipe-management-collection.json`.
2. Set the environment variables for:
   - `{{base_url}}` = `[{{BASE_URL}}app/category/](http://3.110.88.71:8000/)`
   - `{{access_token}}` (optional if using authenticated endpoints)
3. Run your requests.

## 📂 Project Structure

```plaintext
Advance-Ecommerce/
│
├── app/                      # E-commerce core app
│   ├── models.py             # Product, Category, Cart, Order models
│   ├── views.py              # DRF views and logic
│   ├── serializers.py        # DRF serializers
│   ├── consumers.py          # WebSocket consumers
│   ├── urls.py               # App endpoints
│
├── users/                    # Custom User & Auth
│   ├── models.py             # CustomUser with roles
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── ecommerce/                # Project-level settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py               # Channels config
│   └── wsgi.py
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

```

---

## 🚀 API Endpoints

# Base URL - [http://3.110.88.71:8000/](http://3.110.88.71:8000/)

## 🔐 ⭐ Users

| Method | Endpoint                  | Description                            |
| ------ | ------------------------- | -------------------------------------- |
| POST   | `/auth/register-user/`    | Register a new user (creator / viewer) |
| POST   | `/auth/login/`            | Login & get access + refresh tokens    |
| POST   | `/auth/logout/`           | Logout (invalidate refresh token)      |
| POST   | `/auth/get-access-token/` | Get new access token using refresh     |

---

## 📁 Categories

| Method | Endpoint            | Description                             |
| ------ | ------------------- | --------------------------------------- |
| POST   | `/category/`        | Create a new product category           |
| GET    | `/list-category/`   | List all product categories             |
| DELETE | `/delete-category/` | Delete a product category (by ID param) |

---

## 📦 Products

| Method | Endpoint           | Description                                  |
| ------ | ------------------ | -------------------------------------------- |
| POST   | `/product/`        | Create a new product (**Redis cache set**)   |
| GET    | `/list-product/`   | List all products (**Paginated + Cached**)   |
| DELETE | `/delete-product/` | Delete a product (**Redis cache delete**)    |

---

## 🛒 Orders

| Method | Endpoint                | Description                                               |
| ------ | ----------------------- | --------------------------------------------------------- |
| POST   | `/place-order/`         | Place an order from the cart                              |
| PATCH  | `/update-order-status/` | Update order status (**sends WebSocket notification**)    |
| GET    | `/list-user-order/`     | List all orders for the authenticated user                |

---

## 🔔 WebSocket Notifications

- Connect to WebSocket:

```bash
ws://localhost:8000/ws/notifications/<access_token>/


## ⚙️ Installation

### 🐳 Docker (recommended)
```bash
docker-compose up --build
