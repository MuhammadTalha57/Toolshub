# controllers/stripe_payment.py
import stripe
from odoo import http
from odoo.http import request
# import logging

# _logger = logging.getLogger(__name__)

class StripePaymentController(http.Controller):
    
    @http.route('/toolshub/processRentPayment', type='json', auth='user', methods=['POST'])
    def process_rent_payment(self, **kwargs ):
        """
        Process a rental payment with Stripe Connect
        """
        print("CONTROLLER", kwargs)
        listing = kwargs.get('listing')
        print(f"Got Listing {listing}")

        if not listing:
            print("NO LISTING")
            return {
                'success': False,
                'data': {
                    'message': 'No Rent Listing Selected',
                    'error': '/processRentPayment called without providing listing'
                }
            }

        # Initialize Stripe
        stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')
        
        print("Creating Checkout Session")
        try:
            # HARDCODED TEST VALUES
            SELLER_STRIPE_ACCOUNT = 'acct_1SIuDg0JSHJqOCek'
            RENTAL_AMOUNT = listing['price']
            PLATFORM_FEE_PERCENT = 5  # Platform takes 5%
            PLATFORM_FEE = int(RENTAL_AMOUNT * PLATFORM_FEE_PERCENT / 100)
            
            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Tool Rental',
                            'description': f"{listing['tool_name']} - {listing['plan_name']}",
                        },
                        'unit_amount': RENTAL_AMOUNT,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:8069/toolshub?paymentStatus=success',
                cancel_url='http://localhost:8069/toolshub?paymentStatus=cancelled',
                payment_intent_data={
                    'application_fee_amount': PLATFORM_FEE,
                    'transfer_data': {
                        'destination': SELLER_STRIPE_ACCOUNT,
                    },
                },
                metadata={
                    'tool_name': listing['tool_name'],
                    'tool_name': listing['plan_name'],
                    'user_id': str(request.env.user.id),
                    'user_email': request.env.user.email,
                    'seller_account': SELLER_STRIPE_ACCOUNT,
                }
            )

            print("Created Checkout Session")
            
            return {
                'success': True,
                'data': {
                    'checkout_url': session.url,
                    'session_id': session.id,
                }
            }
            
        except stripe._error.StripeError as e:
            print(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': "Stripe Error Occured",
                    'error': str(e)
                }
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': "Unexpected Error Occured",
                    'error': str(e)
                }
            }
    
    @http.route('/toolshub/validateConnectAccount', type='json', auth='user', methods=['POST'])
    def validate_connect_account(self, **kwargs):
        connect_id = kwargs.get("connect_id")
        if not connect_id:
            return {
                "success": False,
                "data": {
                    'message': "No Connect Account ID Provided",
                }
            }

        try:
            # Initialize Stripe
            stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')

            stripe.Account.retrieve(connect_id)

            user = request.env.user  # current user
            user.write({
                "stripe_connect_account_id": connect_id
            })

            return {
                "success": True, 
                "data": {
                    "message": "Account Added Successfully"
                }
                }
        
        except stripe._error.StripeError as e:
            return {
                "success": False, 
                "data": {
                    'message': "Stripe Connect account not found",
                    'error': ''
                }
            }
        except Exception as e:
            return {
                "success": False, 
                "data": {
                    'message': "Unexpected Error Occured",
                    'error': str(e)
                }
            }

    @http.route('/toolshub/createConnectAccount', type='json', auth='user', methods=['POST'], csrf=False)
    def create_stripe_connect_account(self, **kwargs):
        """Create Stripe Connect account and redirect user to onboarding"""
        try:
            # Set your Stripe API key
            stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')
            
            current_user = request.env.user
            
            # Check if user already has an account
            if current_user.stripe_connect_account_id:
                account_id = current_user.stripe_connect_account_id
            else:
                # Create a new Connected Account
                account = stripe.Account.create(
                    type='express',
                    country='US',
                    email=current_user.email,
                    capabilities={
                        'card_payments': {'requested': True},
                        'transfers': {'requested': True},
                    }
                )
                account_id = account.id
                
                # Save account ID to user
                current_user.sudo().write({
                    'stripe_connect_account_id': account_id
                })
            
            # Generate onboarding link
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=request.httprequest.host_url + 'toolshub',
                return_url=request.httprequest.host_url + 'toolshub?connectAccountStatus=success',
                type='account_onboarding',
            )
            
            # Return onboarding link to frontend
            return {
                'success': True,
                'data': {
                    'account_link': account_link.url,
                }
            }
            
        except Exception as e:
            print(f"Stripe Connect Error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'An Error Occured',
                    'error': str(e)
                }
            }
