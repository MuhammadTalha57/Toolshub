from odoo import models, fields, api
from odoo.exceptions import ValidationError
import stripe

class ToolshubRentWizard(models.TransientModel):
    _name = "toolshub.rent.wizard"
    _description = "Wizard for renting a tool"

    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing", required=True)
    buyer_id = fields.Many2one("res.users", string="Buyer", required=True)
    currency_id = fields.Many2one(related="rent_listing_id.currency_id")
    price = fields.Monetary(string="Total Price", currency_field="currency_id", readonly=True, related="rent_listing_id.price")
    payment_method_id = fields.Char("Stripe Payment Method ID")  # filled from frontend JS

    def action_pay_and_rent(self):
        for rec in self:
            stripe.api_key = self.env['ir.config_parameter'].sudo().get_param('stripe.secret_key')
            
            if not rec.payment_method_id:
                raise ValidationError("Payment information is missing. Complete the payment first.")
            
            try:
                # Create and confirm PaymentIntent
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(rec.price * 100),  # convert to cents
                    currency=rec.rent_listing_id.currency_id.name.lower(),
                    payment_method=rec.payment_method_id,
                    confirm=True,
                    off_session=True
                )
            except stripe.error.CardError as e:
                raise ValidationError(f"Payment failed: {e.user_message}")
            except Exception as e:
                raise ValidationError(f"Payment error: {str(e)}")
            
            # Payment succeeded → create rented tool
            rented_tools = self.env['toolshub.rented.tools']
            rented_tools.create({
                'rent_listing_id': rec.rent_listing_id.id,
                'lender_id': rec.buyer_id.id,
            })
