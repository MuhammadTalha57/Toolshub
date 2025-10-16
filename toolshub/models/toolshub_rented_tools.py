from odoo import fields, models, api

class ToolshubRentedTools(models.Model):
    _name = "toolshub.rented.tools"
    _description = "Model for Rented Toos."

    # Fields
    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing")
    # owner_id = fields.Many2one("res.users", string="Owner", required=True, ondelete="cascade", related="rent_listing_id.owner_id")
    lender_id = fields.Many2one("res.users", string="Lender", required=True, ondelete="cascade")
    # currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", default=lambda self: self.env.company.currency_id)
    # price = fields.Monetary(string="Price", related="rent_listing_id.price", currency_field="currency_id")
    # tool_id = fields.Many2one(string="Tool", related="rent_listing_id.tool_id")
    # plan_id = fields.Many2one(string="Plan", related="rent_listing_id.plan_id")

    payment_intent_id = fields.Char(
        string="Stripe PaymentIntent ID",
        readonly=True,
        copy=False,
        help="ID of the Stripe PaymentIntent (pi_...)"
    )


    payment_status = fields.Char(
        string="Payment Status",
        readonly=True,
        copy=False,
        help="Stripe PaymentIntent status"
    )