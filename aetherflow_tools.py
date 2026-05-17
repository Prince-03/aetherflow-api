from langchain.tools import tool
import math
import random

# Massive Mock Database for Simulation
mock_db = {
    # Electronics & Tech
    "SKU-1001": {"sku": "SKU-1001", "name": "Wireless Earbuds Basic", "current_stock": 150, "reorder_point": 500, "unit_cost": 15.00, "holding_cost_pct": 0.15, "base_annual_demand": 12000, "category": "Electronics"},
    "SKU-1002": {"sku": "SKU-1002", "name": "USB-C Cables (3-Pack)", "current_stock": 850, "reorder_point": 1000, "unit_cost": 4.50, "holding_cost_pct": 0.10, "base_annual_demand": 25000, "category": "Electronics"},
    "SKU-1003": {"sku": "SKU-1003", "name": "Smart Home Hub Pro", "current_stock": 200, "reorder_point": 150, "unit_cost": 180.00, "holding_cost_pct": 0.12, "base_annual_demand": 1200, "category": "Electronics"},
    "SKU-1004": {"sku": "SKU-1004", "name": "Mechanical Keyboard (Blue Switch)", "current_stock": 45, "reorder_point": 120, "unit_cost": 45.00, "holding_cost_pct": 0.20, "base_annual_demand": 3500, "category": "Electronics"},
    
    # Wellness & Fitness
    "SKU-2001": {"sku": "SKU-2001", "name": "Eco-Friendly Yoga Mat", "current_stock": 80, "reorder_point": 150, "unit_cost": 22.00, "holding_cost_pct": 0.25, "base_annual_demand": 3000, "category": "Wellness"},
    "SKU-2002": {"sku": "SKU-2002", "name": "Adjustable Dumbbell Set", "current_stock": 12, "reorder_point": 50, "unit_cost": 85.00, "holding_cost_pct": 0.30, "base_annual_demand": 800, "category": "Wellness"},
    "SKU-2003": {"sku": "SKU-2003", "name": "Matcha Green Tea Powder (Premium)", "current_stock": 400, "reorder_point": 300, "unit_cost": 18.00, "holding_cost_pct": 0.20, "base_annual_demand": 5000, "category": "Wellness"},
    "SKU-2004": {"sku": "SKU-2004", "name": "Foam Roller (High Density)", "current_stock": 310, "reorder_point": 200, "unit_cost": 8.50, "holding_cost_pct": 0.15, "base_annual_demand": 6000, "category": "Wellness"},

    # Viral / Trending (Highly Volatile)
    "SKU-3001": {"sku": "SKU-3001", "name": "Vintage Graphic Tee", "current_stock": 500, "reorder_point": 200, "unit_cost": 12.00, "holding_cost_pct": 0.35, "base_annual_demand": 8000, "category": "Apparel"},
    "SKU-3002": {"sku": "SKU-3002", "name": "LED Room Light Strips", "current_stock": 120, "reorder_point": 400, "unit_cost": 8.00, "holding_cost_pct": 0.15, "base_annual_demand": 15000, "category": "Home Goods"},
    "SKU-3003": {"sku": "SKU-3003", "name": "Stanley Quencher Tumbler (Pink)", "current_stock": 5, "reorder_point": 100, "unit_cost": 25.00, "holding_cost_pct": 0.10, "base_annual_demand": 20000, "category": "Viral/Trending"},
    "SKU-3004": {"sku": "SKU-3004", "name": "Sunset Projection Lamp", "current_stock": 30, "reorder_point": 500, "unit_cost": 10.00, "holding_cost_pct": 0.20, "base_annual_demand": 25000, "category": "Viral/Trending"},

    # Hardware & Tools
    "SKU-4001": {"sku": "SKU-4001", "name": "Professional Cordless Drill", "current_stock": 45, "reorder_point": 30, "unit_cost": 120.00, "holding_cost_pct": 0.08, "base_annual_demand": 400, "category": "Hardware"},
    "SKU-4002": {"sku": "SKU-4002", "name": "100-Piece Mechanics Tool Set", "current_stock": 85, "reorder_point": 100, "unit_cost": 65.00, "holding_cost_pct": 0.10, "base_annual_demand": 1500, "category": "Hardware"},
    "SKU-4003": {"sku": "SKU-4003", "name": "Heavy Duty Duct Tape (Pack of 5)", "current_stock": 900, "reorder_point": 500, "unit_cost": 5.00, "holding_cost_pct": 0.05, "base_annual_demand": 10000, "category": "Hardware"},

    # Grocery / Perishables
    "SKU-5001": {"sku": "SKU-5001", "name": "Organic Cold-Pressed Juice", "current_stock": 50, "reorder_point": 100, "unit_cost": 35.00, "holding_cost_pct": 0.60, "base_annual_demand": 4000, "category": "Grocery"},
    "SKU-5002": {"sku": "SKU-5002", "name": "Artisan Coffee Beans (1lb)", "current_stock": 180, "reorder_point": 150, "unit_cost": 14.00, "holding_cost_pct": 0.25, "base_annual_demand": 6500, "category": "Grocery"},
    "SKU-5003": {"sku": "SKU-5003", "name": "Gluten-Free Oats", "current_stock": 420, "reorder_point": 300, "unit_cost": 3.50, "holding_cost_pct": 0.15, "base_annual_demand": 12000, "category": "Grocery"},
}

trends_db = {
    "SKU-1001": 1.05, "SKU-1002": 0.98, "SKU-1003": 1.15, "SKU-1004": 1.30,
    "SKU-2001": 1.20, "SKU-2002": 0.85, "SKU-2003": 1.60, "SKU-2004": 1.05,
    "SKU-3001": 0.60, "SKU-3002": 1.10, "SKU-3003": 3.50, "SKU-3004": 4.10,
    "SKU-4001": 1.00, "SKU-4002": 0.95, "SKU-4003": 1.02,
    "SKU-5001": 1.02, "SKU-5002": 1.15, "SKU-5003": 1.00,
}

def get_all_inventory():
    """Helper for the FastAPI server to send all available inventory items to the React frontend."""
    inventory_list = []
    for sku, data in mock_db.items():
        item_data = data.copy()
        item_data["trend"] = trends_db.get(sku, 1.0) # Attach the trend for the frontend fallback simulation
        inventory_list.append(item_data)
    return inventory_list


# 1. Sense: Check internal inventory
@tool
def get_inventory_status(sku: str) -> dict:
    """Fetches current inventory data for a specific SKU."""
    return mock_db.get(sku, "SKU not found.")

# 2. Sense: Check external market trends
@tool
def get_social_trend_multiplier(sku: str) -> float:
    """Checks social media sentiment and returns a demand multiplier."""
    base_trend = trends_db.get(sku, 1.0)
    # Adding a +/- 5% random noise to make the simulation less deterministic
    noise = random.uniform(-0.05, 0.05)
    return round(base_trend + noise, 2)

# 3. Think/Act: Calculate optimized order quantity
@tool
def calculate_dynamic_eoq(base_annual_demand: int, order_cost: float, holding_cost_per_unit: float, trend_multiplier: float) -> int:
    """Calculates the Economic Order Quantity (EOQ) adjusted for real-time market trends."""
    adjusted_demand = base_annual_demand * trend_multiplier
    
    if holding_cost_per_unit <= 0:
        return 0
        
    eoq = math.sqrt((2 * adjusted_demand * order_cost) / holding_cost_per_unit)
    return int(eoq)

# 4. Act: Draft the Purchase Order
@tool
def draft_purchase_order(sku: str, quantity: int) -> str:
    """Drafts a purchase order for human approval."""
    if quantity <= 0:
         return f"SKIPPED: Calculated order quantity for {sku} is {quantity}. No PO drafted."
    return f"SUCCESS: Drafted PO for {quantity} units of {sku}. Status: Pending Human Approval."
