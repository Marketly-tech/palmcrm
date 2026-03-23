"""
Customers module for RRL CRM.
"""
from customers.routes import router, generate_customer_id
from customers.models import Customer, CustomerBase, CustomerCreate, DocumentChecklist, GoogleFormWebhook

__all__ = [
    "router",
    "generate_customer_id",
    "Customer",
    "CustomerBase",
    "CustomerCreate",
    "DocumentChecklist",
    "GoogleFormWebhook",
]
