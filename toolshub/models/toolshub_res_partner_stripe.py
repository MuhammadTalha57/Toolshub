# ...existing code...
from odoo import models, fields

class ResPartnerStripe(models.Model):
    _inherit = "res.partner"

    stripe_account_id = fields.Char(string="Stripe Account ID", copy=False)
# ...existing code...