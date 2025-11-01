from odoo import http
from odoo.http import request, route

class OwlPlayground(http.Controller):
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
        return request.render('toolshub.login_template', values)

