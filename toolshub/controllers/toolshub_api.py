from odoo import http
from odoo.http import request

class ToolshubAPI(http.Controller):
    @http.route(['/toolshub/api/getRentListings'], type='json', auth='user', methods=['POST'])
    def get_rent_listings(self, filters=None, limit=None, offset=0):
        """
        Get rent listings with optional filters
        
        :param filters: dict of filters (e.g., {'tool_id': 1, 'owner_id': 2})
        :param limit: int, limit number of results
        :param offset: int, offset for pagination
        :return: dict with listings data
        """
        print("Getting Rent Listings")
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

            print(total_count, listings)
            
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
                })
            
            return {
                'success': True,
                'data': listings_data,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('toolshub/api/createRentListing', type='json', auth='user', methods=['POST'])
    def create_rent_listing(self, **kwargs):
        """
        Create a new rental listing
        Expected params: tool_id, plan_id, unlimited_users, total_users, price
        """
        try:
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
                    total_users = kwargs.get('total_users')
                    if total_users is None:
                        return {
                            'success': False,
                            'error': 'validation_error',
                            'message': 'total_users is required when unlimited_users is False'
                        }
                    total_users = int(total_users)
                    if total_users <= 0:
                        return {
                            'success': False,
                            'error': 'validation_error',
                            'message': 'total_users must be greater than 0'
                        }
                else:
                    total_users = 0  # Set to 0 or None for unlimited
                    
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
                # owner_id will be set automatically via default lambda
            }
            
            # Create the record
            rental_listing = request.env['toolshub.tool.rent.listings'].create(vals)
            
            # Check if record was created successfully
            if rental_listing and rental_listing.exists():
                print(f"Rental listing created successfully: ID {rental_listing.id}")
                
                # Read the created record to return complete data
                listing_data = rental_listing.read()[0]
                
                return {
                    'success': True,
                    'message': 'Rental listing created successfully',
                    'data': listing_data,
                    'listing_id': rental_listing.id
                }
            else:
                print("Failed to create rental listing - record does not exist after creation")
                return {
                    'success': False,
                    'error': 'creation_failed',
                    'message': 'Failed to create rental listing'
                }
                
        except ValueError as e:
            print(f"Validation error creating rental listing: {str(e)}")
            return {
                'success': False,
                'error': 'validation_error',
                'message': str(e)
            }
            
        except Exception as e:
            print(f"Error creating rental listing: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'server_error',
                'message': f'An error occurred: {str(e)}'
            }

