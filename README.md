# 🎨 PosterKart — Premium Full-Stack Wall Art E-Commerce Platform

> **PosterKart** is a full-stack, commercial-grade e-commerce web application engineered for browsing, customizing, and ordering museum-quality wall posters and framed prints. Built with **Python Django**, **SQLite**, **HTML5/CSS3/Bootstrap 5**, and responsive modern **JavaScript**.

---

## 🌟 Key Features

### 1. 🛍️ Customer Experience & Storefront
- **Editorial Hero Showcase**: Modern split-layout hero banner with 3D poster showcase.
- **10 Curated Poster Categories**: Movies, Anime, Cars & Bikes, Gaming, Quotes, Sports, Nature, Music, Minimalist, Aesthetic.
- **Advanced Shop Filtering & Search**: Filter by category, price range, stock availability, and sorting (Most Popular, Newest, Price Low-High, Price High-Low, Rating).
- **Debounced Live Search**: Search dropdown with instant query suggestions, thumbnails, and category links.
- **Quick View Modal**: Interactive popup on product cards with size/frame selectors and instant Add-to-Bag.
- **Interactive Wall Mockup Preview**: View how any poster looks on living room, bedroom, or office studio walls with dynamic frame color changes.

### 2. 🖼️ Poster Customization & Pricing Engine
- **Poster Sizes**: A4 (Base Price), A3 (+₹100), A2 (+₹250).
- **Framing Options**: No Frame / Rolled Canvas (₹0), Matte Black Wood Frame (+₹200), Modern White Frame (+₹200), Classic Natural Walnut Frame (+₹300).
- **Dynamic JavaScript & Backend Recalculation**: Live client-side price preview verified securely on Django backend before placing orders.
- **Delivery Policy**: Automatic free delivery on orders ₹499 or above (₹50 standard charge below ₹499).

### 3. 🎨 Custom Poster Studio
- **Personalized Art Creator**: Upload your personal photos, digital illustrations, or wedding moments.
- **Live Canvas Preview**: Real-time image preview inside selected wooden frame with custom text overlay.
- **Validation**: Accepts JPG, JPEG, PNG, and WEBP up to 10 MB.

### 4. 🛒 Bag & Wishlist Systems
- **Slide-out Cart Drawer**: Smooth slide-in cart drawer with live subtotal, quantity updates, and free-shipping progress meter.
- **Dedicated Cart Page**: Itemized summary, quantity controls, and coupon application.
- **Coupon System**: Percentage or flat discounts with minimum order validation (e.g., `POSTER10`, `SAVE100`, `WELCOME50`, `FESTIVE20`).
- **Wishlist**: Save favorite posters with animated heart toggles and 1-click move to bag.

### 5. 📦 Orders, Checkout & Live Tracking
- **Multi-Step Checkout**: Saved delivery address selection or in-place address creation.
- **Payment Options**: Cash on Delivery (COD) & Demo Online Payment (Cards, UPI, NetBanking simulation).
- **Celebratory Order Success Page**: Displays Order ID, delivery destination, and estimated transit date.
- **6-Stage Visual Order Tracking Timeline**: Order Placed ➔ Confirmed ➔ Printing & Framing ➔ Shipped ➔ Out for Delivery ➔ Delivered.
- **Order Cancellation**: Customers can cancel orders before the package reaches the "Shipped" stage.

### 6. 🛡️ Staff Admin Dashboard
- **Store Operations Overview**: Total Customers, Total Posters, Total Orders, Total Revenue, Pending Orders, Delivered Orders.
- **Live Order Status Management**: Inline status updater for quick tracking updates.
- **Custom Poster Requests Viewer**: Preview uploaded files, text requests, and specs.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Django 5.2 |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Database** | SQLite3 (Production-ready schema for PostgreSQL/MySQL) |
| **Image Processing** | Pillow (PIL) |
| **Authentication** | Django Auth System (Session/Cookie based + CSRF Protection) |

---

## 📁 Project Directory Structure

```text
posterkart/
│
├── accounts/                  # User accounts, authentication & addresses
│   ├── forms.py               # Registration, Login, Profile & Address forms
│   ├── models.py              # UserProfile and Address models
│   ├── urls.py                # Authentication routing
│   └── views.py               # Auth & address controllers
│
├── store/                     # Posters, categories, catalog & info pages
│   ├── admin.py               # Django Admin customization
│   ├── context_processors.py  # Global categories processor
│   ├── forms.py               # Review & contact forms
│   ├── models.py              # Category, Poster, PosterSize, FrameOption, Review
│   ├── urls.py                # Shop, category, API routes
│   └── views.py               # Storefront & Admin dashboard views
│
├── cart/                      # Shopping cart, wishlist & coupons
│   ├── context_processors.py  # Cart and wishlist badge context
│   ├── models.py              # Cart, CartItem, Coupon, Wishlist
│   ├── urls.py                # Cart & wishlist endpoints
│   ├── utils.py               # Cart merging & session retrieval
│   └── views.py               # AJAX cart drawer & coupon views
│
├── orders/                    # Checkout, payments & order tracking
│   ├── models.py              # Order and OrderItem models
│   ├── urls.py                # Checkout, tracking, cancellation routes
│   └── views.py               # Checkout & payment simulation controllers
│
├── customposters/             # Custom poster upload studio
│   ├── forms.py               # Image upload & size validation form
│   ├── models.py              # CustomPoster model
│   ├── urls.py                # Custom studio route
│   └── views.py               # Custom poster handler
│
├── templates/                 # Reusable Django template inheritance
│   ├── base.html              # Master layout
│   ├── navbar.html            # Sticky header with search & drawer trigger
│   ├── footer.html            # Trust badges & footer navigation
│   ├── 404.html / 500.html    # Friendly error pages
│   ├── includes/              # Component partials (cart drawer, product card, quick view)
│   ├── store/                 # Home, shop, category, product detail, info pages
│   ├── accounts/              # Register, login, profile, addresses
│   ├── cart/                  # Cart & wishlist templates
│   ├── orders/                # Checkout, demo payment, tracking, success
│   ├── customposters/         # Custom poster studio
│   └── admin_dashboard/       # Operational stats & orders manager
│
├── static/                    # Static assets
│   ├── css/style.css          # Design system & responsive styles
│   ├── js/main.js             # AJAX engine, modals, drawer & price calculator
│   └── images/                # Fallback placeholders & icons
│
├── media/                     # Uploaded poster images & user uploads
├── seed_data.py               # Database populator with Pillow artwork generator
├── test_workflow.py           # Automated end-to-end test suite
├── requirements.txt           # Python dependencies
└── manage.py                  # Django CLI runner
```

---

## ⚡ Quick Start & Installation Guide

### Step 1: Clone or Navigate to Project Directory
```powershell
cd C:\Users\yoges\posterkart
```

### Step 2: Create & Activate Python Virtual Environment
**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```
**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Seed Sample Data & Artworks
Run the seed script to automatically populate all 10 categories, poster sizes, frame options, coupons, and 20 sample posters with generated artwork images:
```bash
python seed_data.py
```

### Step 6: Start the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your web browser.

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Email | Access |
|---|---|---|---|---|
| **Customer** | `rahul` | `rahul123` | `rahul@example.com` | Full customer journey, Wishlist, Checkout |
| **Staff Admin** | `admin` | `admin123` | `admin@posterkart.com` | Custom Dashboard (`/admin-dashboard/`) & Django Admin (`/admin/`) |

---

## 🧪 Running the Automated Test Suite

To verify all 14 core user journeys (browsing, quick view, adding to bag with sizes/frames, coupon application, address selection, order checkout, demo payment simulation, live order tracking, custom poster studio, and admin status updates):

```bash
python test_workflow.py
```

---

## 💳 Available Test Discount Coupons

| Coupon Code | Discount | Minimum Order | Description |
|---|---|---|---|
| `POSTER10` | **10% OFF** | ₹0 | 10% discount on all orders |
| `SAVE100` | **₹100 FLAT OFF** | ₹499 | ₹100 instant discount on orders ₹499+ |
| `WELCOME50` | **₹50 FLAT OFF** | ₹299 | Welcome offer for new customers |
| `FESTIVE20` | **20% OFF** | ₹799 | Festive discount on large orders |

---

## 🔒 Security & Best Practices
- **Password Hashing**: PBKDF2 with SHA-256 via Django Auth.
- **CSRF Protection**: All POST/AJAX endpoints protected via Django CSRF tokens.
- **Server-Side Validation**: Final order prices, coupons, and discounts are calculated securely on the backend before order creation.
- **Access Control**: Role-based access ensuring customers can only view their own orders and addresses.
