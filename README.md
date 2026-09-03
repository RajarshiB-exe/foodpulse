# FoodPulse — Food Delivery Economics Intelligence Platform

FoodPulse is a full-stack analytics product for understanding the economics behind food-delivery orders: demand, discounts, delivery costs, contribution margin, restaurant performance, menu performance, anomalies and customer feedback.

## Included in this shipped build

- Executive marketplace dashboard
- 90-day GMV/order/contribution trend
- 14-day demand forecast using Random Forest regression
- Restaurant benchmarking and restaurant-level economics
- Menu-level sales and unit economics
- Contribution-margin simulator
- Isolation Forest anomaly detection
- Review sentiment and topic intelligence
- Area and cuisine supply analysis
- PostgreSQL data model and seeded demonstration dataset
- FastAPI backend with interactive OpenAPI docs
- React + TypeScript + Vite frontend
- Docker Compose one-command startup
- Authorized Swiggy integration boundary using OAuth 2.1 + PKCE/MCP-compatible configuration
- Automated backend unit test for the simulator

## Data policy

The bundled restaurant names and transaction records are a realistic demonstration dataset. They are not claimed to be live Swiggy/Zomato records and the financial metrics should not be presented as actual performance of those businesses.

The architecture is designed so an authorized API, permitted merchant export, or licensed dataset can replace the demonstration ingestion layer without changing the analytics interface.

## Run locally

Requirements: Docker Desktop.

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at `http://localhost:5173`.

FastAPI documentation is available at `http://localhost:8000/docs`.

To stop the stack:

```bash
docker compose down
```

To reset the demonstration database and reseed it:

```bash
docker compose down -v
docker compose up --build
```

## Architecture

Browser → React/Vite → FastAPI → SQLAlchemy → PostgreSQL

Server-side analytics use Pandas, NumPy and scikit-learn. The application separates the data layer from analytics so authorized ingestion sources can be added later.

## API surface

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/anomalies`
- `GET /api/forecast`
- `GET /api/restaurants`
- `GET /api/restaurants/{id}/economics`
- `GET /api/restaurants/{id}/menu`
- `GET /api/reviews/intelligence`
- `POST /api/simulator`
- `GET /api/integrations/swiggy/status`

## Swiggy integration

FoodPulse includes an isolated integration boundary for authorized Swiggy Builders Club access. Configure only credentials you are authorized to use; never commit access tokens to Git.

## Resume line

Built a full-stack food-delivery economics intelligence platform using React, FastAPI and PostgreSQL, with server-side analytics, restaurant benchmarking, anomaly detection, demand forecasting, review intelligence and an interactive contribution-margin simulator.
