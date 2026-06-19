# Atelier — Online Fashion Store API

A **REST API** for an online fashion store, built with **Django REST Framework**. It covers the full e-commerce flow — catalog, cart, wishlist, checkout, orders — with **M-Pesa (Safaricom Daraja) payments**, **admin analytics**, and an **AI fashion-assistant chatbot** powered by a Retrieval-Augmented Generation (RAG) pipeline.

JWT-authenticated, documented with an interactive OpenAPI (Swagger) UI, containerised with Docker, and covered by an automated test suite.

---

## Tech Stack

| Concern | Choice |
| --- | --- |
| Language / Framework | Python 3.12, Django 5.2 |
| API | Django REST Framework (class-based views & viewsets) |
| Auth | JWT (`djangorestframework-simplejwt`) |
| Database | PostgreSQL |
| Payments | M-Pesa STK Push (Safaricom Daraja) |
| Chatbot | RAG: HuggingFace embeddings → Pinecone retrieval → OpenAI generation (LangChain) |
| API docs | `drf-spectacular` (Swagger UI + ReDoc) |
| Filtering / search | `django-filter`, DRF SearchFilter |
| Server / static | Gunicorn, WhiteNoise |
| Containerisation | Docker + Docker Compose |

---

## Features

- **JWT auth** — register, login, refresh, profile, change password.
- **Catalog** — products grouped by category; filtering (category/size/color), search, ordering, pagination; "similar products" endpoint. Write access is staff-only.
- **Cart** — per-user cart with add / update-quantity / remove.
- **Wishlist** — toggle products in/out.
- **Checkout & orders** — create orders from the cart (Cash on Delivery or M-Pesa), list/track/cancel orders, order status timeline.
- **M-Pesa payments** — STK push initiation + Daraja callback webhook; marks orders paid, reduces stock and emails the customer (via Django signals).
- **Admin analytics** — revenue, top products, low-stock alerts, sales trend (staff only).
- **AI chatbot** — ask fashion/style questions; answered from a fashion knowledge base via RAG.
- **Secure config** — every secret read from the environment; production security headers auto-enable when `DEBUG=0`.

---

## Project Layout

```
.
├── Atelier_Fashion/          # Django project
│   ├── Atelier_Fashion/      # settings, root urls, wsgi/asgi
│   ├── pages/                # catalog, cart, wishlist, orders, checkout, analytics
│   ├── Accounts/             # JWT auth (register / login / profile / password)
│   ├── payments/             # M-Pesa STK push + callback + transactions
│   ├── chatbot/              # RAG chat endpoint (lazy-loaded pipeline)
│   └── manage.py
├── src/                      # RAG helpers (PDF loading, chunking, embeddings)
├── Data/                     # Fashion PDFs (chatbot knowledge base)
├── store_index.py            # One-off: build the Pinecone index from Data/
├── Dockerfile, docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Quick Start (Docker)

```bash
git clone <repo-url>
cd Atelier-Online-Fashion-Store

cp .env.example .env          # set a real SECRET_KEY & DB_PASSWORD (M-Pesa/chatbot keys optional)
docker compose up --build
```

Migrations and static collection run automatically. Then:

- API root: <http://localhost:8000/api/>
- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>
- Admin: <http://localhost:8000/admin/>

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

> The chatbot dependencies (which pull in `torch`) make the image large. The API runs fine without M-Pesa/OpenAI/Pinecone keys; those features report a clear error until configured.

---

## Local Development

```bash
cd Atelier-Online-Fashion-Store
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # installs the local src/ package too (-e .)

cp .env.example .env                      # set DB_HOST=localhost + local Postgres creds
cd Atelier_Fashion
python manage.py migrate
python manage.py runserver
python manage.py test                     # run the test suite
```

---

## API Overview

Base path: `/api/`

**Auth** — `POST /auth/register/`, `POST /auth/login/`, `POST /auth/refresh/`, `GET|PATCH /auth/profile/`, `POST /auth/change-password/`

**Catalog** — `GET|POST /products/`, `GET|PUT|PATCH|DELETE /products/{id}/`, `GET /products/{id}/similar/` (`?category=`, `?size=`, `?color=`, `?search=`, `?ordering=`)

**Cart** — `GET /cart/`, `GET|POST /cart/items/`, `PATCH|DELETE /cart/items/{id}/`

**Wishlist** — `GET /wishlist/`, `POST /wishlist/toggle/{product_id}/`, `DELETE /wishlist/{id}/`

**Checkout & orders** — `POST /checkout/`, `GET /orders/`, `GET /orders/{id}/`, `POST /orders/{id}/cancel/`

**Payments** — `POST /payments/stk-push/`, `POST /payments/mpesa/callback/` (webhook), `GET /payments/transactions/`

**Analytics** — `GET /analytics/` (staff only)

**Chatbot** — `POST /api/chatbot/chat/` with `{ "message": "..." }`

Full request/response details: [docs/API.md](docs/API.md) or the live Swagger UI.

---

## Setting Up the Chatbot (RAG)

The chatbot answers from the fashion PDFs in `Data/`. To enable it:

1. Set `OPENAI_API_KEY` and `PINECONE_API_KEY` in `.env`.
2. Build the vector index once:
   ```bash
   python store_index.py
   ```
3. Call `POST /api/chatbot/chat/`. Until configured, the endpoint returns `503` with a clear message — the rest of the API is unaffected.

---

## Security Notes

- `.env` is git-ignored; only `.env.example` (placeholders) is committed.
- `SECRET_KEY`, database, email, M-Pesa and chatbot credentials are all read from the environment — none are hard-coded.
- When `DEBUG=0`, HSTS and secure cookies are enabled automatically.
- The M-Pesa callback endpoint validates the amount against the stored transaction before marking an order paid.
