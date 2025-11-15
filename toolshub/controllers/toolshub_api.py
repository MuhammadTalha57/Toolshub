import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


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
                    'tool_img_url': listing.tool_id.image_url,
                    'plan_id': listing.plan_id.id if listing.plan_id else None,
                    'plan_name': listing.plan_id.name if listing.plan_id else '',
                    'unlimited_access': listing.plan_id.is_unlimited,
                    'duration_years': listing.plan_id.duration_years,
                    'duration_months': listing.plan_id.duration_months,
                    'duration_days': listing.plan_id.duration_days,
                    'is_active': listing.is_active,
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
                    'image_url': tool.image_url,
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
        """

        _logger.info("HIT /toolshub/api/getPlans, Getting Plans")
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
            
            _logger.debug(f"Total Count of Tools: {total_count}")
            _logger.debug(f"Plans: {plans}")
            
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
                'data': {
                    'plans': plans_data
                },
            }
            
        except Exception as e:
            _logger.error(str(e))
            return {
                'success': False,
                'data': {
                    'message': "Failed to get Plans",
                    'error': str(e)
                }
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
            _logger.error("Missing Arguments while creating rent listing")
            return {
                'success': False,
                'data': {
                    'message': "Required Parameters are missing",
                }
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
                    _logger.error("Total Users not provided")
                    return {
                        'success': False,
                        'data': {
                            'message': 'total_users is required when unlimited_users is False',
                        }
                    }
                if total_users <= 0:
                    _logger.error("Total Users are not positive")
                    return {
                        'success': False,
                        'data': {
                            'message': 'total_users must be greater than 0',
                        }
                    }
            else:
                total_users = 0
                
        except (ValueError, TypeError) as e:
            _logger.error("Invalid Data Format")
            return {
                'success': False,
                'data': {
                    'message': f'Invalid data format: {str(e)}',
                    'error': str(e)
                }
            }
        
        # Check if tool exists
        tool = request.env['toolshub.tools'].browse(tool_id)
        if not tool.exists():
            _logger.error(f"Tool Not found Tool ID = {tool_id}")
            return {
                'success': False,
                'data': {
                    'message': f'Selected Tool Not Found'
                }
            }
        
        # Check if plan exists and belongs to the tool
        plan = request.env['toolshub.tool.plans'].browse(plan_id)
        if not plan.exists():
            _logger.error(f"Plan Not found Tool ID = {plan_id}")
            return {
                'success': False,
                'data': {
                    'message': f'Selected Plan Not Found'
                }
            }
        
        if plan.tool_id.id != tool_id:
            _logger.error(f"Invalid Plan for Selected Tool Tool ID = {tool_id}, Plan ID = {plan_id}")
            return {
                'success': False,
                'data': {
                    'message': f'Selected plan does not belong to the selected tool'
                }
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

        rental_listing = request.env['toolshub.tool.rent.listings'].create(vals)
        
        # If we reach here, record was created successfully
        _logger.debug(f"Rental listing created successfully: ID {rental_listing.id}")
        _logger.info("Rent Listing Created Successfully")
        
        # Read the created record to return complete data
        listing_data = rental_listing.read()[0]
        
        return {
            'success': True,
            'data': {
                'message': 'Rental listing created successfully'
            }
        }

    @http.route('/toolshub/api/getUserStripeAccount', type='json', auth='user', methods=['POST'])
    def get_user_stripe_account(self, **kwargs):
        """
        Get user's Stripe Connect account ID
        """
        try:
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
            _logger.error(f"Error getting user stripe account: {str(e)}")
            return {
                'success': False,
                'data': {
                    'error': str(e),
                    'message': 'Failed to fetch user stripe account'
                }
            }

    @http.route('/toolshub/api/toggleListingActive', type='json', auth='user', methods=['POST'])
    def toggle_listing_active(self, **kwargs):
        """
        Toggle is_active status of a rental listing
        Expected params: listing_id
        """
        _logger.info("HIT /toolshub/api/toggleListingActive, Toggling Listing Active Status")
        
        # Validate required fields
        listing_id = kwargs.get('listing_id')
        
        if not listing_id:
            _logger.error("Missing listing_id parameter")
            return {
                'success': False,
                'data': {
                    'message': "listing_id parameter is required",
                }
            }
        
        try:
            listing_id = int(listing_id)
        except (ValueError, TypeError) as e:
            _logger.error(f"Invalid listing_id format: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': f'Invalid listing_id format: {str(e)}',
                    'error': str(e)
                }
            }
        
        try:
            # Get the listing
            RentListing = request.env['toolshub.tool.rent.listings'].sudo()
            listing = RentListing.browse(listing_id)
            
            if not listing.exists():
                _logger.error(f"Listing not found with ID = {listing_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'Listing not found'
                    }
                }
            
            # Check if current user is the owner
            if listing.owner_id.id != request.env.user.id:
                _logger.error(f"User {request.env.user.id} attempted to toggle listing {listing_id} owned by {listing.owner_id.id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'You can only toggle your own listings'
                    }
                }
            
            # Toggle is_active
            new_status = not listing.is_active
            listing.write({'is_active': new_status})
            
            _logger.debug(f"Listing {listing_id} is_active toggled to {new_status}")
            _logger.info(f"Listing Active Status Toggled Successfully for Listing ID {listing_id}")
            
            return {
                'success': True,
                'data': {
                    'message': 'Listing status updated successfully',
                    'listing_id': listing_id,
                    'is_active': new_status
                }
            }
            
        except Exception as e:
            _logger.error(f"Error toggling listing active status: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'Failed to toggle listing status',
                    'error': str(e)
                }
            }

    @http.route('/toolshub/api/createRentRecord', type='json', auth='user', methods=['POST'])
    def create_rent_record(self, listing_id, **kwargs):
        """
        Create a rental record in toolshub.rented.tools
        Required params: listing_id
        """
        _logger.info(f"Creating rent record for listing ID: {listing_id}")
        
        # Validate listing_id
        if not listing_id:
            _logger.error("Missing listing_id parameter")
            return {
                'success': False,
                'data': {
                    'message': "listing_id parameter is required",
                }
            }
        
        try:
            listing_id = int(listing_id)
        except (ValueError, TypeError) as e:
            _logger.error(f"Invalid listing_id format: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': f'Invalid listing_id format: {str(e)}',
                    'error': str(e)
                }
            }
        
        try:
            # Get the listing
            RentListing = request.env['toolshub.tool.rent.listings'].sudo()
            listing = RentListing.browse(listing_id)
            
            if not listing.exists():
                _logger.error(f"Listing not found with ID = {listing_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'Listing not found'
                    }
                }
            
            # Check if listing is active
            if not listing.is_active:
                _logger.error(f"Attempted to rent inactive listing ID = {listing_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'This listing is no longer active'
                    }
                }
            
            # Get current user (lender)
            current_user = request.env.user
            
            # Prevent renting own listing
            if listing.owner_id.id == current_user.id:
                _logger.error(f"User {current_user.id} attempted to rent their own listing {listing_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'You cannot rent your own listing'
                    }
                }
            
            # Check if user already rented this listing
            RentedTools = request.env['toolshub.rented.tools'].sudo()
            existing_rent = RentedTools.search([
                ('rent_listing_id', '=', listing_id),
                ('lender_id', '=', current_user.id)
            ], limit=1)
            
            if existing_rent:
                _logger.warning(f"User {current_user.id} already rented listing {listing_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'You have already rented this listing'
                    }
                }
            
            # Prepare values for creation
            vals = {
                'rent_listing_id': listing_id,
                'lender_id': current_user.id,
            }
            
            # Create the rental record
            rented_record = RentedTools.create(vals)
            
            _logger.debug(f"Rental record created successfully: ID {rented_record.id}")
            _logger.info(f"Rent Record Created Successfully for Listing ID {listing_id}, User ID {current_user.id}")
            
            return {
                'success': True,
                'data': {
                    'message': 'Rental record created successfully',
                }
            }
            
        except Exception as e:
            _logger.error(f"Error creating rent record: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'Failed to create rental record',
                    'error': str(e)
                }
            }

    @http.route('/toolshub/api/getRentedTools', type='json', auth='user', methods=['POST'])
    def get_rented_tools(self, **kwargs):
        """
        Get all rented tools for the current user
        """
        _logger.info("HIT /toolshub/api/getRentedTools, Getting Rented Tools")
        
        try:
            # Get current user
            current_user = request.env.user
            
            # Query rented tools for current user
            RentedTools = request.env['toolshub.rented.tools'].sudo()
            domain = [('lender_id', '=', current_user.id)]
            
            rented_tools = RentedTools.search(domain, order='id desc')
            
            _logger.debug(f"Found {len(rented_tools)} rented tools for user {current_user.id}")
            
            # Format data
            rented_tools_data = []
            for rented_tool in rented_tools:
                listing = rented_tool.rent_listing_id
            
                # Build listing object
                listing_data = {
                    'id': listing.id,
                    'tool_id': listing.tool_id.id if listing.tool_id else None,
                    'tool_name': listing.tool_id.name if listing.tool_id else '',
                    'tool_img': listing.tool_id.icon,
                    'tool_img_url': listing.tool_id.image_url,
                    'plan_id': listing.plan_id.id if listing.plan_id else None,
                    'plan_name': listing.plan_id.name if listing.plan_id else '',
                    'unlimited_access': listing.plan_id.is_unlimited,
                    'duration_years': listing.plan_id.duration_years,
                    'duration_months': listing.plan_id.duration_months,
                    'duration_days': listing.plan_id.duration_days,
                    'is_active': listing.is_active,
                    'price': listing.price,
                    'currency_symbol': listing.currency_id.symbol if listing.currency_id else '$',
                    'subscribers_count': listing.subscribers_count,
                    'unlimited_users': listing.unlimited_users,
                    'available_users': listing.available_users if not listing.unlimited_users else None,
                    'owner_id': listing.owner_id.id if listing.owner_id else None,
                    'owner_name': listing.owner_id.name if listing.owner_id else '',
                    'owner_connect_account_id': listing.owner_id.stripe_connect_account_id
                }
            
                rented_tools_data.append({
                    'id': rented_tool.id,
                    'remaining_usage': rented_tool.remaining_usage,
                    'listing': listing_data,
                    'lender_id': rented_tool.lender_id.id if rented_tool.lender_id else None,
                    'is_active': rented_tool.is_active,
                    'login': rented_tool.login,
                    'password': rented_tool.password
                })
            
            return {
            'success': True,
            'data': {
                'rented_tools': rented_tools_data
            }
            }
            
        except Exception as e:
            _logger.error(f"Error getting rented tools: {str(e)}")
            return {
            'success': False,
            'data': {
                'message': 'Failed to get rented tools',
                'error': str(e)
            }
        }

    @http.route('/toolshub/api/getRentedOutTools', type='json', auth='user', methods=['POST'])
    def get_rented_out_tools(self, **kwargs):
        """
        Get all tools that the current user has rented out to others
        """
        _logger.info("HIT /toolshub/api/getRentedOutTools, Getting Rented Out Tools")
        
        try:
            # Get current user
            current_user = request.env.user
            
            # Query rented tools where the listing owner is the current user
            RentedTools = request.env['toolshub.rented.tools'].sudo()
            domain = [('rent_listing_id.owner_id', '=', current_user.id)]
            
            rented_out_tools = RentedTools.search(domain, order='id desc')
            
            _logger.debug(f"Found {len(rented_out_tools)} rented out tools for user {current_user.id}")
            
            # Format data
            rented_out_tools_data = []
            for rented_tool in rented_out_tools:
                listing = rented_tool.rent_listing_id
            
                # Build listing object
                listing_data = {
                    'id': listing.id,
                    'tool_id': listing.tool_id.id if listing.tool_id else None,
                    'tool_name': listing.tool_id.name if listing.tool_id else '',
                    'tool_img': listing.tool_id.icon,
                    'tool_img_url': listing.tool_id.image_url,
                    'plan_id': listing.plan_id.id if listing.plan_id else None,
                    'plan_name': listing.plan_id.name if listing.plan_id else '',
                    'unlimited_access': listing.plan_id.is_unlimited,
                    'duration_years': listing.plan_id.duration_years,
                    'duration_months': listing.plan_id.duration_months,
                    'duration_days': listing.plan_id.duration_days,
                    'is_active': listing.is_active,
                    'price': listing.price,
                    'currency_symbol': listing.currency_id.symbol if listing.currency_id else '$',
                    'subscribers_count': listing.subscribers_count,
                    'unlimited_users': listing.unlimited_users,
                    'available_users': listing.available_users if not listing.unlimited_users else None,
                    'owner_id': listing.owner_id.id if listing.owner_id else None,
                    'owner_name': listing.owner_id.name if listing.owner_id else '',
                    'owner_connect_account_id': listing.owner_id.stripe_connect_account_id
                }
            
                rented_out_tools_data.append({
                    'id': rented_tool.id,
                    'remaining_usage': rented_tool.remaining_usage,
                    'listing': listing_data,
                    'lender_id': rented_tool.lender_id.id if rented_tool.lender_id else None,
                    'lender_name': rented_tool.lender_id.name if rented_tool.lender_id else '',
                    'is_active': rented_tool.is_active,
                    'login': rented_tool.login,
                    'password': rented_tool.password
                })
            
            return {
                'success': True,
                'data': {
                    'rented_out_tools': rented_out_tools_data
                }
            }
            
        except Exception as e:
            _logger.error(f"Error getting rented out tools: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'Failed to get rented out tools',
                    'error': str(e)
                }
            }

    @http.route('/toolshub/api/updateRentedToolCredentials', type='json', auth='user', methods=['POST'])
    def update_rented_tool_credentials(self, rented_tool_id, login, password, **kwargs):
        """
        Update login and password for a rented tool
        Expected params: rented_tool_id, login, password
        """
        _logger.info("HIT /toolshub/api/updateRentedToolCredentials, Updating Rented Tool Credentials")
        
        # Validate required fields
        # rented_tool_id = kwargs.get('rented_tool_id')
        # login = kwargs.get('login')
        # password = kwargs.get('password')
        
        if not rented_tool_id:
            _logger.error("Missing rented_tool_id parameter")
            return {
                'success': False,
                'data': {
                    'message': "rented_tool_id parameter is required",
                }
            }
        
        if not login or not password:
            _logger.error("Missing login or password parameters")
            return {
                'success': False,
                'data': {
                    'message': "login and password parameters are required",
                }
            }
        
        try:
            rented_tool_id = int(rented_tool_id)
        except (ValueError, TypeError) as e:
            _logger.error(f"Invalid rented_tool_id format: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': f'Invalid rented_tool_id format: {str(e)}',
                    'error': str(e)
                }
            }
        
        try:
            # Get the rented tool record
            RentedTools = request.env['toolshub.rented.tools'].sudo()
            rented_tool = RentedTools.browse(rented_tool_id)
            
            if not rented_tool.exists():
                _logger.error(f"Rented tool not found with ID = {rented_tool_id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'Rented tool record not found'
                    }
                }
            
            # Check if current user is the owner of the listing
            current_user = request.env.user
            if rented_tool.rent_listing_id.owner_id.id != current_user.id:
                _logger.error(f"User {current_user.id} attempted to update credentials for rented tool {rented_tool_id} owned by {rented_tool.rent_listing_id.owner_id.id}")
                return {
                    'success': False,
                    'data': {
                        'message': 'You can only update credentials for your own rented out tools'
                    }
                }
            
            # Update credentials
            rented_tool.write({
                'login': login,
                'password': password
            })
            
            _logger.debug(f"Credentials updated for rented tool ID {rented_tool_id}")
            _logger.info(f"Rented Tool Credentials Updated Successfully for ID {rented_tool_id}")
            
            return {
                'success': True,
                'data': {
                    'message': 'Credentials updated successfully',
                    'login': login,
                    'password': password,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error updating rented tool credentials: {str(e)}")
            return {
                'success': False,
                'data': {
                    'message': 'Failed to update credentials',
                    'error': str(e)
                }
            }

