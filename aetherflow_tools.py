from langchain.tools import tool
import math
import random

# 1. Sense: Check internal inventory
@tool
def get_inventory_status(sku: str) -> dict:
    """Fetches current inventory data for a specific SKU."""
    # Expanded mock DB to mirror real-world retail categories with varying margins, holding costs, and volumes.
    mock_db = {
        # High Volume, Low Margin, High Competition (e.g., Basic Electronics Accessories)
        "SKU-1001": {"name": "Wireless Earbuds Basic", "current_stock": 150, "reorder_point": 500, "unit_cost": 15.00, "holding_cost_pct": 0.15, "base_annual_demand": 12000},
        "SKU-1002": {"name": "USB-C Charging Cables (3-Pack)", "current_stock": 850, "reorder_point": 1000, "unit_cost": 4.50, "holding_cost_pct": 0.10, "base_annual_demand": 25000},
        
        # High Margin, Trend-Driven, Moderate Volume (e.g., Niche Fitness/Wellness)
        "SKU-2001": {"name": "Eco-Friendly Yoga Mat", "current_stock": 80, "reorder_point": 150, "unit_cost": 22.00, "holding_cost_pct": 0.25, "base_annual_demand": 3000},
        "SKU-2002": {"name": "Adjustable Dumbbell Set", "current_stock": 12, "reorder_point": 50, "unit_cost": 85.00, "holding_cost_pct": 0.30, "base_annual_demand": 800},
        "SKU-2003": {"name": "Matcha Green Tea Powder (Premium)", "current_stock": 400, "reorder_point": 300, "unit_cost": 18.00, "holding_cost_pct": 0.20, "base_annual_demand": 5000},

        # Seasonal/Viral, Volatile Demand (e.g., Trendy Apparel/Novelty)
        "SKU-3001": {"name": "Oversized Vintage Graphic Tee", "current_stock": 500, "reorder_point": 200, "unit_cost": 12.00, "holding_cost_pct": 0.35, "base_annual_demand": 8000},
        "SKU-3002": {"name": "LED Room Light Strips", "current_stock": 120, "reorder_point": 400, "unit_cost": 8.00, "holding_cost_pct": 0.15, "base_annual_demand": 15000},
        "SKU-3003": {"name": "Stanley Quencher Tumbler (Pink)", "current_stock": 5, "reorder_point": 100, "unit_cost": 25.00, "holding_cost_pct": 0.10, "base_annual_demand": 20000}, # Chronic stockout risk

        # Slow Mover, High Value, Low Holding Cost (e.g., Specialty Hardware/Tools)
        "SKU-4001": {"name": "Professional Cordless Drill", "current_stock": 45, "reorder_point": 30, "unit_cost": 120.00, "holding_cost_pct": 0.08, "base_annual_demand": 400},
        "SKU-4002": {"name": "Smart Home Hub Pro", "current_stock": 200, "reorder_point": 150, "unit_cost": 180.00, "holding_cost_pct": 0.12, "base_annual_demand": 1200},
        
        # Perishable / Shelf-Life Sensitive (High holding cost due to spoilage risk)
        "SKU-5001": {"name": "Organic Cold-Pressed Juice (12-Pack)", "current_stock": 50, "reorder_point": 100, "unit_cost": 35.00, "holding_cost_pct": 0.60, "base_annual_demand": 4000},
    }
    return mock_db.get(sku, "SKU not found.")

# 2. Sense: Check external market trends
@tool
def get_social_trend_multiplier(sku: str) -> float:
    """Checks social media sentiment and returns a demand multiplier."""
    # Simulating data scraped from TikTok/Twitter/Google Trends
    trends = {
        # Basic Electronics: Usually stable, minor fluctuations
        "SKU-1001": 1.05, 
        "SKU-1002": 0.98,
        
        # Fitness/Wellness: Seasonal spikes (e.g., New Year) or influencer mentions
        "SKU-2001": 1.20, # Rising trend in eco-friendly products
        "SKU-2002": 0.85, # Dip in interest as gym memberships rise
        "SKU-2003": 1.60, # Sudden viral TikTok recipe spike
        
        # Trendy/Novelty: Highly volatile
        "SKU-3001": 0.60, # Trend is dying down
        "SKU-3002": 1.10, # Steady influencer background presence
        "SKU-3003": 3.50, # Massive viral trend, severe shortage expected
        
        # Specialty/Hardware: Driven more by macro-economics than social media
        "SKU-4001": 1.00, # Stable
        "SKU-4002": 1.15, # Positive tech review recently published
        
        # Perishables: Stable unless recalled or newly popular
        "SKU-5001": 1.02, # Normal demand
    }
    # Return a slight random variation to simulate live, fuzzy data if SKU is found, else 1.0
    base_trend = trends.get(sku, 1.0)
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
        
    # EOQ Formula: sqrt((2 * Demand * OrderCost) / HoldingCost)
    # OrderCost represents the fixed cost of placing an order (shipping, admin, etc.)
    eoq = math.sqrt((2 * adjusted_demand * order_cost) / holding_cost_per_unit)
    
    # We shouldn't return fractional units
    return int(eoq)

# 4. Act: Draft the Purchase Order
@tool
def draft_purchase_order(sku: str, quantity: int) -> str:
    """Drafts a purchase order for human approval."""
    if quantity <= 0:
         return f"SKIPPED: Calculated order quantity for {sku} is {quantity}. No PO drafted."
    return f"SUCCESS: Drafted PO for {quantity} units of {sku}. Status: Pending Human Approval."

# Helper function to run a mock simulation for a single SKU
def simulate_agent_decision(sku: str, fixed_order_cost: float = 50.0):
    """Simulates the agent's reasoning process for a given SKU."""
    print(f"\n--- Running Agent Simulation for {sku} ---")
    
    # Step 1: Sense Internal
    inventory_data = get_inventory_status(sku)
    if isinstance(inventory_data, str): # "SKU not found."
        print(inventory_data)
        return
    
    print(f"Sense (Internal): {inventory_data['name']} - Current Stock: {inventory_data['current_stock']}, Reorder Point: {inventory_data['reorder_point']}")
    
    # Check if we need to order
    if inventory_data['current_stock'] > inventory_data['reorder_point']:
        print("Decision: Stock level healthy. No action required.")
        return

    # Step 2: Sense External
    trend = get_social_trend_multiplier(sku)
    print(f"Sense (External): Social Trend Multiplier is {trend}x")

    # Step 3: Think
    holding_cost_per_unit = inventory_data['unit_cost'] * inventory_data['holding_cost_pct']
    base_demand = inventory_data['base_annual_demand']
    
    optimal_qty = calculate_dynamic_eoq(
        base_annual_demand=base_demand,
        order_cost=fixed_order_cost,
        holding_cost_per_unit=holding_cost_per_unit,
        trend_multiplier=trend
    )
    
    print(f"Think (Analysis): Base Demand: {base_demand}, Adjusted Demand: {int(base_demand * trend)}.")
    print(f"Think (Analysis): Holding Cost/Unit: ${holding_cost_per_unit:.2f}. Calculated EOQ: {optimal_qty} units.")

    # Step 4: Act
    result = draft_purchase_order(sku, optimal_qty)
    print(f"Act: {result}")

if __name__ == "__main__":
    # Test a few different scenarios
    
    # Scenario A: Viral product, severely understocked (Stanley Cup)
    simulate_agent_decision("SKU-3003")
    
    # Scenario B: High volume, slightly below reorder point, stable trend (Earbuds)
    simulate_agent_decision("SKU-1001")
    
    # Scenario C: Stock level is healthy, should skip ordering (Cables)
    simulate_agent_decision("SKU-1002")
    
    # Scenario D: Dying trend, below reorder point (Vintage Tee)
    # Even though we need to reorder, the EOQ will be adjusted downward due to the low trend
    simulate_agent_decision("SKU-3001")