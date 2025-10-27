from odoo import http
from odoo.http import request, route

class OwlPlayground(http.Controller):
    @http.route(['/toolshub'], type='http', auth='public')
    def show_homepage(self):
        """
        Renders the owl playground page
        """
        print("Controller hit")
        return request.render('toolshub.frontend_template')

