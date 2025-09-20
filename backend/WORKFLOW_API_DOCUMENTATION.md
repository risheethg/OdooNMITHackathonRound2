# Manufacturing Workflow API Documentation

## Complete API Endpoints for Wooden Table Manufacturing

This document maps the complete workflow described in your requirements to the actual API endpoints implemented.

### Phase 1: Setup (One-time preparation)

#### Step 1: Creating Products
**User Action**: Inventory Manager creates raw materials and finished goods

**API Calls**:
```
POST /products
```

**Example Requests**:
```json
// Create Wooden Leg
{
    "name": "Wooden Leg",
    "type": "Raw Material",
    "description": "Wooden table leg"
}

// Create Wooden Top  
{
    "name": "Wooden Top",
    "type": "Raw Material", 
    "description": "Wooden table top"
}

// Create Screws
{
    "name": "Screws",
    "type": "Raw Material",
    "description": "Screws for assembly"
}

// Create Wooden Table (finished product)
{
    "name": "Wooden Table",
    "type": "Finished Good",
    "description": "Complete wooden table"
}
```

**What the API Does**: Creates product documents in the database and returns product IDs.

#### Step 2: Defining the Recipe (Bill of Materials)
**User Action**: Manufacturing Manager creates BOM with components and operations

**API Call**:
```
POST /boms
```

**Example Request**:
```json
{
    "finishedProductId": "wooden_table_product_id",
    "components": [
        {"productId": "wooden_leg_id", "quantity": 4},
        {"productId": "wooden_top_id", "quantity": 1}, 
        {"productId": "screws_id", "quantity": 12}
    ],
    "operations": [
        {"name": "Assembly", "duration": 60},
        {"name": "Painting", "duration": 30}
    ],
    "recipe": "Recipe for manufacturing one wooden table"
}
```

**What the API Does**: 
- Validates all product IDs exist
- Creates BOM document linking finished product to components and operations
- Stores the recipe for future manufacturing orders

### Phase 2: Production (Making the Tables)

#### Step 3: Creating the Manufacturing Order
**User Action**: Manager creates order to produce 10 Wooden Tables

**API Call**:
```
POST /manufacturing-orders
```

**Example Request**:
```json
{
    "product_id": "wooden_table_product_id",
    "quantity": 10
}
```

**What the API Does**:
- Finds BOM for the product
- Calculates total material requirements (40 legs, 10 tops, 120 screws)
- Creates Manufacturing Order with status "planned"
- Automatically creates Work Orders for each operation (Assembly, Painting)
- Stores BOM snapshot to preserve recipe at time of order

#### Step 4: Executing Work Orders
**User Action**: Operators start and complete individual tasks

**API Call**:
```
PATCH /work-orders/{work_order_id}/status
```

**Example Request**:
```json
{
    "status": "in_progress"  // or "done"
}
```

**What the API Does**: Updates work order status in database

### Phase 3: Completion & Reporting

#### Step 5: Finalizing Manufacturing Order (THE CRITICAL AUTOMATION)
**User Action**: Manager marks entire job as complete

**API Call**:
```
PATCH /manufacturing-orders/{mo_id}/complete
```

**What the API Does** (The Automation Magic):
1. Validates MO exists and is ready for completion
2. Reads BOM snapshot and quantity from the MO
3. Automatically creates stock ledger entries:
   - **Consumption entries** (negative):
     - -40 Wooden Legs
     - -10 Wooden Tops  
     - -120 Screws
   - **Production entry** (positive):
     - +10 Wooden Tables
4. Updates MO status to "done"

#### Step 6: Checking Inventory
**User Action**: Check current stock levels

**API Call**:
```
GET /stock/availability
```

**What the API Does**:
- Reads ALL historical transactions from stock_ledger
- Aggregates using MongoDB pipeline to sum all quantity changes
- Returns real-time calculated stock levels for every product
- No static inventory numbers - always calculated from complete history

### Additional Available Endpoints

**Get all products**:
```
GET /products
GET /products/{product_id}
```

**Get BOMs**:
```
GET /boms
GET /boms/{bom_id}
GET /boms/product/{product_id}  // Get BOM for specific product
```

**Get Manufacturing Orders**:
```
GET /manufacturing-orders
GET /manufacturing-orders/{mo_id}
GET /manufacturing-orders?status=planned  // Filter by status
```

**Get Stock Ledger History**:
```
GET /stock-ledger/  // Complete transaction history
GET /stock-ledger/availability  // Alternative stock levels endpoint
```

### Key Implementation Features

1. **Real-time Inventory**: Stock levels always calculated from complete transaction history
2. **Automatic Updates**: MO completion triggers automatic inventory adjustments  
3. **Data Integrity**: BOM snapshots preserve recipes even if original BOM changes
4. **Validation**: All product IDs validated before creating BOMs or MOs
5. **Audit Trail**: Complete history of all inventory movements preserved
6. **Error Handling**: Comprehensive validation and error responses

### Workflow Summary
```
Products → BOM → Manufacturing Order → Work Orders → Complete MO → Updated Inventory
   ↓         ↓           ↓               ↓              ↓            ↓
POST      POST        POST           PATCH         PATCH        GET
/products /boms  /manufacturing- /work-orders/  /manufacturing- /stock/
                  orders         {id}/status    orders/{id}/   availability
                                                complete
```

This implementation provides exactly the workflow you described, with automatic inventory management and real-time calculated stock levels.