# controllers/stripe_payment.py
import stripe
from odoo import http
from odoo.http import request
# import logging

# _logger = logging.getLogger(__name__)

class StripePaymentController(http.Controller):
    
    @http.route('/toolshub/process-rental-payment', type='json', auth='user', methods=['POST'])
    def process_rental_payment(self, **kwargs):
        """
        Process a rental payment with Stripe Connect
        This is the method you'll use in production (with hardcoded values for testing)
        """
        # Initialize Stripe
        stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')  # Replace with your secret key
        
        try:
            # HARDCODED TEST VALUES
            SELLER_STRIPE_ACCOUNT = 'acct_1SIuDg0JSHJqOCek'  # Replace with your connect account ID
            RENTAL_AMOUNT = 10000  # $100.00 in cents
            PLATFORM_FEE_PERCENT = 15  # Your marketplace takes 15%
            PLATFORM_FEE = int(RENTAL_AMOUNT * PLATFORM_FEE_PERCENT / 100)  # $15.00
            
            # Create Stripe Checkout Session (recommended for marketplaces)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Equipment Rental',
                            'description': 'Power Drill - 3 days rental',
                        },
                        'unit_amount': RENTAL_AMOUNT,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:8069/toolshub?status=success',
                cancel_url='http://localhost:8069/toolshub?status=cancelled',
                # success_url='http://localhost:8069/toolshub/payment-success?session_id={CHECKOUT_SESSION_ID}',
                # cancel_url='http://localhost:8069/toolshub/payment-cancelled',
                payment_intent_data={
                    'application_fee_amount': PLATFORM_FEE,
                    'transfer_data': {
                        'destination': SELLER_STRIPE_ACCOUNT,
                    },
                },
                metadata={
                    'user_id': str(request.env.user.id),
                    'user_email': request.env.user.email,
                    'rental_id': 'RENTAL_TEST_001',
                    'seller_account': SELLER_STRIPE_ACCOUNT,
                }
            )
            
            print(f"Checkout session created: {session.id}")
            print(f"Amount: ${RENTAL_AMOUNT/100}, Platform fee: ${PLATFORM_FEE/100}")
            
            return {
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id,
                'amount': RENTAL_AMOUNT,
                'platform_fee': PLATFORM_FEE,
                'seller_receives': RENTAL_AMOUNT - PLATFORM_FEE,
            }
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/toolshub/payment-success', type='http', auth='public', website=True)
    def payment_success(self, **kwargs):
        """Handle successful payment return"""
        session_id = kwargs.get('session_id')
        if session_id:
            # Verify the payment was successful
            stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')  # Replace with your secret key
            session = stripe.checkout.Session.retrieve(session_id)
            print(f"Payment successful! Session: {session_id}, Status: {session.payment_status}")
        
        return "<h1>Payment Successful!</h1><p>Rental confirmed.</p><a href='/'>Go Home</a>"
    
    @http.route('/toolshub/payment-cancelled', type='http', auth='public', website=True)
    def payment_cancelled(self, **kwargs):
        """Handle cancelled payment"""
        return "<h1>Payment Cancelled</h1><p>Rental was not completed.</p><a href='/'>Go Home</a>"