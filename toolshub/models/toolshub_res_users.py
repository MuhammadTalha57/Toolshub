from odoo import models, fields

class ResUsers(models.Model):
    # Extending Users Table
    _inherit = 'res.users'

    stripe_connect_account_id = fields.Char("Stripe Connect Account ID")
