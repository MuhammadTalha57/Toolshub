from odoo import fields, models, api

class ToolshubRentedTools(models.Model):
    _name = "toolshub.rented.tools"
    _description = "Model for Rented Toos."

    # Fields
    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing")
    lender_id = fields.Many2one("res.users", string="Lender", required=True, ondelete="cascade")