# CARBON CREDIT SYSTEM DESIGN - UPDATED

## SYSTEM OVERVIEW

A comprehensive carbon credit management platform that connects farmers, validators, and administrators through a transparent blockchain-inspired tracking system. **Now includes dedicated Farm Service management with geospatial data visualization and protected route authentication.**

---

## PROJECT STRUCTURE (UPDATED)

```markdown
baseprogram/
├── models/                    # Database models (SQLAlchemy)
│   ├── user.py               # User model definition
│   ├── farm.py               # NEW: Farm model with geospatial data
│   └── carbon_credit.py      # NEW: Carbon credit transactions
│
├── schemas/                   # Pydantic schemas (validation)
│   ├── user.py              # User request/response schemas
│   ├── auth.py              # Authentication schemas
│   └── farm.py              # NEW: Farm data schemas
│
├── routers/                   # API endpoints (organized by feature)
│   ├── auth.py              # Authentication routes
│   ├── users.py             # User management routes
│   ├── leaderboard.py       # Leaderboard routes
│   └── farmservice.py       # NEW: Farm management routes
│
├── templates/                 # HTML templates (Jinja2)
│   ├── base.html            # Base template with navbar
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # User dashboard
│   ├── profile_edit.html    # Profile editing
│   ├── leaderboard.html     # Leaderboard display
│   ├── profile.html         # Public profile view
│   ├── farmservice.html     # NEW: Farm management dashboard
│   └── error.html           # Error page
│
├── static/                    # Static files
│   ├── css/
│   │   ├── style.css        # Main styles
│   │   └── farmservice.css  # NEW: Farm service styles
│   ├── js/
│   │   ├── auth.js          # Authentication utilities
│   │   ├── utils.js         # Helper functions
│   │   ├── farmservice.js   # NEW: Farm management logic
│   │   └── mapHandler.js    # NEW: Map integration
│   └── profile_pics/
│
├── media/
│   └── profile_pics/
│
├── utils/                     # NEW: Utility modules
│   ├── geospatial.py        # Area calculation from coordinates
│   ├── auth_middleware.py   # Route protection middleware
│   └── carbon_calculator.py # Credit calculation logic
│
├── main.py                    # FastAPI application entry point
├── database.py                # Database configuration
├── auth.py                    # Authentication logic
├── config.py                  # Application settings
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── .gitignore                 # Git ignore rules
```

---

## NEW FARM SERVICE ROUTE - SYSTEM DESIGN

### 1. DATABASE SCHEMA

**New Farm Model (`models/farm.py`)**

```python
# Conceptual structure - NOT full code

class Farm:
    """
    Stores individual farm records with geospatial data
    """
    Fields:
    - farm_id: Primary key (UUID or auto-increment)
    - farmer_id: Foreign key to User.id
    - farm_name: String (optional, defaults to "Farm #X")
    - phone: String (farmer contact)
    - latitude: Float (coordinate)
    - longitude: Float (coordinate)
    - area_hectares: Float (calculated from polygon or entered)
    - soil_type: String (e.g., "Loamy", "Clay", "Sandy")
    - district: String
    - state: String
    - annual_credits: Float (calculated based on area + soil type)
    - annual_value_inr: Float (credits × market rate)
    - polygon_coordinates: JSON (array of lat/lon for boundary)
    - created_at: Timestamp
    - updated_at: Timestamp
    - is_verified: Boolean (validator approval status)
    
    Relationships:
    - belongs_to: User (farmer)
    - has_many: CarbonCreditTransactions
```

**User Model Update**

```python
# Add relationship in user.py
class User:
    # ... existing fields ...
    farms = relationship("Farm", back_populates="owner")
```

---

### 2. DATA FLOW & USER JOURNEY

#### **Phase 1: Farm Registration**

```
USER ACTION → SYSTEM RESPONSE

1. Farmer logs in → Auth token stored in localStorage/session
2. Navigates to /farmservice → Middleware checks token validity
3. Clicks "Add New Farm" → Opens registration modal/form

FORM INPUTS:
- Farm Name (optional)
- Phone Number (auto-filled from profile)
- District (dropdown from Indian districts dataset)
- State (auto-populated based on district)
- Soil Type (dropdown: Loamy, Clay, Sandy, Mixed)

MAP INTERACTION:
- User clicks "Draw on Map" → Activates Leaflet/Google Maps drawing tool
- User draws polygon around farm boundary
- System captures array of [lat, lon] coordinates

AUTOMATIC CALCULATIONS:
- Area Calculation: Shoelace formula on polygon coordinates → hectares
- Annual Credits: area_hectares × soil_type_factor × regional_coefficient
- Annual Value: annual_credits × current_market_rate_per_credit

4. Submit → POST /api/farmservice/farms
   Backend validates:
   - User authentication
   - Coordinate data validity
   - No overlapping farms (spatial query)
   
5. Success → Farm saved with farmer_id = current_user.id
```

---

### 3. GEOSPATIAL AREA CALCULATION

**How Map Calculates Area (`utils/geospatial.py`)**

```python
PROCESS:

1. User draws polygon on map (Leaflet Draw or Google Maps Drawing Manager)
2. Frontend captures coordinates array:
   polygon = [
     [lat1, lon1],
     [lat2, lon2],
     ...
     [latN, lonN]
   ]

3. Frontend sends to backend OR calculates client-side using:
   
   METHOD A - Shoelace Formula (for small areas):
   - Converts lat/lon to meters using Haversine
   - Applies shoelace algorithm
   - Returns square meters → hectares
   
   METHOD B - Geodesic Calculation (for accuracy):
   - Uses geopy/shapely library
   - Accounts for Earth's curvature
   - More accurate for large farms

4. Result stored in area_hectares field

FORMULA SIMPLIFIED:
area_m² = abs(sum(x[i] * y[i+1] - x[i+1] * y[i]) / 2)
area_hectares = area_m² / 10000
```

---

### 4. API ENDPOINTS

**New Router: `routers/farmservice.py`**

```python
ENDPOINTS STRUCTURE:

GET /farmservice
→ Renders farmservice.html (protected route)
→ Requires: Valid JWT token

GET /api/farmservice/farms
→ Returns all farms for logged-in farmer
→ Response: {
    "total_farms": 5,
    "total_area": 12.5,
    "total_credits": 156.25,
    "total_value": 78125.00,
    "farms": [
      {
        "farm_id": "f001",
        "farm_name": "North Field",
        "area_hectares": 2.5,
        "soil_type": "Loamy",
        "annual_credits": 31.25,
        "annual_value_inr": 15625,
        "coordinates": [[lat, lon], ...]
      },
      ...
    ]
  }

POST /api/farmservice/farms
→ Creates new farm
→ Request Body: {
    "farm_name": "Optional Name",
    "phone": "9876543210",
    "district": "Pune",
    "state": "Maharashtra",
    "soil_type": "Loamy",
    "polygon_coordinates": [[lat, lon], ...]
  }
→ Backend Process:
  1. Verify user authentication
  2. Calculate area from coordinates
  3. Calculate credits: area × soil_factor × 12.5
  4. Calculate value: credits × 500 INR
  5. Save to database
  6. Return created farm object

PUT /api/farmservice/farms/{farm_id}
→ Updates farm details (only owner can update)
→ Recalculates area if coordinates changed

DELETE /api/farmservice/farms/{farm_id}
→ Soft delete (mark as inactive)
→ Only owner can delete

GET /api/farmservice/statistics
→ Returns aggregated stats for farmer's dashboard
```

---

### 5. CARBON CREDIT CALCULATION LOGIC

**How Credits Are Generated (`utils/carbon_calculator.py`)**

```python
CALCULATION FORMULA:

annual_credits = area_hectares × soil_multiplier × base_rate

SOIL TYPE MULTIPLIERS:
- Loamy Soil: 1.2x (best carbon sequestration)
- Clay Soil: 1.0x (standard)
- Sandy Soil: 0.8x (lower retention)
- Mixed Soil: 1.0x (average)

BASE RATE: 12.5 credits per hectare per year

EXAMPLE:
Farm with 2.5 hectares of Loamy soil:
2.5 × 1.2 × 12.5 = 37.5 credits/year

MARKET VALUE:
annual_value_inr = annual_credits × 500 (current rate)
37.5 credits × ₹500 = ₹18,750/year

VERIFICATION MULTIPLIER:
- Unverified farms: 0.5x credits (pending validation)
- Verified farms: 1.0x credits (full value)
```

---

### 6. FRONTEND ROUTE PROTECTION

**Authentication Middleware (`utils/auth_middleware.py`)**

```python
PROTECTION STRATEGY:

1. ALL PROTECTED ROUTES:
   - /dashboard
   - /profile
   - /farmservice ← NEW
   - /profile/edit

2. MIDDLEWARE FLOW:
   
   Request → Check JWT in Cookie/Header
   ↓
   Valid? → Allow access
   ↓
   Invalid/Missing? → Redirect to /login?next=/farmservice
   
3. IMPLEMENTATION:
   - Backend: FastAPI Depends() decorator
   - Frontend: JavaScript checks on page load
   
4. TOKEN VALIDATION:
   - Check signature
   - Check expiration
   - Verify user_id exists in database
   - Check user.is_active = True

EXAMPLE CHECK (conceptual):
async def get_current_user(token: str):
    if not token:
        raise HTTPException(401, "Not authenticated")
    user = verify_jwt(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return user
```

---

### 7. UI/UX DESIGN - FARMSERVICE PAGE

**Layout Structure (`templates/farmservice.html`)**

```
┌─────────────────────────────────────────────────┐
│  NAVBAR (from base.html)                        │
│  [Logo] [Dashboard] [FarmService*] [Leaderboard]│
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  STATISTICS HEADER                              │
│  ┌───────────┬───────────┬───────────┬────────┐│
│  │ Total     │ Total     │ Annual    │ Annual ││
│  │ Farms: 5  │ Area:     │ Credits:  │ Value: ││
│  │           │ 12.5 ha   │ 156.25    │ ₹78,125││
│  └───────────┴───────────┴───────────┴────────┘│
│  [+ Add New Farm] [Export Data]                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  FARM CARDS GRID (3 columns)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────┐│
│  │ FARM #1     │ │ FARM #2     │ │ FARM #3   ││
│  │ North Field │ │ South Plot  │ │ East Farm ││
│  │             │ │             │ │           ││
│  │ [Map View]  │ │ [Map View]  │ │ [Map View]││
│  │             │ │             │ │           ││
│  │ Area: 2.5ha │ │ Area: 4.0ha │ │ Area: 6.0││
│  │ Soil: Loamy │ │ Soil: Clay  │ │ Soil: Mix││
│  │ Credits: 31 │ │ Credits: 50 │ │ Credits:75││
│  │ Value:₹15.6K│ │ Value:₹25K  │ │Value:₹37K││
│  │             │ │             │ │           ││
│  │ [Edit][View]│ │ [Edit][View]│ │[Edit][Del]││
│  └─────────────┘ └─────────────┘ └───────────┘│
└─────────────────────────────────────────────────┘
```

**Interactive Features:**

```javascript
MAP INTEGRATION (Leaflet.js):

1. Small thumbnail maps in each card
2. Click card → Opens modal with full-size map
3. Drawing mode for new farms:
   - Polygon tool for irregular shapes
   - Circle tool for approximate areas
   - Edit vertices after drawing
   
4. Color coding:
   - Green: Verified farms
   - Yellow: Pending verification
   - Red: Rejected/inactive

REAL-TIME UPDATES:
- Add farm → Card appears instantly (optimistic UI)
- Edit area → Credits/value recalculate on blur
- Delete → Fade out animation
```

---

### 8. COMPLETE USER FLOW EXAMPLE

**Scenario: New Farmer Adds First Farm**

```
STEP 1: AUTHENTICATION
User visits /farmservice
→ Middleware checks JWT token
→ No token found
→ Redirect to /login?next=/farmservice

STEP 2: LOGIN
User enters credentials
→ POST /api/auth/login
→ Backend validates
→ Returns JWT token
→ Stored in httpOnly cookie
→ Redirect to /farmservice

STEP 3: FARMSERVICE PAGE LOAD
GET /farmservice
→ Middleware validates token ✓
→ Renders farmservice.html
→ JavaScript auto-fetches: GET /api/farmservice/farms
→ Returns empty array (first-time user)
→ Displays "No farms yet" message

STEP 4: ADD FARM
Click "+ Add New Farm"
→ Opens modal with form + map

Form fills:
- Farm Name: "Sunrise Acres"
- Phone: 9876543210 (pre-filled)
- District: Pune (dropdown)
→ State: Maharashtra (auto-set)
- Soil Type: Loamy (dropdown)

Map interaction:
→ Click "Draw Boundary"
→ User clicks 4 points on map
→ Polygon closes automatically
→ JavaScript calculates area: 3.2 hectares
→ Display preview: "Estimated 3.2 ha"

STEP 5: BACKEND PROCESSING
Click "Submit"
→ POST /api/farmservice/farms
→ Request payload:
{
  "farm_name": "Sunrise Acres",
  "phone": "9876543210",
  "district": "Pune",
  "state": "Maharashtra",
  "soil_type": "Loamy",
  "polygon_coordinates": [
    [18.5204, 73.8567],
    [18.5214, 73.8567],
    [18.5214, 73.8577],
    [18.5204, 73.8577]
  ]
}

Backend executes:
1. Extract farmer_id from JWT token
2. Validate coordinates (4+ points, closed polygon)
3. Calculate area using Shoelace formula:
   → 3.2 hectares
4. Calculate credits:
   → 3.2 × 1.2 (Loamy) × 12.5 = 48 credits
5. Calculate value:
   → 48 × 500 = ₹24,000
6. Insert into database:
   INSERT INTO farms VALUES (
     farm_id='f-uuid-001',
     farmer_id='user-123',
     farm_name='Sunrise Acres',
     area_hectares=3.2,
     annual_credits=48,
     annual_value_inr=24000,
     is_verified=FALSE,
     ...
   )
7. Return created farm object

STEP 6: UI UPDATE
→ Modal closes
→ New farm card appears
→ Statistics update:
  Total Farms: 0 → 1
  Total Area: 0 → 3.2 ha
  Annual Credits: 0 → 48
  Annual Value: ₹0 → ₹24,000
```

---

### 9. DATA SOURCES & POPULATION

**Where Data Comes From:**

```
FARMER INFORMATION:
- farmer_id: From User.id (logged-in user)
- name: From User.full_name
- phone: From User.phone OR farm-specific input
→ Source: User registration + profile

LOCATION DATA:
- district/state: Dropdown from static JSON file
  (indian_districts.json with 700+ districts)
- lat/lon: User interaction with map widget
→ Source: Manual selection/drawing

FARM DETAILS:
- area_hectares: CALCULATED from polygon coordinates
- soil_type: User selects from predefined list
→ Source: User input + calculation

FINANCIAL DATA:
- annual_credits: CALCULATED (area × soil × base_rate)
- annual_value_inr: CALCULATED (credits × market_rate)
→ Source: Backend computation on save/update

STATIC DATA REQUIREMENTS:
1. indian_districts.json (district→state mapping)
2. soil_types.json (type→multiplier mapping)
3. market_rates table (dynamic pricing)
```

**Database Seeding (Optional for Testing):**

```python
# seed_data.py - Sample farms for development

def seed_sample_farms():
    """
    Creates 5 sample farms for user_id='demo-farmer'
    Used in development environment only
    """
    sample_farms = [
      {
        "farm_name": "North Field",
        "area_hectares": 2.5,
        "district": "Pune",
        "soil_type": "Loamy",
        "polygon": [[18.52, 73.85], [18.52, 73.86], ...]
      },
      # ... 4 more farms
    ]
    # Insert into database
```

---

### 10. API RESPONSE EXAMPLES

**GET /api/farmservice/farms (Success)**

```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_farms": 5,
      "total_area_hectares": 12.5,
      "total_annual_credits": 156.25,
      "total_annual_value_inr": 78125.00,
      "verified_farms": 3,
      "pending_verification": 2
    },
    "farms": [
      {
        "farm_id": "f-001",
        "farm_name": "North Field",
        "phone": "9876543210",
        "district": "Pune",
        "state": "Maharashtra",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "area_hectares": 2.5,
        "soil_type": "Loamy",
        "annual_credits": 37.5,
        "annual_value_inr": 18750,
        "is_verified": true,
        "polygon_coordinates": [
          [18.5204, 73.8567],
          [18.5214, 73.8567],
          [18.5214, 73.8577],
          [18.5204, 73.8577]
        ],
        "created_at": "2025-01-15T10:30:00Z",
        "verified_at": "2025-01-20T14:22:00Z"
      }
      // ... more farms
    ]
  }
}
```

---

### 11. SECURITY & VALIDATION

**Route Protection Implementation:**

```python
# Conceptual middleware structure

FRONTEND (JavaScript):
- On page load: Check if localStorage has 'auth_token'
- If missing: window.location = '/login?next=' + current_path
- If present: Include in Authorization header for API calls

BACKEND (FastAPI):
- Every /api/farmservice/* route requires:
  @router.get("/farms", dependencies=[Depends(get_current_user)])
  
- get_current_user function:
  1. Extract token from cookie/header
  2. Decode JWT
  3. Query database for user
  4. Return user object OR raise 401

- Ownership validation:
  If updating/deleting farm:
    - Verify farm.farmer_id == current_user.id
    - Else raise 403 Forbidden

DATA VALIDATION:
- Pydantic schemas validate:
  * area_hectares > 0
  * soil_type in allowed_list
  * polygon has min 3 coordinates
  * district exists in reference data
  * phone matches Indian format
```

---

### 12. TECHNOLOGY STACK UPDATES

**New Dependencies (requirements.txt additions):**

```
# Existing dependencies remain unchanged
# Add these new packages:

geopy==2.4.1              # Geodesic calculations
shapely==2.0.2            # Polygon operations
pyproj==3.6.1             # Coordinate transformations
```

**Frontend Libraries:**

```html
<!-- Add to base.html -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
```

---

### 13. MAP VISUALIZATION DETAILS

**Leaflet Map Configuration:**

```javascript
// Conceptual map initialization

On farmservice.html load:
1. Initialize base map centered on India
   - Zoom level: 5 (country view)
   - Tile layer: OpenStreetMap

2. For each farm card:
   - Create miniature map (300x200px)
   - Center on farm coordinates
   - Draw polygon from saved coordinates
   - Zoom to fit farm boundary

3. Add New Farm modal:
   - Full-screen map (100% viewport)
   - Drawing controls enabled
   - Polygon/Circle tools active
   - Real-time area calculation display
   
4. Color scheme:
   - Verified farms: #10b981 (green)
   - Pending: #f59e0b (yellow)
   - User's location marker: #ef4444 (red pin)

5. Interactivity:
   - Click farm card → Popup with details
   - Hover → Highlight border
   - Edit mode → Draggable vertices
```

---

### 14. ERROR HANDLING & EDGE CASES

**Common Scenarios:**

```
CASE 1: Overlapping Farms
- User draws farm boundary over existing farm
→ Backend spatial query detects overlap
→ Return 400: "Farm boundary overlaps with Farm #3"
→ UI highlights conflict on map

CASE 2: Invalid Polygon
- User draws self-intersecting polygon
→ Shapely validation fails
→ Return 400: "Invalid polygon shape"
→ UI shows error + resets drawing

CASE 3: Token Expiration
- User idle for 24 hours, token expires
- Tries to add farm
→ API returns 401
→ Frontend catches error
→ Redirect to /login with message: "Session expired"

CASE 4: Network Failure During Submit
- Farm saved but response lost
→ Frontend shows error
→ User retries
→ Backend detects duplicate (same coordinates + timestamp)
→ Return existing farm instead of creating new

CASE 5: GPS Inaccuracy
- Mobile user's location jumps erratically
→ Frontend validates coordinates before sending
→ Check distance between consecutive points
→ Reject if > 500m jump between adjacent vertices
```

---

### 15. PERFORMANCE OPTIMIZATION

**Database Indexing:**

```sql
-- Conceptual index strategy

CREATE INDEX idx_farmer_farms ON farms(farmer_id);
CREATE SPATIAL INDEX idx_farm_location ON farms(latitude, longitude);
CREATE INDEX idx_farm_status ON farms(is_verified, farmer_id);
```

**API Response Caching:**

```python
# Cache farm statistics for 5 minutes
# Invalidate on farm create/update/delete

@cache(expire=300)
def get_farmer_statistics(farmer_id):
    # Aggregate queries
    return stats
```

**Frontend Optimization:**

```javascript
// Lazy load map tiles
// Only load visible farms' detailed data
// Paginate if > 20 farms (unlikely for individual farmers)
// Compress polygon coordinates (remove redundant precision)
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Backend Foundation (Week 1)
- [ ] Create Farm model with geospatial fields
- [ ] Implement area calculation utility
- [ ] Build farmservice router with CRUD endpoints
- [ ] Add authentication middleware to protect routes
- [ ] Write unit tests for calculations

### Phase 2: Frontend Development (Week 2)
- [ ] Design farmservice.html template
- [ ] Integrate Leaflet map with drawing tools
- [ ] Build farm card components
- [ ] Implement statistics dashboard
- [ ] Add real-time validation feedback

### Phase 3: Integration & Testing (Week 3)
- [ ] Connect frontend to backend APIs
- [ ] Test end-to-end farm creation flow
- [ ] Validate area calculations against known values
- [ ] Security audit on route protection
- [ ] Performance testing with 50+ farms per user

### Phase 4: Polish & Deploy (Week 4)
- [ ] Mobile responsive design
- [ ] Error handling & user feedback
- [ ] Documentation & help tooltips
- [ ] Production deployment
- [ ] User acceptance testing

---

## KEY DECISIONS TO MAKE

1. **Map Provider**: Leaflet (open-source) vs Google Maps (paid but feature-rich)?
2. **Area Calculation**: Client-side (faster) vs Server-side (more secure)?
3. **Verification Workflow**: Auto-approve vs manual validator review?
4. **Credit Market Rate**: Static ₹500 vs dynamic pricing model?
5. **Farm Limit**: Unlimited farms vs cap at 10 per farmer?

---

## CONCLUSION

This system enables farmers to:
- **Register farms** using intuitive map drawing
- **Track carbon credits** automatically calculated from farm data
- **Monitor earnings** in real-time
- **Manage multiple farms** from a single dashboard
