import requests
from fastmcp import FastMCP

from serpapi import GoogleSearch

mcp = FastMCP("Brand Comprison server")

@mcp.tool()
def get_brand_data(brand_name: str, product_type: str = "shoes"):
    
    """
    fetches real time shopping for a specific brand and product
    """
    params = {
        "engine" : "google_shopping",
        "q" : f"{brand_name} {product_type}",
        "api_key" :"",   # write your api here
        "num" :3   
    }

    search = GoogleSearch(params)
    results = search.get_dict().get("shopping_results", [])

    return[
        {"title": r.get("title"), "price": r.get("price"), "rating": r.get("rating")}
        for r in results
    ]

if __name__ == "__main__":
    mcp.run()
