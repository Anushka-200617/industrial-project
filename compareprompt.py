
import asyncio
import streamlit as st
import os
import json
import re
import pandas as pd
from dotenv import load_dotenv

from fastmcp import Client
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

def run_async_task(coro):
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

async def run_comparison():
    # connect to FastMCP server
    async with Client("compareserver.py") as client:

        # call MCP tools
        nike_data = await client.call_tool(
            "get_brand_data",
            {"brand_name": "nike"}
        )

        puma_data = await client.call_tool(
            "get_brand_data",
            {"brand_name": "puma"}
        )

        # build context
        context = f"Nike Data: {nike_data}\nPuma Data: {puma_data}"

        # structured prompt
        final_prompt = f"""
Based on this real-time data:
{context}

Create a comparison table.

Return ONLY valid JSON list with fields:
brand, product, price, rating

Limit to maximum 10 rows.
Example:
[
  {{"brand":"Nike","product":"...","price":100,"rating":4.5}}
]
"""

        print("--- Context Provided to AI ---")
        print(final_prompt)

        # LLM setup
        llm = ChatHuggingFace(
            llm=HuggingFaceEndpoint(
                repo_id="openai/gpt-oss-120b",
                max_new_tokens=1024,
                temperature=0.2,
                do_sample=False,
                timeout=120,
                huggingfacehub_api_token=HF_TOKEN
            )
        )

        response = llm.invoke(final_prompt)

        # print("\n--- AI RESPONSE ---")
        # print(response.content)

        # extract JSON safely
        try:
            json_text = re.search(r"\[.*\]", response.content, re.S).group()
            data = json.loads(json_text)
        except Exception:
            data = json.loads(response.content)

        # convert to dataframe
        df = pd.DataFrame(data)

        print("\n--- DATAFRAME ---")
        # print(df)

        return df

# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Brand Comparison", layout="wide")

st.title("👟 Nike vs Puma Comparison")

st.write("Click the button below to fetch and compare products")

# Button
if st.button("🔍 Compare Brands"):

    with st.spinner("Fetching data..."):
        df = run_async_task(run_comparison())

    st.success("✅ Comparison Ready!")

    # Show DataFrame
    st.dataframe(df, use_container_width=True)

# if __name__ == "__main__":
#     asyncio.run(run_comparison())


# second typr UI
# ---------------- UI ---------------- #

# st.set_page_config(page_title="Brand Comparison AI", layout="wide")

# st.title(" Brand Comparison AI (Nike vs Puma)")

# st.write("Select or enter product type")

# # Dropdown
# product_option = st.selectbox(
#     "Choose Product",
#     ["shoes", "t-shirts", "hoodies", "jackets", "sports shoes"]
# )

# # Custom input
# custom_product = st.text_input("Or type your own product")

# product = custom_product if custom_product else product_option

# # Button
# if st.button(" Compare Brands"):

#     with st.spinner(f"Fetching {product} data..."):

#         nike_data = get_brand_data("nike", product)
#         puma_data = get_brand_data("puma", product)

#         df = generate_comparison(nike_data, puma_data)

#     if not df.empty:
#         st.success(" Comparison Ready!")

#         st.subheader("Comparison Table")
#         st.dataframe(df, use_container_width=True)

#         # Chart
#         st.subheader("Price Comparison")
#         st.bar_chart(df.set_index("product")["price"])

#     else:
#         st.error("No data found. Try another product.")
