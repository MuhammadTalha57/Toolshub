import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ToolshubAPI(http.Controller):
    @http.route(['/toolshub/api/getRentListings'], type='json', auth='user', methods=['POST'])
    def get_rent_listings(self, filters=None, limit=None, offset=0):
        """
        Get rent listings with optional filters
        """
        _logger.info("HIT /toolshub/api/getRentListing, Getting Rent Listings")
        try:
            domain = []
            
            # Apply filters if provided
            if filters:
                if filters.get('tool_id'):
                    domain.append(('tool_id', '=', int(filters['tool_id'])))
                if filters.get('owner_id'):
                    domain.append(('owner_id', '=', int(filters['owner_id'])))
                if filters.get('plan_id'):
                    domain.append(('plan_id', '=', int(filters['plan_id'])))
                if filters.get('min_price'):
                    domain.append(('price', '>=', float(filters['min_price'])))
                if filters.get('max_price'):
                    domain.append(('price', '<=', float(filters['max_price'])))
                if filters.get('unlimited_users') is not None:
                    domain.append(('unlimited_users', '=', filters['unlimited_users']))
            
            # Query listings
            RentListing = request.env['toolshub.tool.rent.listings'].sudo()
            
            # Get total count
            total_count = RentListing.search_count(domain)
            
            # Get listings with pagination
            listings = RentListing.search(domain, limit=limit, offset=offset, order='id desc')
            
            _logger.debug(f"Total Count of Rent Listings {total_count}")
            _logger.debug(f"Rent Listings {listings}")
            
            # Format data
            listings_data = []
            for listing in listings:
                listings_data.append({
                    'id': listing.id,
                    'tool_id': listing.tool_id.id if listing.tool_id else None,
                    'tool_name': listing.tool_id.name if listing.tool_id else '',
                    'tool_img': listing.tool_id.icon,
                    'plan_id': listing.plan_id.id if listing.plan_id else None,
                    'plan_name': listing.plan_id.name if listing.plan_id else '',
                    'unlimited_access': listing.plan_id.is_unlimited,
                    'duration_years': listing.plan_id.duration_years,
                    'duration_months': listing.plan_id.duration_months,
                    'duration_days': listing.plan_id.duration_days,
                    'price': listing.price,
                    'currency_symbol': listing.currency_id.symbol if listing.currency_id else '$',
                    'subscribers_count': listing.subscribers_count,
                    'unlimited_users': listing.unlimited_users,
                    'available_users': listing.available_users if not listing.unlimited_users else None,
                    'owner_id': listing.owner_id.id if listing.owner_id else None,
                    'owner_name': listing.owner_id.name if listing.owner_id else '',
                    'owner_connect_account_id': listing.owner_id.stripe_connect_account_id
                })
            
            return {
                'success': True,
                "data": {
                    'listings': listings_data,
                }
            }
            
        except Exception as e:
            _logger.error(str(e))
            return {
                'success': False,
                'data': {
                    'message': "Failed to get Rent Listings",
                    'error': str(e)
                }
            }

    @http.route(['/toolshub/api/getTools'], type='json', auth='user', methods=['POST'])
    def get_tools(self, filters=None, limit=None, offset=0):
        """
        Get tools with optional filters
        """
        _logger.info("HIT /toolshub/api/getTools, Getting Tools")
        try:
            domain = []
            
            # Apply filters if provided
            if filters:
                # Filter by name (exact match)
                if filters.get('name'):
                    domain.append(('name', '=', filters['name']))
                
                # Filter by URL (exact match)
                if filters.get('url'):
                    domain.append(('url', '=', filters['url']))
                
                # Search filter (searches in name and url)
                if filters.get('search'):
                    search_term = filters['search']
                    domain.append('|')
                    domain.append(('name', 'ilike', search_term))
                    domain.append(('url', 'ilike', search_term))
                
                # Filter by IDs (useful for getting specific tools)
                if filters.get('ids'):
                    tool_ids = filters['ids']
                    if isinstance(tool_ids, list):
                        domain.append(('id', 'in', tool_ids))
                    else:
                        domain.append(('id', '=', int(tool_ids)))
            
            # Query tools
            Tool = request.env['toolshub.tools'].sudo()
            
            # Get total count
            total_count = Tool.search_count(domain)
            
            # Get tools with pagination
            tools = Tool.search(domain, limit=limit, offset=offset, order='name asc')
            
            _logger.debug(f"Total Count of Tools {total_count}")
            _logger.debug(f"Tools {tools}")
            
            # Format data
            tools_data = []
            for tool in tools:
                 # Serialize plan_ids properly
                plans_data = []
                for plan in tool.plan_ids:
                    plans_data.append({
                        'id': plan.id,
                        'name': plan.name,
                        'price': plan.price,
                        'total_users': plan.total_users,
                        'unlimited_users': plan.unlimited_users,
                        'currency_symbol': plan.currency_id.symbol if plan.currency_id else '$',
                        'duration_years': plan.duration_years,
                        'duration_months': plan.duration_months,
                        'duration_days': plan.duration_days,
                        'is_unlimited': plan.is_unlimited,
                    })
                
                tools_data.append({
                    'id': tool.id,
                    'name': tool.name,
                    'icon': tool.icon,  # Base64 encoded image
                    'url': tool.url,
                    'plan_ids': plans_data,  # Now it's a proper list of dicts
                    'plans_count': len(plans_data)
                })
            
            return {
                'success': True,
                'data': {
                    'tools': tools_data,
                }
            }
            
        except Exception as e:
            _logger.error(str(e))
            return {
                'success': False,
                'data': {
                    'message': "Failed to get Tools",
                    'error': str(e)
                }
            }

    @http.route(['/toolshub/api/getPlans'], type='json', auth='user', methods=['POST'])
    def get_plans(self, filters=None, limit=None, offset=0):
        """
        Get tool plans with optional filters
        
        :param filters: dict of filters (e.g., {'tool_id': 1, 'search': 'premium', 'unlimited_users': True})
        :param limit: int, limit number of results
        :param offset: int, offset for pagination
        :return: dict with plans data
        """
        print("Getting Plans")
        try:
            domain = []
            
            # Apply filters if provided
            if filters:
                # Filter by tool_id (most common filter)
                if filters.get('tool_id'):
                    domain.append(('tool_id', '=', int(filters['tool_id'])))
                
                # Filter by name (exact match)
                if filters.get('name'):
                    domain.append(('name', '=', filters['name']))
                
                # Search filter (searches in name)
                if filters.get('search'):
                    search_term = filters['search']
                    domain.append(('name', 'ilike', search_term))
                
                # Filter by unlimited users
                if filters.get('unlimited_users') is not None:
                    domain.append(('unlimited_users', '=', filters['unlimited_users']))
                
                # Filter by unlimited access
                if filters.get('is_unlimited') is not None:
                    domain.append(('is_unlimited', '=', filters['is_unlimited']))
                
                # Filter by price range
                if filters.get('min_price'):
                    domain.append(('price', '>=', float(filters['min_price'])))
                if filters.get('max_price'):
                    domain.append(('price', '<=', float(filters['max_price'])))
                
                # Filter by total users range
                if filters.get('min_users'):
                    domain.append(('total_users', '>=', int(filters['min_users'])))
                if filters.get('max_users'):
                    domain.append(('total_users', '<=', int(filters['max_users'])))
                
                # Filter by IDs (useful for getting specific plans)
                if filters.get('ids'):
                    plan_ids = filters['ids']
                    if isinstance(plan_ids, list):
                        domain.append(('id', 'in', plan_ids))
                    else:
                        domain.append(('id', '=', int(plan_ids)))
            
            # Query plans
            Plan = request.env['toolshub.tool.plans'].sudo()
            
            # Get total count
            total_count = Plan.search_count(domain)
            
            # Get plans with pagination
            plans = Plan.search(domain, limit=limit, offset=offset, order='tool_id asc, price asc')
            
            print(f"Found {total_count} plans, returning {len(plans)}")
            
            # Format data
            plans_data = []
            for plan in plans:
                # Get features for this plan
                features = []
                for feature in plan.feature_ids:
                    features.append({
                        'id': feature.id,
                        'name': feature.name if hasattr(feature, 'name') else '',
                        # Add other feature fields as needed
                    })
                
                plans_data.append({
                    'id': plan.id,
                    'name': plan.name,
                    'tool_id': plan.tool_id.id if plan.tool_id else None,
                    'tool_name': plan.tool_id.name if plan.tool_id else '',
                    'tool_icon': plan.tool_id.icon if plan.tool_id else None,
                    'total_users': plan.total_users,
                    'unlimited_users': plan.unlimited_users,
                    'price': plan.price,
                    'currency_id': plan.currency_id.id if plan.currency_id else None,
                    'currency_symbol': plan.currency_id.symbol if plan.currency_id else '$',
                    'currency_name': plan.currency_id.name if plan.currency_id else 'USD',
                    'duration_years': plan.duration_years,
                    'duration_months': plan.duration_months,
                    'duration_days': plan.duration_days,
                    'is_unlimited': plan.is_unlimited,
                    'features': features,
                    'features_count': len(features)
                })
            
            return {
                'success': True,
                'data': plans_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            print(f"Error getting plans: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to fetch plans'
            }

    @http.route('/toolshub/api/createRentListing', type='json', auth='user', methods=['POST'])
    def create_rent_listing(self, **kwargs):
        """
        Create a new rental listing
        Expected params: tool_id, plan_id, unlimited_users, total_users, price
        """
        # Validate required fields
        required_fields = ['tool_id', 'plan_id', 'price', 'unlimited_users', 'total_users']
        missing_fields = [field for field in required_fields if field not in kwargs]
        
        if missing_fields:
            return {
                'success': False,
                'error': 'missing_fields',
                'message': f"Missing required fields: {', '.join(missing_fields)}",
                'missing_fields': missing_fields
            }
        
        # Validate data types and values
        try:
            tool_id = int(kwargs.get('tool_id'))
            plan_id = int(kwargs.get('plan_id'))
            price = float(kwargs.get('price'))
            unlimited_users = kwargs.get('unlimited_users', False)
            total_users = int(kwargs.get('total_users'))
            
            # Convert string 'true'/'false' to boolean if needed
            if isinstance(unlimited_users, str):
                unlimited_users = unlimited_users.lower() == 'true'
            
            # Only validate total_users if not unlimited
            if not unlimited_users:
                if total_users is None:
                    return {
                        'success': False,
                        'error': 'validation_error',
                        'message': 'total_users is required when unlimited_users is False'
                    }
                if total_users <= 0:
                    return {
                        'success': False,
                        'error': 'validation_error',
                        'message': 'total_users must be greater than 0'
                    }
            else:
                total_users = 0
                
        except (ValueError, TypeError) as e:
            return {
                'success': False,
                'error': 'validation_error',
                'message': f'Invalid data format: {str(e)}'
            }
        
        # Check if tool exists
        tool = request.env['toolshub.tools'].browse(tool_id)
        if not tool.exists():
            return {
                'success': False,
                'error': 'not_found',
                'message': f'Tool with ID {tool_id} not found'
            }
        
        # Check if plan exists and belongs to the tool
        plan = request.env['toolshub.tool.plans'].browse(plan_id)
        if not plan.exists():
            return {
                'success': False,
                'error': 'not_found',
                'message': f'Plan with ID {plan_id} not found'
            }
        
        if plan.tool_id.id != tool_id:
            return {
                'success': False,
                'error': 'validation_error',
                'message': 'Selected plan does not belong to the selected tool'
            }
        
        # Prepare values for creation
        vals = {
            'tool_id': tool_id,
            'plan_id': plan_id,
            'unlimited_users': unlimited_users,
            'total_users': total_users if not unlimited_users else 0,
            'price': price,
        }
        
        # Create the record
        # ValidationError will propagate to frontend automatically
        # Odoo will handle the rollback and error response
        print("API Creating Rent Listing")
        rental_listing = request.env['toolshub.tool.rent.listings'].create(vals)
        
        # If we reach here, record was created successfully
        print(f"Rental listing created successfully: ID {rental_listing.id}")
        
        # Read the created record to return complete data
        listing_data = rental_listing.read()[0]
        
        return {
            'success': True,
            'message': 'Rental listing created successfully',
            'data': listing_data,
            'listing_id': rental_listing.id
        }

    @http.route('/toolshub/api/getUserStripeAccount', type='json', auth='user', methods=['POST'])
    def get_user_stripe_account(self, **kwargs):
        """
        Get user's Stripe Connect account ID
        
        :param user_id: int, user ID (optional, defaults to current user)
        :return: dict with stripe_connect_account_id
        """
        try:
            # If no user_id provided, use current user
            user = request.env.user
            
            # Get stripe_connect_account_id, return empty string if None
            stripe_account_id = user.stripe_connect_account_id or ''
            
            return {
                'success': True,
                'data': {
                    'stripe_connect_account_id': stripe_account_id
                }
            }
            
        except Exception as e:
            print(f"Error getting user stripe account: {str(e)}")
            return {
                'success': False,
                'data': {
                    'error': str(e),
                    'message': 'Failed to fetch user stripe account'
                }
            }

