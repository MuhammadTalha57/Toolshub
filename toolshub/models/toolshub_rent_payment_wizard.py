# ...existing code...
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ToolshubRentPaymentWizard(models.TransientModel):
    _name = "toolshub.rent.payment.wizard"
    _description = "Wizard to collect buyer and stripe payment info for rent"

    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing", required=True)
    buyer_id = fields.Many2one('res.users', string="Buyer", required=True)
    payment_method_id = fields.Char(string="Stripe PaymentMethod ID", help="PaymentMethod id (pm_...) if confirming server-side")
    confirm = fields.Boolean(string="Confirm payment on server", default=True)
    application_fee_amount = fields.Monetary(string="Platform fee", currency_field='currency_id', help="Optional platform fee (will be taken from the amount)")
    currency_id = fields.Many2one(related='rent_listing_id.currency_id', readonly=True)

    def action_process_payment(self):
        self.ensure_one()
        service = self.env['toolshub.stripe.service'].sudo()
        listing = self.rent_listing_id.sudo()
        buyer_user = self.buyer_id.sudo()

        try:
            amount_cents = None
            if self.rent_listing_id.price:
                amount_cents = int(round(float(self.rent_listing_id.price) * 100))
            app_fee_cents = None
            if self.application_fee_amount:
                app_fee_cents = int(round(float(self.application_fee_amount) * 100))

            result = service.create_payment_intent(
                listing=listing,
                buyer=buyer_user,
                amount_cents=amount_cents,
                currency=(self.currency_id and self.currency_id.name) or None,
                payment_method_id=self.payment_method_id,
                confirm=bool(self.confirm),
                off_session=True,
                application_fee_amount_cents=app_fee_cents
            )
        except ValidationError as e:
            # show error to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Payment failed',
                    'type': 'danger',
                    'message': str(e.name) if hasattr(e, 'name') else str(e),
                    'sticky': True,
                }
            }

        # success notification
        msg = "Payment created"
        if result.get('status'):
            msg += f": {result.get('status')}"
        if result.get('rented_id'):
            msg += " — Rented record created"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Stripe Payment',
                'type': 'success',
                'message': msg,
                'sticky': False,
            }
        }
# ...existing code...