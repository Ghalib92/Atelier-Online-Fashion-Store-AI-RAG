# API Reference

Base URL: `http://localhost:8000/api/`

JSON request/response bodies. Protected endpoints require an
`Authorization: Bearer <access-token>` header. Interactive docs live at
`/api/docs/` (Swagger) and `/api/redoc/`.

---

## Authentication

| Method | Endpoint | Body |
| --- | --- | --- |
| POST | `/auth/register/` | `username, email, password, first_name?, last_name?` |
| POST | `/auth/login/` | `username, password` → `{ access, refresh }` |
| POST | `/auth/refresh/` | `{ refresh }` → `{ access }` |
| GET / PATCH | `/auth/profile/` | current user |
| POST | `/auth/change-password/` | `old_password, new_password` |

```bash
# login, then call a protected endpoint
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'

curl http://localhost:8000/api/cart/ -H "Authorization: Bearer <access>"
```

---

## Catalog

`GET /products/` — list catalog items.

Query params: `?category=dresses`, `?size=M`, `?color=Red`, `?search=floral`,
`?ordering=-price`, `?page=2`.

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Floral Summer Dress",
      "price": "2500.00",
      "category": "dresses",
      "size": "M",
      "color": "Red",
      "quantity": 12,
      "sizes": ["S", "M", "L"],
      "colors": ["Red", "Blue"],
      "image": "/media/products/dress.jpg",
      "availability": "In Stock"
    }
  ]
}
```

- `GET /products/{id}/` — single item.
- `GET /products/{id}/similar/` — related items (same category, shared size/colour).
- `POST/PUT/PATCH/DELETE /products/{id}/` — **staff only**.

---

## Cart

| Method | Endpoint | Notes |
| --- | --- | --- |
| GET | `/cart/` | current user's cart with items + total |
| POST | `/cart/items/` | `{ "product_id": 1, "quantity": 2, "size": "M", "color": "Red" }` |
| PATCH | `/cart/items/{id}/` | `{ "quantity": 3 }` |
| DELETE | `/cart/items/{id}/` | remove an item |

Adding a product that's already in the cart increments its quantity.

---

## Wishlist

- `GET /wishlist/` — list.
- `POST /wishlist/toggle/{product_id}/` — add if absent, remove if present → `{ "in_wishlist": true|false }`.
- `DELETE /wishlist/{id}/` — remove a specific entry.

---

## Checkout & Orders

### Create an order

`POST /checkout/`

```json
{
  "full_name": "Alice Doe",
  "email": "alice@example.com",
  "phone": "254712345678",
  "address": "123 Riverside, Nairobi",
  "payment_method": "mpesa"        // or "cod" (adds a 200 surcharge)
}
```

Creates an order from the current cart. For `cod` the cart is cleared and a
confirmation email is sent. For `mpesa`, follow up with an STK push (below).

### Orders

- `GET /orders/` — list the user's orders (with items, status timeline, `current_status`, `estimated_delivery`).
- `GET /orders/{id}/` — single order.
- `POST /orders/{id}/cancel/` — only allowed before delivery starts.

---

## Payments (M-Pesa)

### Initiate STK push

`POST /payments/stk-push/`

```json
{ "order_id": 42, "phone": "254712345678" }
```

Sends an STK prompt to the phone and records a `Pending` transaction.

### Callback webhook

`POST /payments/mpesa/callback/` — called by Safaricom (public, no auth). On a
successful result whose amount matches the transaction, the order is marked
paid (triggering stock reduction + a confirmation email) and the cart cleared.

### Transactions

`GET /payments/transactions/` — the user's payment history.

---

## Analytics (staff only)

`GET /analytics/?period=30`

```json
{
  "totals": { "users": 120, "products": 64, "orders": 310, "paid_orders": 280, "unpaid_orders": 30, "revenue": 845000 },
  "low_stock_products": [{ "id": 5, "name": "Black Skirt", "quantity": 3 }],
  "top_products": [{ "id": 1, "name": "Floral Summer Dress", "sold": 95 }],
  "sales_trend": [{ "date": "2026-06-01", "total": 12500.0 }],
  "period_days": 30
}
```

---

## Chatbot

`POST /api/chatbot/chat/`

```json
{ "message": "What should I wear to a summer wedding?" }
```

**200** → `{ "answer": "..." }`
**503** → chatbot not configured (missing keys / index).
**502** → upstream model/retrieval failure.

---

## Error responses

| Status | Meaning |
| --- | --- |
| 400 | Validation error |
| 401 | Missing/invalid token |
| 403 | Authenticated but not permitted (e.g. non-staff writing a product) |
| 404 | Not found |
| 502 / 503 | Chatbot upstream failure / not configured |
