import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)

class ToolshubController(http.Controller):
    @http.route(['/toolshub'], type='http', auth='public', website=True)
    def show_homepage(self):
        """
        Renders the Main Toolshub App
        """
        _logger.info("Main Controller Hit, Rendering Toolshub App")
        return request.render('toolshub.main_app')
