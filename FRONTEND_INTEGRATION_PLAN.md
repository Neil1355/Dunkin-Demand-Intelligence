# Frontend Dashboard Analysis

## Current Structure

### Dashboard Tabs (6 total)
1. **Dashboard** - Main overview with charts
2. **Enter Daily Data** - Manual input + Excel upload
3. **Predictions** - AI forecast display
4. **History** - Production history table
5. **Imported Data** - Shows imported throwaway data with weekly summaries
6. **QR Code** - Staff waste submission via QR

---

## Current Chart Sections (Dashboard Tab)

### Section 1: Quick Stats (3 KPI Cards)
- **Today's Production** - Total units produced today
- **Predicted Waste** - Waste percentage
- **Tomorrow's Forecast** - Units forecasted for tomorrow

**Status**: ✅ Already displays with hardcoded placeholder data

### Section 2: Weekly Waste vs Sales (Bar Chart)
- X-axis: Days of week (Mon-Sun)
- Y-axis: Waste & Sales percentages
- Currently: Using `weeklyData` from `/dashboard/accuracy?store_id=X&days=7`

**Status**: ✅ Chart exists, pulling from `weeklyData` state

### Section 3: Production Optimization (Line Chart)
- X-axis: Weeks (Week 1-4)
- Y-axis: Production vs Optimal levels
- Currently: Using hardcoded placeholder data

**Status**: ⚠️ Chart structure exists but data is HARDCODED

---

## New Backend Endpoints Available

### Your New Endpoints (Phase 2)
```
GET  /api/v1/dashboard/imports       - Recent import history
GET  /api/v1/dashboard/production-summary - Production metrics (7-day trends)
GET  /api/v1/dashboard/waste-summary - Waste metrics (7-day trends)
GET  /api/v1/dashboard/quick-stats   - KPI cards (total produced, waste ratio, top waste products)
```

### Existing Endpoints Used
```
POST /api/v1/excel/upload            - Excel file upload
POST /api/v1/throwaway/upload_throwaways - Weekly throwaway upload
GET  /api/v1/throwaway/recent        - Import history (already used in 'Imported Data')
GET  /api/v1/forecast                - Forecast data
GET  /api/v1/dashboard/accuracy      - Weekly accuracy data (already used for charts)
```

---

## Integration Recommendations

### HIGH Priority (Easy Wins)
1. **Replace hardcoded Quick Stats** 
   - Use `/dashboard/quick-stats?store_id=X` 
   - Replace the 3 KPI cards with real data
   - Add 4th card: "Top Waste Product"

2. **Fix Production Optimization Chart**
   - Replace hardcoded `trendData` with real data from `/dashboard/production-summary`
   - Show actual 4-week production trends vs optimal

### MEDIUM Priority (New Insights)
3. **Add Import History Card** (under Quick Stats or as separate section)
   - Use `/dashboard/imports?store_id=X&days=30`
   - Show "Last Import: X days ago"
   - Show import trends (production vs throwaway imports)

4. **Add Waste Trend Card** (new chart in dashboard)
   - Use `/dashboard/waste-summary?store_id=X&days=7`
   - Pie chart or line chart showing waste percentage trend
   - Highlight "Top Wasted Products"

### LOW Priority (Enhancement)
5. **Imported Data Tab Enhancement**
   - Already working but combine with new `/dashboard/imports` endpoint
   - Add import success/failure rates

---

## Specific Code Changes Needed

### 1. Quick Stats - Replace with Real Data
```tsx
// Current (Dashboard.tsx, lines ~460-480)
<div className="grid md:grid-cols-3 gap-6">
  <div>Today's Production: {dashboardData.production}</div>
  <div>Predicted Waste: {dashboardData.waste_pct}%</div>
  <div>Tomorrow's Forecast: {dashboardData.forecast}</div>
</div>

// Should use: GET /dashboard/quick-stats?store_id=X
// Response has: total_produced, total_waste, waste_ratio, top_waste_products
```

### 2. Production Optimization Chart - Real Data
```tsx
// Current (Dashboard.tsx, lines ~530-560)
const trendData = [hardcoded week data]

// Should fetch from: GET /dashboard/production-summary?store_id=X&days=28
// And transform for line chart
```

### 3. Add Import Status Section
- NEW component to display recent import activity
- Use `/dashboard/imports?store_id=X&days=7`

---

## Files to Modify

1. **frontend/src/pages/dashboard/Dashboard.tsx** (main changes)
   - Add state for new endpoints
   - Add fetch functions for imports, production-summary, waste-summary, quick-stats
   - Replace hardcoded data in useEffect
   - Update 3 KPI cards with real data
   - Update trendData for Production Optimization chart

2. **frontend/src/api/client.ts** (if needed)
   - Ensure new endpoints are callable

3. **Optional: Create new component**
   - `ImportHistoryCard.tsx` - Show recent imports + success rate

---

## Integration Order
1. ✅ Quick Stats (easiest - 30 min)
2. ✅ Production Optimization Chart (30 min)
3. ✅ Import History Card (optional - 20 min)
4. ✅ Waste Trend Chart (optional - 30 min)

Total estimated: 1-2 hours for full integration

---

## What's Already Working
- ✅ Excel upload functionality
- ✅ Forecast generation
- ✅ History display
- ✅ Imported data tracking
- ✅ Chart rendering (Recharts)

## What Needs Integration
- ❌ Real production trend data
- ❌ Real quick stats
- ❌ Import history visualization
- ❌ Waste trend analysis

