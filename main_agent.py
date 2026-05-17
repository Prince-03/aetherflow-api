import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import AgentExecutor

# --- The Self-Healing Import ---
# This tries the modern LangChain function first. 
# If your environment has an older version, it falls back seamlessly.
try:
    from langchain_classic.agents import create_tool_calling_agent as build_agent
except ImportError:
    from langchain_classic.agents import create_openai_tools_agent as build_agent

# Assuming inventory_agent.py holds your tools now based on previous artifact
from aetherflow_tools import (
    get_inventory_status, 
    get_social_trend_multiplier, 
    calculate_dynamic_eoq, 
    draft_purchase_order
)

# 1. API KEY SETUP
# Replace with your GitHub Personal Access Token (starts with ghp_ or github_pat_)
#api_key=os.environ.get("GITHUB_TOKEN")
# 2. INITIALIZE AI
# Configure LangChain to use GitHub Models via the Azure inference endpoint
llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0,
    api_key=os.environ.get("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

# 3. BIND TOOLS
tools = [
    get_inventory_status, 
    get_social_trend_multiplier, 
    calculate_dynamic_eoq, 
    draft_purchase_order
]

# 4. SET INSTRUCTIONS
# We updated the system prompt to instruct the agent to use the base_annual_demand 
# provided by the get_inventory_status tool instead of a hardcoded value.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are AetherFlow AI, an autonomous supply chain agent.\n"
               "1. Check inventory for the requested SKU.\n"
               "2. Check external social trends for the SKU.\n"
               "3. If the current stock is below the reorder point, you MUST calculate the Dynamic EOQ.\n"
               "   - For the EOQ calculation, use the 'base_annual_demand' from the inventory status.\n"
               "   - Assume a fixed order cost of $50.00.\n"
               "   - Calculate holding_cost_per_unit by multiplying 'unit_cost' by 'holding_cost_pct'.\n"
               "4. If the calculated EOQ is greater than 0, draft a purchase order for that quantity.\n"
               "   If stock is healthy (above reorder point), do not draft an order and explain why."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 5. ASSEMBLE AGENT
agent = build_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. EXECUTE WITH ERROR HANDLING
if __name__ == "__main__":
    print("--- Starting AetherFlow Agent Evaluation ---")
    
    # Let's test it with a few of the new SKUs to see the dynamic behavior
    test_skus = [
        "SKU-1001", # High volume, stock is low (150 vs 500 reorder point)
        "SKU-3003", # Viral Stanley Cup, chronic stockout (5 vs 100)
        "SKU-1002"  # Stock is healthy (850 vs 1000) - shouldn't order
    ]
    
    for sku in test_skus:
        print(f"\n==============================")
        print(f"Testing Scenario for: {sku}")
        print(f"==============================")
        try:
            response = agent_executor.invoke({
                "input": f"Please analyze {sku} and take necessary actions."
            })
            print("\n--- Final Output ---")
            print(response["output"])
        except Exception as e:
            print(f"\n[!] EXECUTION HALTED FOR {sku}:")
            print(f"Error Details: {e}")
            print("-> If the error mentions 'Authentication', you need to put your real OpenAI API key on line 23.")
