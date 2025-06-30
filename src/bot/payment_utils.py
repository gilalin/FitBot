import os
import requests
from typing import Dict, Any, Optional

PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://payment:8000')

def create_payment(
    amount: float,
    currency: str = 'USD',
    description: str = '',
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a payment through the payment service.
    
    Args:
        amount: Amount to charge (in the smallest currency unit, e.g., cents)
        currency: Three-letter currency code (default: USD)
        description: Description of the payment
        metadata: Additional metadata to attach to the payment
    
    Returns:
        Dict containing payment information including the payment URL
    
    Raises:
        requests.exceptions.RequestException: If the payment service request fails
    """
    try:
        response = requests.post(
            f"{PAYMENT_SERVICE_URL}/pay",
            json={
                "amount": amount,
                "currency": currency,
                "description": description,
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Payment service error: {str(e)}")
        raise

def get_payment_status(payment_id: str) -> Dict[str, Any]:
    """
    Get the status of a payment.
    
    Args:
        payment_id: The ID of the payment to check
    
    Returns:
        Dict containing payment status information
    
    Raises:
        requests.exceptions.RequestException: If the payment service request fails
    """
    try:
        response = requests.get(f"{PAYMENT_SERVICE_URL}/payment/{payment_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Payment service error: {str(e)}")
        raise 