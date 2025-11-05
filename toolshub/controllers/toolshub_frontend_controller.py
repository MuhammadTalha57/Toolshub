from odoo import http
from odoo.http import request, route

class ToolshubFrontendController(http.Controller):
    @http.route(['/toolshub'], type='http', auth='public', website=True)
    def show_homepage(self):
        """
        Renders the owl playground page
        """
        website = request.env['website'].sudo().get_current_website()
        values = {
            'website': website,
            'preview_object': False,
        }
        print("Controller hit")
        return request.render('toolshub.main_app', values)
    

    @http.route(['/toolshub/getRentListings'], type='json', auth='user', methods=['POST'])
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
