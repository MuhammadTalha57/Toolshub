from odoo import http
from odoo.http import request
import stripe
from stripe._error import SignatureVerificationError  # ✅ ADD THIS LINE
import json
import logging

_logger = logging.getLogger(__name__)


class StripeWebhook(http.Controller):

    def _get_stripe_keys(self):
        """Get Stripe keys from Odoo system parameters"""
        IrConfigParam = request.env['ir.config_parameter'].sudo()
        return {
            'secret_key': IrConfigParam.get_param('stripe.secret_key', ''),
            'webhook_secret': IrConfigParam.get_param('stripe.webhook_secret', '')
        }
    
    @http.route('/stripe/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def stripe_webhook(self):
        """
        Handle Stripe webhook events
        """
        keys = self._get_stripe_keys()
        
        # Set Stripe API key
        stripe.api_key = keys['secret_key']
        
        payload = request.httprequest.data
        sig_header = request.httprequest.headers.get('Stripe-Signature')
        
        print("="*50)
        print("📨 Received Stripe Webhook")
        print("="*50)
        
        # Debug logging
        print(f"Webhook secret exists: {bool(keys['webhook_secret'])}")
        print(f"Signature header exists: {bool(sig_header)}")
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, keys['webhook_secret']
            )
            
            print(f"✅ Event Type: {event['type']}")
            print(f"📦 Event ID: {event['id']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                print(f"💰 Checkout completed: {session['id']}")
                print(f"Amount: {session['amount_total']/100} {session['currency']}")
                self._handle_checkout_completed(session)
                
            elif event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                print(f"💳 Payment succeeded: {payment_intent['id']}")
                print(f"Amount: {payment_intent['amount']/100} {payment_intent['currency']}")
                self._handle_payment_success(payment_intent)
                
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                print(f"❌ Payment failed: {payment_intent['id']}")
                self._handle_payment_failed(payment_intent)
                
            elif event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                print(f"🔔 Subscription created: {subscription['id']}")
                self._handle_subscription_created(subscription)
                
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                print(f"🔕 Subscription cancelled: {subscription['id']}")
                self._handle_subscription_deleted(subscription)
                
            else:
                print(f"ℹ️ Unhandled event type: {event['type']}")
            
            print("="*50)
            
            return request.make_response(
                json.dumps({'status': 'success'}), 
                headers=[('Content-Type', 'application/json')]
            )
            
        except ValueError as e:
            # Invalid payload
            print(f"❌ Invalid payload: {str(e)}")
            return request.make_response(
                json.dumps({'error': 'Invalid payload'}), 
                status=400
            )
            
        except SignatureVerificationError as e:  # ✅ CHANGED THIS LINE
            # Invalid signature
            print(f"❌ Invalid signature: {str(e)}")
            print(f"Webhook secret configured: {bool(keys['webhook_secret'])}")
            print(f"Webhook secret value (first 10): {keys['webhook_secret'][:10] if keys['webhook_secret'] else 'EMPTY'}")
            return request.make_response(
                json.dumps({'error': 'Invalid signature'}), 
                status=400
            )
            
        except Exception as e:
            print(f"❌ Webhook error: {str(e)}", exc_info=True)
            return request.make_response(
                json.dumps({'error': str(e)}), 
                status=500
            )
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout"""
        print(f"Processing checkout: {session}")
        # Your business logic here
        
    def _handle_payment_success(self, payment_intent):
        """Handle successful payment"""
        print(f"Processing payment: {payment_intent}")
        # Your business logic here
        
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment"""
        print(f"Payment failed: {payment_intent}")
        # Your business logic here
        
    def _handle_subscription_created(self, subscription):
        """Handle new subscription"""
        print(f"Processing subscription: {subscription}")
        # Your business logic here
        
    def _handle_subscription_deleted(self, subscription):
        """Handle cancelled subscription"""
        print(f"Subscription cancelled: {subscription}")
        # Your business logic here