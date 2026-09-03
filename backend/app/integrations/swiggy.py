import os, httpx
class SwiggyMCP:
    """Authorized Swiggy MCP adapter. Credentials are supplied by the approved integration owner."""
    def __init__(self):
        self.url=os.getenv("SWIGGY_MCP_URL","https://mcp.swiggy.com/food")
        self.token=os.getenv("SWIGGY_ACCESS_TOKEN")
    async def search_restaurants(self,address_id:str,query:str):
        if not self.token: return {"connected":False,"message":"Add SWIGGY_ACCESS_TOKEN after completing authorized OAuth."}
        # Swiggy MCP uses authenticated tool calls; keep this adapter isolated so the app
        # can be wired to the approved MCP client without hard-coding private endpoints.
        return {"connected":True,"message":"Adapter configured; connect your MCP client/tool call here.","query":query}
