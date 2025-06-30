import os
import stripe
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

app = Flask(__name__)

class PaymentService:
    def __init__(self):
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    def create_customer(self, email, name=None, metadata=None):
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except stripe.error.StripeError as e:
            print(f"Error creating customer: {str(e)}")
            raise

    def create_subscription(self, customer_id, price_id, metadata=None):
        """Create a subscription for a customer."""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {}
            )
            return subscription
        except stripe.error.StripeError as e:
            print(f"Error creating subscription: {str(e)}")
            raise

    def create_payment_intent(self, amount_cents, currency='usd', customer_id=None, metadata=None):
        """Create a payment intent for a one-time payment."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {}
            )
            return intent
        except stripe.error.StripeError as e:
            print(f"Error creating payment intent: {str(e)}")
            raise

    def create_membership_price(self, amount_cents, interval='month', name=None, metadata=None):
        """Create a recurring price for memberships."""
        try:
            # First create a product
            product = stripe.Product.create(
                name=name or f"Membership - {interval}ly",
                metadata=metadata or {}
            )

            # Then create a price for the product
            price = stripe.Price.create(
                product=product.id,
                unit_amount=amount_cents,
                currency='usd',
                recurring={
                    'interval': interval,
                    'interval_count': 1
                },
                metadata=metadata or {}
            )
            return price
        except stripe.error.StripeError as e:
            print(f"Error creating price: {str(e)}")
            raise

    def create_product_price(self, amount_cents, name, description=None, metadata=None):
        """Create a one-time price for products."""
        try:
            # Create a product
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )

            # Create a one-time price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=amount_cents,
                currency='usd',
                metadata=metadata or {}
            )
            return price
        except stripe.error.StripeError as e:
            print(f"Error creating product price: {str(e)}")
            raise

    def cancel_subscription(self, subscription_id):
        """Cancel a subscription."""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            print(f"Error canceling subscription: {str(e)}")
            raise

    def handle_webhook(self, payload, sig_header):
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )

            # Handle specific events
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                # Handle successful payment
                print(f"Payment succeeded: {payment_intent.id}")
            elif event.type == 'customer.subscription.created':
                subscription = event.data.object
                # Handle new subscription
                print(f"Subscription created: {subscription.id}")
            elif event.type == 'customer.subscription.deleted':
                subscription = event.data.object
                # Handle cancelled subscription
                print(f"Subscription cancelled: {subscription.id}")

            return event

        except ValueError as e:
            print(f"Invalid payload: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid signature: {str(e)}")
            raise

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    # Here you would handle payment logic, e.g., call Stripe
    # For now, just echo the request
    return jsonify({"status": "success", "received": data}), 200

# Example usage
if __name__ == '__main__':
    payment_service = PaymentService()

    # Example: Create a customer
    try:
        customer = payment_service.create_customer(
            email="test@example.com",
            name="Test User",
            metadata={"user_id": "123"}
        )
        print(f"Created customer: {customer.id}")

        # Example: Create a membership price
        price = payment_service.create_membership_price(
            amount_cents=9900,  # $99.00
            interval='month',
            name="Monthly Membership",
            metadata={"type": "membership"}
        )
        print(f"Created price: {price.id}")

        # Example: Create a subscription
        subscription = payment_service.create_subscription(
            customer_id=customer.id,
            price_id=price.id,
            metadata={"membership_id": "456"}
        )
        print(f"Created subscription: {subscription.id}")

    except stripe.error.StripeError as e:
        print(f"Error in example: {str(e)}")

    app.run(host='0.0.0.0', port=8000) 