from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class AuthAPI(http.Controller):
    
    @http.route('/api/auth/signup', type='json', auth='public', methods=['POST'], csrf=False)
    def signup(self, name, email, password, **kwargs):
        """
        User signup endpoint
        Expected JSON payload:
        {
            "params": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "secure_password"
            }
        }
        """
        try:
            # Validate input
            if not all([name, email, password]):
                return {
                    'success': False,
                    'message': 'Name, email, and password are required'
                }
            
            # Check if user already exists
            existing_user = request.env['res.users'].sudo().search([
                ('login', '=', email)
            ], limit=1)
            
            if existing_user:
                return {
                    'success': False,
                    'message': 'User with this email already exists'
                }
            
            # Create new user
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'email': email,
                'password': password,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]
            })
            
            # Authenticate the newly created user
            # request.session.authenticate(request.db, email, password)

            # credential = {'login': email, 'password': password, 'type': 'password'}
            # uid = request.session.authenticate(request.db, credential)
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user': user,
                'session_id': request.session.sid
            }
            
        except Exception as e:
            _logger.error(f"Signup error: {str(e)}")
            print("Signup Error ")
            return {
                'success': False,
                'message': str(e)
            }
    
    
    @http.route('/api/auth/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, email, password, **kwargs):
        """
        User login endpoint
        Expected JSON payload:
        {
            "params": {
                "email": "john@example.com",
                "password": "secure_password"
            }
        }
        """
        try:
            # Validate input
            if not email or not password:
                return {
                    'success': False,
                    'message': 'Email and password are required'
                }
            
            # Authenticate user
            credential = {'login': email, 'password': password, 'type': 'password'}
            uid = request.session.authenticate(request.db, credential)
            
            if not uid:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Get user information
            user_id = request.session.uid
            user = request.env["res.users"].sudo().browse(user_id)

            if not user.exists():
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            return { 
                'success': True,
                'message': 'Login successful',
                'user': user,
                'session_id': request.session.sid
            }
            
        except Exception as e:
            _logger.error(f"Login error: {str(e)}")
            return {
                'success': False,
                'message': 'Invalid credentials or server error'
            }
    
    
    @http.route('/api/auth/logout', type='json', auth='user', methods=['POST'], csrf=False)
    def logout(self, **kwargs):
        """
        User logout endpoint
        """
        try:
            request.session.logout()
            return {
                'success': True,
                'message': 'Logout successful'
            }
        except Exception as e:
            _logger.error(f"Logout error: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    
    @http.route('/api/auth/check', type='json', auth='user', methods=['POST'], csrf=False)
    def check_session(self, **kwargs):
        """
        Check if user session is valid
        """
        try:
            user = request.env.user
            
            if user._is_public():
                return {
                    'success': False,
                    'message': 'Not authenticated'
                }
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                },
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }