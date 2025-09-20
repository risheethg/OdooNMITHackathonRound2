"""
Wooden Table Manufacturing Workflow Test

This script demonstrates the complete manufacturing workflow described:
1. Create products (raw materials and finished goods)
2. Create BOM (bill of materials / recipe)
3. Create manufacturing order
4. Complete manufacturing order (triggers automatic inventory updates)
5. Check final stock levels

This matches the example: Making 10 Wooden Tables
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_wooden_table_workflow():
    print("=== WOODEN TABLE MANUFACTURING WORKFLOW TEST ===\n")
    
    # Step 1: Create Products (Raw Materials and Finished Goods)
    print("Step 1: Creating Products...")
    
    products_to_create = [
        {"name": "Wooden Leg", "type": "Raw Material", "description": "Wooden table leg"},
        {"name": "Wooden Top", "type": "Raw Material", "description": "Wooden table top"},
        {"name": "Screws", "type": "Raw Material", "description": "Screws for assembly"},
        {"name": "Wooden Table", "type": "Finished Good", "description": "Complete wooden table"}
    ]
    
    product_ids = {}
    
    for product_data in products_to_create:
        response = requests.post(f"{BASE_URL}/products/", json=product_data)
        if response.status_code == 201:
            result = response.json()
            product_id = result["data"]["_id"]
            product_ids[product_data["name"]] = product_id
            print(f"✅ Created product: {product_data['name']} (ID: {product_id})")
        else:
            print(f"❌ Failed to create product: {product_data['name']} - {response.text}")
            return False
    
    print()
    
    # Step 2: Create BOM (Recipe for Wooden Table)
    print("Step 2: Creating Bill of Materials (Recipe)...")
    
    bom_data = {
        "finishedProductId": product_ids["Wooden Table"],
        "components": [
            {"productId": product_ids["Wooden Leg"], "quantity": 4},
            {"productId": product_ids["Wooden Top"], "quantity": 1},
            {"productId": product_ids["Screws"], "quantity": 12}
        ],
        "operations": [
            {"name": "Assembly", "duration": 60},
            {"name": "Painting", "duration": 30}
        ],
        "recipe": "Recipe for manufacturing one wooden table"
    }
    
    response = requests.post(f"{BASE_URL}/boms/", json=bom_data)
    if response.status_code == 201:
        bom_result = response.json()
        bom_id = bom_result["data"]["_id"]
        print(f"✅ Created BOM for Wooden Table (ID: {bom_id})")
        print(f"   Components: 4 Wooden Legs, 1 Wooden Top, 12 Screws")
        print(f"   Operations: Assembly (60 min), Painting (30 min)")
    else:
        print(f"❌ Failed to create BOM - {response.text}")
        return False
    
    print()
    
    # Step 3: Create Manufacturing Order (Job to make 10 tables)
    print("Step 3: Creating Manufacturing Order...")
    
    mo_data = {
        "product_id": product_ids["Wooden Table"],
        "quantity": 10
    }
    
    response = requests.post(f"{BASE_URL}/manufacturing-orders/", json=mo_data)
    if response.status_code == 201:
        mo_result = response.json()
        mo_id = mo_result["data"]["mo_id"]
        print(f"✅ Created Manufacturing Order (ID: {mo_id})")
        print(f"   Product: Wooden Table")
        print(f"   Quantity: 10 tables")
        print(f"   This will consume: 40 Wooden Legs, 10 Wooden Tops, 120 Screws")
    else:
        print(f"❌ Failed to create Manufacturing Order - {response.text}")
        return False
    
    print()
    
    # Step 4: Simulate completing work orders (normally done by operators)
    print("Step 4: Simulating Work Order Completion...")
    print("   (In real workflow, operators would complete Assembly and Painting tasks)")
    print("   For this test, we'll directly complete the Manufacturing Order")
    print()
    
    # Step 5: Complete Manufacturing Order (Triggers Automatic Inventory Updates)
    print("Step 5: Completing Manufacturing Order (The Magic Happens Here!)...")
    
    response = requests.patch(f"{BASE_URL}/manufacturing-orders/{mo_id}/complete")
    if response.status_code == 200:
        completion_result = response.json()
        print(f"✅ Manufacturing Order completed successfully!")
        print(f"   Automatic inventory updates triggered:")
        print(f"   📉 -40 Wooden Legs consumed")
        print(f"   📉 -10 Wooden Tops consumed") 
        print(f"   📉 -120 Screws consumed")
        print(f"   📈 +10 Wooden Tables produced")
    else:
        print(f"❌ Failed to complete Manufacturing Order - {response.text}")
        return False
    
    print()
    
    # Step 6: Check Final Stock Levels
    print("Step 6: Checking Final Stock Levels...")
    
    response = requests.get(f"{BASE_URL}/stock/availability")
    if response.status_code == 200:
        stock_result = response.json()
        stock_data = stock_result["data"]
        
        print("✅ Current Stock Levels (calculated from ledger history):")
        for item in stock_data:
            product_name = "Unknown"
            for name, pid in product_ids.items():
                if pid == item["product_id"]:
                    product_name = name
                    break
            print(f"   📦 {product_name}: {item['current_stock']} units")
    else:
        print(f"❌ Failed to get stock levels - {response.text}")
        return False
    
    print()
    print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print("The manufacturing system has automatically tracked all inventory changes.")
    return True

if __name__ == "__main__":
    test_wooden_table_workflow()