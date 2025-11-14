import logging

import stripe
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class StripePaymentController(http.Controller):
    
    @http.route('/toolshub/processRentPayment', type='json', auth='user', methods=['POST'])
    def process_rent_payment(self, **kwargs ):
        """
        Process a rental payment with Stripe Connect
        """
        _logger.info("HIT /toolshub/processRentPayment, Processing Rent Payment")
        _logger.debug(f"Request kwargs: {kwargs}")
        
        listing = kwargs.get('listing')
        _logger.debug(f"Got Listing {listing}")

        if not listing:
            _logger.error("No Rent Listing Selected")
            return {
                'success': False,
                'data': {
                    'message': 'No Rent Listing Selected',
                    'error': '/processRentPayment called without providing listing'
                }
            }

        # Initialize Stripe
        stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')
        
        _logger.debug("Creating Checkout Session")
        try:
            SELLER_STRIPE_ACCOUNT = listing['owner_connect_account_id']
            RENTAL_AMOUNT = listing['price'] * 100
            PLATFORM_FEE_PERCENT = 5  # Platform takes 5%
            PLATFORM_FEE = int(RENTAL_AMOUNT * PLATFORM_FEE_PERCENT / 100)
            
            _logger.info(f"Seller Account: {SELLER_STRIPE_ACCOUNT}, Amount: {RENTAL_AMOUNT}, Platform Fee: {PLATFORM_FEE}")
            
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
                success_url= request.httprequest.host_url + 'toolshub?paymentStatus=success',
                cancel_url= request.httprequest.host_url + 'toolshub?paymentStatus=cancelled',
                payment_intent_data={
                    'application_fee_amount': PLATFORM_FEE,
                    'transfer_data': {
                        'destination': SELLER_STRIPE_ACCOUNT,
                    },
                },
                metadata={
                    'tool_name': listing['tool_name'],
                    'plan_name': listing['plan_name'],
                    'user_id': str(request.env.user.id),
                    'user_email': request.env.user.email,
                    'seller_account': SELLER_STRIPE_ACCOUNT,
                }
            )

            _logger.info("Checkout Session Created Successfully")
            _logger.debug(f"Session ID: {session.id}")
            
            return {
                'success': True,
                'data': {
                    'checkout_url': session.url,
                    'session_id': session.id,
                }
            }
            
        except stripe._error.StripeError as e:
            _logger.error(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': "Stripe Error Occured",
                    'error': str(e)
                }
            }
        except Exception as e:
            _logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': "An Error Occured",
                    'error': str(e)
                }
            }
    
    @http.route('/toolshub/validateConnectAccount', type='json', auth='user', methods=['POST'])
    def validate_connect_account(self, **kwargs):
        _logger.info("HIT /toolshub/validateConnectAccount, Validating Connect Account")
        
        connect_id = kwargs.get("connect_id")
        _logger.debug(f"Connect ID: {connect_id}")
        
        if not connect_id:
            _logger.error("No Connect Account ID Provided")
            return {
                "success": False,
                "data": {
                    'message': "No Connect Account ID Provided",
                }
            }

        try:
            # Initialize Stripe
            stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')

            _logger.debug(f"Retrieving Stripe Account: {connect_id}")
            stripe.Account.retrieve(connect_id)

            user = request.env.user
            _logger.debug(f"Updating user {user.id} with Connect Account ID")
            user.write({
                "stripe_connect_account_id": connect_id
            })

            _logger.info("Connect Account Validated and Added Successfully")
            return {
                "success": True, 
                "data": {
                    "message": "Account Added Successfully"
                }
            }
        
        except stripe._error.StripeError as e:
            _logger.error(f"Stripe error: {str(e)}")
            return {
                "success": False, 
                "data": {
                    'message': "Stripe Connect account not found",
                    'error': str(e)
                }
            }
        except Exception as e:
            _logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False, 
                "data": {
                    'message': "An Error Occured",
                    'error': str(e)
                }
            }

    @http.route('/toolshub/createConnectAccount', type='json', auth='user', methods=['POST'], csrf=False)
    def create_stripe_connect_account(self, **kwargs):
        """Create Stripe Connect account and redirect user to onboarding"""
        _logger.info("HIT /toolshub/createConnectAccount, Creating Stripe Connect Account")
        
        try:
            # Set your Stripe API key
            stripe.api_key = request.env['ir.config_parameter'].sudo().get_param('stripe_api_key', '')
            
            current_user = request.env.user
            _logger.debug(f"Current user: {current_user.id} - {current_user.email}")
            
            # Check if user already has an account
            if current_user.stripe_connect_account_id:
                account_id = current_user.stripe_connect_account_id
                _logger.debug(f"User already has Connect Account: {account_id}")
            else:
                _logger.debug("Creating new Stripe Connect Account")
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
                _logger.debug(f"Created Connect Account: {account_id}")
                
                # Save account ID to user
                current_user.sudo().write({
                    'stripe_connect_account_id': account_id
                })
                _logger.debug(f"Saved Connect Account ID to user {current_user.id}")
            
            # Generate onboarding link
            _logger.debug(f"Generating onboarding link for account: {account_id}")
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=request.httprequest.host_url + 'toolshub',
                return_url=request.httprequest.host_url + 'toolshub?connectAccountStatus=success',
                type='account_onboarding',
            )
            
            _logger.info("Stripe Connect Account Created and Onboarding Link Generated Successfully")
            _logger.debug(f"Onboarding URL: {account_link.url}")
            
            # Return onboarding link to frontend
            return {
                'success': True,
                'data': {
                    'account_link': account_link.url,
                }
            }
            
        except stripe._error.StripeError as e:
            _logger.error(f"Stripe Connect Error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'Stripe Error Occurred',
                    'error': str(e)
                }
            }
        except Exception as e:
            _logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'An Error Occurred',
                    'error': str(e)
                }
            }
        
    


