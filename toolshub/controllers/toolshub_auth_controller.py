import logging
import secrets
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ToolshubAuth(http.Controller):
    
    @http.route('/toolshub/api/signup', type='json', auth='public', methods=['POST'], csrf=False)
    def signup(self, **kwargs):
        """
        Signup with email verification - creates INACTIVE user
        Expected params: name, email, password
        """
        _logger.info("HIT /toolshub/api/signup, Creating New User")
        _logger.debug(f"Request kwargs: {kwargs}")
        
        name = kwargs.get('username')
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        # Validate inputs
        if not name or not email or not password:
            _logger.error("Missing required signup parameters")
            return {
                'success': False,
                'data': {
                    'message': 'All fields are required for signup'
                }
            }
        
        try:
            # Check if email already exists (including inactive users)
            existing_user = request.env['res.users'].with_context(active_test=False).sudo().search([
                ('login', '=', email)
            ], limit=1)
            
            if existing_user:
                _logger.error(f"Email already registered: {email}")
                return {
                    'success': False,
                    'data': {
                        'message': 'This email is already registered'
                    }
                }
            
            # Generate unique activation token (never expires)
            activation_token = secrets.token_urlsafe(32)
            _logger.debug(f"Generated activation token for {email}")
            
            # Create partner
            partner = request.env['res.partner'].sudo().create({
                'name': name,
                'email': email,
                'is_company': False,
            })
            _logger.debug(f"Partner created: ID {partner.id}")
            
            # Create INACTIVE user with activation token stored
            user = request.env['res.users'].sudo().create({
                'login': email,
                'password': password,
                'partner_id': partner.id,
                'active': False,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
            })
            
            _logger.debug(f"Created inactive user: {email} (ID: {user.id})")
            _logger.info(f"User Created Successfully: {email}")
            
            # Store activation token with user ID (no expiry)
            request.env['ir.config_parameter'].sudo().set_param(
                f'activation_token_{activation_token}',
                f'{user.id}|{email}'
            )
            
            # Send activation email
            self._send_activation_email(user, activation_token)
            
            return {
                'success': True,
                'data': {
                    'message': 'Account created! Please check your email to activate your account.'
                }
            }
            
        except Exception as e:
            _logger.error(f"Signup error: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'An error occurred during signup. Please try again.',
                    'error': str(e)
                }
            }
    
    def _send_activation_email(self, user, token):
        """Send activation email with link"""
        _logger.info(f"Sending activation email to {user.login}")
        
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            activation_link = f"{base_url}/toolshub/activate?token={token}"
            
            mail_values = {
                'subject': 'Activate Your Toolshub Account',
                'email_from': request.env.company.email or 'noreply@toolshub.com',
                'email_to': user.login,
                'body_html': f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                            <h1 style="color: white; margin: 0; text-align: center;">Welcome to Toolshub!</h1>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                            <h2 style="color: #333;">Hi {user.name},</h2>
                            
                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                Thank you for signing up! You're almost ready to start renting and listing tools.
                            </p>
                            
                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                Please click the button below to activate your account:
                            </p>
                            
                            <div style="text-align: center; margin: 40px 0;">
                                <a href="{activation_link}" 
                                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                          color: white;
                                          padding: 15px 40px;
                                          text-decoration: none;
                                          border-radius: 30px;
                                          font-weight: bold;
                                          font-size: 16px;
                                          display: inline-block;
                                          box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                    Activate My Account
                                </a>
                            </div>
                            
                            <p style="color: #999; font-size: 14px;">
                                Or copy and paste this link into your browser:
                            </p>
                            <p style="color: #667eea; word-break: break-all; font-size: 14px; background: white; padding: 10px; border-radius: 5px;">
                                {activation_link}
                            </p>
                            
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                                <p style="color: #999; font-size: 13px;">
                                    💡 This activation link does not expire
                                </p>
                                <p style="color: #999; font-size: 13px;">
                                    If you didn't create this account, please ignore this email.
                                </p>
                            </div>
                            
                            <p style="color: #666; margin-top: 30px;">
                                Best regards,<br>
                                <strong>The Toolshub Team</strong>
                            </p>
                        </div>
                    </div>
                """,
            }
            
            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            
            _logger.debug(f"Activation email sent successfully to {user.login}")
            
        except Exception as e:
            _logger.error(f"Error sending activation email: {str(e)}")
    
    @http.route('/toolshub/activate', type='http', auth='public', methods=['GET'], website=True)
    def activate_account(self, token=None, **kwargs):
        """Activate user account via email link"""
        _logger.info("HIT /toolshub/activate, Activating User Account")
        _logger.debug(f"Activation token: {token}")
        
        try:
            if not token:
                _logger.error("Missing activation token")
                return request.redirect('/toolshub?token_error=missing')
            
            # Get stored token data
            token_data = request.env['ir.config_parameter'].sudo().get_param(
                f'activation_token_{token}'
            )
            
            if not token_data:
                _logger.error(f"Invalid token: {token}")
                return request.redirect('/toolshub?token_error=invalid')
            
            # Parse token data (no expiry field)
            parts = token_data.split('|')
            if len(parts) != 2:
                _logger.error(f"Malformed token data: {token}")
                return request.redirect('/toolshub?token_error=invalid')
            
            user_id, email = parts
            user_id = int(user_id)
            
            _logger.debug(f"Token data: user_id={user_id}, email={email}")
            
            # Get the user (search inactive users)
            user = request.env['res.users'].with_context(active_test=False).sudo().browse(user_id)
            
            if not user.exists():
                _logger.error(f"User not found: ID {user_id}")
                return request.redirect('/toolshub?token_error=user_not_found')
            
            if user.active:
                _logger.warning(f"User {email} already activated")
                return request.redirect('/toolshub?token_info=already')
            
            # Activate user
            user.write({'active': True})
            
            # Delete used token (one-time use)
            request.env['ir.config_parameter'].sudo().search([
                ('key', '=', f'activation_token_{token}')
            ]).unlink()
            
            _logger.info(f"User Activated Successfully: {email} (ID: {user_id})")
            
            # Redirect to login with success message
            return request.redirect('/toolshub?token_info=activated')
            
        except Exception as e:
            _logger.error(f"Activation error: {str(e)}")
            return request.redirect('/toolshub?token_error=failed')
    
    # @http.route('/toolshub/api/resendActivation', type='json', auth='public', methods=['POST'], csrf=False)
    # def resend_activation(self, **kwargs):
    #     """
    #     Resend activation email
    #     Expected params: email
    #     """
    #     _logger.info("HIT /toolshub/api/resendActivation, Resending Activation Email")
        
    #     email = kwargs.get('email')
        
    #     if not email:
    #         _logger.error("Missing email parameter")
    #         return {
    #             'success': False,
    #             'data': {
    #                 'message': 'Email parameter is required'
    #             }
    #         }
        
    #     try:
    #         # Find inactive user with this email
    #         user = request.env['res.users'].with_context(active_test=False).sudo().search([
    #             ('login', '=', email),
    #             ('active', '=', False)
    #         ], limit=1)
            
    #         if not user:
    #             _logger.error(f"No inactive account found for email: {email}")
    #             return {
    #                 'success': False,
    #                 'data': {
    #                     'message': 'No inactive account found with this email'
    #                 }
    #             }
            
    #         # Delete old token if exists
    #         old_tokens = request.env['ir.config_parameter'].sudo().search([
    #             ('key', 'like', f'activation_token_%'),
    #             ('value', 'like', f'{user.id}|{email}')
    #         ])
    #         old_tokens.unlink()
    #         _logger.debug(f"Deleted {len(old_tokens)} old token(s) for {email}")
            
    #         # Generate new token (no expiry)
    #         activation_token = secrets.token_urlsafe(32)
            
    #         _logger.debug(f"Generated new activation token for {email}")
            
    #         # Store new token
    #         request.env['ir.config_parameter'].sudo().set_param(
    #             f'activation_token_{activation_token}',
    #             f'{user.id}|{email}'
    #         )
            
    #         # Send email
    #         self._send_activation_email(user, activation_token)
            
    #         _logger.info(f"Activation Email Resent Successfully to {email}")
            
    #         return {
    #             'success': True,
    #             'data': {
    #                 'message': 'Activation email sent! Please check your inbox.'
    #             }
    #         }
            
    #     except Exception as e:
    #         _logger.error(f"Resend activation error: {str(e)}")
    #         return {
    #             'success': False,
    #             'data': {
    #                 'message': 'Failed to resend activation email',
    #                 'error': str(e)
    #             }
    #         }