# Dunkin Demand Intelligence — API Contract (v1)

Base URL:
http://localhost:5000/api/v1

---

## Forecast

GET /forecast?store_id=1&target_date=YYYY-MM-DD  
Returns stored forecasts from forecast_history

---

GET /forecast/history?store_id=1&limit=30  
Returns historical forecasts

---

## Accuracy

GET /forecast/accuracy  
Returns MAE, MAPE, bias, last_updated

---

## Learning

GET /forecast/learning/summary  
Returns learning adjustments summary

---

## Approvals

GET /forecast/approvals?status=pending  
POST /forecast/approvals/approve

---

## Waste

POST /waste/submit  
POST /waste/approve

---

## System

GET /health  
Returns backend + database status

---

### Notes
- All dashboard endpoints are READ-ONLY
- Forecast generation is not triggered by GET requests
- Frontend must not compute business logic