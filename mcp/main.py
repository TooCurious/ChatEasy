from fastmcp import FastMCP
from schemas import OrderRequest, OrderResponse
from fake_db import ORDERS

mcp = FastMCP("Personal Information Detection", host="0.0.0.0", port=5005)

@mcp.tool()
def get_order_status_tool(order_id: OrderRequest) -> OrderResponse:

    """
    Retrieves the current status and estimated delivery time for a specific order.

    This tool is designed to answer user queries about order progress, such as:
    - "What is the status of my order ORD-123?"
    - "When will my package arrive?"

    The function searches a predefined list of orders (`ORDERS`) for a match by `order_id`.
    If found, it returns a structured response containing the order ID, current status
    (e.g., 'processing', 'shipped', 'delivered'), and the estimated time of arrival in days.

    Parameters:
        order_id (OrderRequest): A validated input object containing the unique identifier
                                 of the order (e.g., a string like "ORD-7890").

    Returns:
        OrderResponse: A structured object with the following fields:
            - order_id: the same ID that was queried,
            - status: current state of the order (string),
            - eta_days: estimated number of days until delivery (int or float).

    Raises:
        ValueError: If no order with the given `order_id` exists in the system.
                    The error message includes the missing ID for debugging.

    Example (as used by an AI agent):
        Input: order_id = "ORD-5521"
        Output: OrderResponse(order_id="ORD-5521", status="shipped", eta_days=3)

    Note:
        This tool assumes that:
        - All order IDs are unique.
        - The `ORDERS` list is pre-populated and accessible in the current scope.
        - `OrderRequest` and `OrderResponse` are Pydantic models or similar data containers
          that support field access and serialization.
    """
    
    order = next((o for o in ORDERS if o["order_id"] == order_id), None)
    if order:
        return OrderResponse(
            order_id=order["order_id"],
            status=order["status"],
            eta_days=order["eta_days"]
        )
    else:
        raise ValueError(f"Order with ID {order_id} not found.")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")