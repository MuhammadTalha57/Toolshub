from odoo import fields, models, api

class ToolshubRentedTools(models.Model):
    _name = "toolshub.rented.tools"
    _description = "Model for Rented Toos."

    # Fields
    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing")
    lender_id = fields.Many2one("res.users", string="Lender", required=True, ondelete="cascade")

    # payment_intent_id = fields.Char(
    #     string="Stripe PaymentIntent ID",
    #     readonly=True,
    #     copy=False,
    #     help="ID of the Stripe PaymentIntent (pi_...)"
    # )


    # payment_status = fields.Char(
    #     string="Payment Status",
    #     readonly=True,
    #     copy=False,
    #     help="Stripe PaymentIntent status"
    # )