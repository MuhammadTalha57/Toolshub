# ...existing code...
from odoo import models, api
from odoo.exceptions import ValidationError
import stripe
import logging

_logger = logging.getLogger(__name__)

class ToolshubStripeService(models.AbstractModel):
    _name = "toolshub.stripe.service"
    _description = "Stripe helper service for Toolshub"

    def _get_stripe_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('stripe_api_key') or ''

    def _ensure_listing_and_seller(self, listing):
        if not listing:
            raise ValidationError("Missing rent listing")
        owner_partner = listing.owner_id.partner_id
        if not owner_partner or not owner_partner.stripe_account_id:
            raise ValidationError("Seller has not connected a Stripe account")
        return owner_partner.stripe_account_id

    def create_payment_intent(self, *, listing, buyer, amount_cents=None, currency=None,
                              payment_method_id=None, confirm=False, off_session=False,
                              application_fee_amount_cents=None):
        """Create a PaymentIntent that transfers funds to the listing owner.
        listing: record of toolshub.tool.rent.listings (recordset)
        buyer: res.users record
        Returns dict with keys: payment_intent_id, client_secret (if not confirmed), status, rented_id (if created)
        """
        stripe.api_key = self._get_stripe_key()
        if not stripe.api_key:
            raise ValidationError("Stripe API key is not configured (system parameter: stripe_api_key)")

        owner_acct = self._ensure_listing_and_seller(listing)

        # compute amount/currency defaults
        if amount_cents is None:
            price = float(listing.price or 0.0)
            amount_cents = int(round(price * 100))
        if currency is None:
            currency = (listing.currency_id and listing.currency_id.name or 'usd').lower()

        try:
            create_kwargs = {
                'amount': int(amount_cents),
                'currency': currency.lower(),
                'payment_method_types': ['card'],
                'transfer_data': {'destination': owner_acct},
                'metadata': {
                    'rent_listing_id': str(listing.id),
                    'buyer_id': str(buyer.id if buyer else ''),
                }
            }
            if application_fee_amount_cents:
                create_kwargs['application_fee_amount'] = int(application_fee_amount_cents)

            if confirm:
                if not payment_method_id:
                    raise ValidationError("payment_method_id is required to confirm on server")
                create_kwargs.update({
                    'payment_method': payment_method_id,
                    'confirm': True,
                    'off_session': bool(off_session),
                })
                pi = stripe.PaymentIntent.create(**create_kwargs)
                # create rented record
                rented = self.env['toolshub.rented.tools'].sudo().create({
                    'rent_listing_id': listing.id,
                    'lender_id': buyer.id if buyer else False,
                    'payment_intent_id': getattr(pi, 'id', False),
                    'payment_status': getattr(pi, 'status', False),
                })
                return {
                    'payment_intent_id': getattr(pi, 'id', False),
                    'status': getattr(pi, 'status', False),
                    'rented_id': rented.id,
                }
            else:
                pi = stripe.PaymentIntent.create(**create_kwargs)
                return {
                    'payment_intent_id': getattr(pi, 'id', False),
                    'client_secret': getattr(pi, 'client_secret', False),
                    'status': getattr(pi, 'status', False),
                }
        except Exception as e:
            _logger.exception("Stripe error")
            raise ValidationError(str(e))
# ...existing code...