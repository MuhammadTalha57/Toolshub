from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import stripe
import logging

_logger = logging.getLogger(__name__)


def _get_stripe_key():
    return request.env['ir.config_parameter'].sudo().get_param('stripe.secret_key') or ''


class ToolshubStripeController(http.Controller):

    @http.route('/toolshub/stripe/create_account', type='json', auth='user', csrf=False)
    def create_connect_account(self, partner_id=None, country='US'):
        """Create a Stripe Connect Express account and save account id on res.partner.stripe_account_id.
        If partner_id omitted, the current user's partner is used.
        Only admin or the partner owner can create for another partner.
        """
        stripe.api_key = _get_stripe_key()
        Partner = request.env['res.partner'].sudo()
        if partner_id:
            partner = Partner.browse(int(partner_id))
            if not partner.exists():
                raise ValidationError("Partner not found")
            # only allow creating for others if system admin
            if partner.id != request.env.user.partner_id.id and not request.env.user.has_group('base.group_system'):
                raise AccessError("Not allowed to create a Stripe account for this partner")
        else:
            partner = request.env.user.partner_id

        try:
            acct = stripe.Account.create(type='express', country=country, email=partner.email or None)
            partner.sudo().write({'stripe_account_id': acct['id']})
            return {'account_id': acct['id']}
        except Exception as e:
            _logger.exception("Stripe create account error")
            raise ValidationError(f"Stripe error: {e}")

    @http.route('/toolshub/stripe/create_account_link', type='http', auth='user', methods=['GET'], csrf=False)
    def create_account_link(self, partner_id=None):
        """Create an AccountLink and redirect the user to Stripe onboarding.
        Uses current host for return/refresh URLs.
        """
        stripe.api_key = _get_stripe_key()
        Partner = request.env['res.partner'].sudo()
        if partner_id:
            partner = Partner.browse(int(partner_id))
        else:
            partner = request.env.user.partner_id

        acct_id = partner.sudo().stripe_account_id
        if not acct_id:
            return request.make_response("Partner has no stripe_account_id; create one first", headers=[('Content-Type', 'text/plain')], status=400)

        host = request.httprequest.host_url.rstrip('/')
        refresh_url = f"{host}/toolshub/stripe/create_account_link?partner_id={partner.id}"
        return_url = f"{host}/web?redirected=from_stripe_onboarding"

        try:
            link = stripe.AccountLink.create(account=acct_id, refresh_url=refresh_url, return_url=return_url, type='account_onboarding')
            return request.redirect(link.url)
        except Exception as e:
            _logger.exception("Stripe account link error")
            return request.make_response(f"Stripe error: {e}", headers=[('Content-Type', 'text/plain')], status=500)

    @http.route('/toolshub/stripe/create_payment_intent', type='json', auth='user', csrf=False)
    def create_payment_intent(self, rent_listing_id, amount_cents=None, currency=None, payment_method_id=None, confirm=False, off_session=False, application_fee_amount_cents=None):
        """JSON endpoint for frontend to create PaymentIntent server-side.
           Returns the same dict as service.create_payment_intent.
        """
        if not rent_listing_id:
            raise ValidationError("rent_listing_id is required")
        listing = request.env['toolshub.tool.rent.listings'].sudo().browse(int(rent_listing_id))
        if not listing.exists():
            raise ValidationError("Rent listing not found")

        buyer = request.env.user

        service = request.env['toolshub.stripe.service'].sudo()
        result = service.create_payment_intent(
            listing=listing,
            buyer=buyer,
            amount_cents=amount_cents,
            currency=currency,
            payment_method_id=payment_method_id,
            confirm=bool(confirm),
            off_session=True,
            application_fee_amount_cents=application_fee_amount_cents
        )
        return result





        # """Create a PaymentIntent that transfers funds to the listing owner (Connect).
        # - rent_listing_id: id of toolshub.tool.rent.listings
        # - amount_cents: optional override amount in cents (if omitted taken from listing.price)
        # - currency: optional currency string (e.g. 'usd')
        # - payment_method_id: optional Stripe PaymentMethod id (if planning server-side confirm)
        # - confirm: if true the intent will be confirmed server-side (requires payment_method_id and allowed off_session)
        # - returns client_secret (when not confirmed) or payment result when confirmed
        # """
        # stripe.api_key = _get_stripe_key()
        # Listing = request.env['toolshub.tool.rent.listings'].sudo()
        # listing = Listing.browse(int(rent_listing_id))
        # if not listing.exists():
        #     raise ValidationError("Rent listing not found")

        # owner_partner = listing.owner_id.partner_id.sudo()
        # owner_acct = owner_partner.stripe_account_id
        # if not owner_acct:
        #     raise ValidationError("Seller has not connected a Stripe account")

        # # amount and currency default from listing
        # if amount_cents is None:
        #     price = float(listing.price or 0.0)
        #     amount_cents = int(round(price * 100))
        # if currency is None:
        #     currency = (listing.currency_id and listing.currency_id.name or 'usd').lower()

        # try:
        #     create_kwargs = {
        #         'amount': int(amount_cents),
        #         'currency': currency.lower(),
        #         'payment_method_types': ['card'],
        #         'transfer_data': {'destination': owner_acct},
        #         'metadata': {
        #             'rent_listing_id': str(listing.id),
        #             'buyer_id': str(request.env.user.id)
        #         }
        #     }
        #     if application_fee_amount_cents:
        #         create_kwargs['application_fee_amount'] = int(application_fee_amount_cents)

        #     if confirm:
        #         if not payment_method_id:
        #             raise ValidationError("payment_method_id is required to confirm on server")
        #         create_kwargs.update({
        #             'payment_method': payment_method_id,
        #             'confirm': True,
        #             'off_session': bool(off_session),
        #         })
        #         pi = stripe.PaymentIntent.create(**create_kwargs)
        #         # create rented record on successful/processing payments
        #         rented_model = request.env['toolshub.rented.tools'].sudo()
        #         rented = rented_model.create({
        #             'rent_listing_id': listing.id,
        #             'lender_id': request.env.user.id,
        #             'payment_intent_id': getattr(pi, 'id', False),
        #             'payment_status': getattr(pi, 'status', False),
        #         })
        #         return {
        #             'payment_intent_id': getattr(pi, 'id', False),
        #             'status': getattr(pi, 'status', False),
        #             'rented_id': rented.id,
        #         }
        #     else:
        #         # create PaymentIntent and return client_secret for frontend confirmation
        #         pi = stripe.PaymentIntent.create(**create_kwargs)
        #         return {
        #             'payment_intent_id': getattr(pi, 'id', False),
        #             'client_secret': getattr(pi, 'client_secret', False),
        #             'status': getattr(pi, 'status', False),
        #         }
        # except stripe.error.CardError as e:
        #     _logger.exception("Stripe card error")
        #     raise ValidationError(getattr(e, 'user_message', str(e)))
        # except Exception as e:
        #     _logger.exception("Stripe error")
        #     raise ValidationError(str(e))