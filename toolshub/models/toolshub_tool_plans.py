from odoo import fields, models

class ToolshubToolPlans(models.Model):
    _name = "toolshub.tool.plans"
    _description = "Model for subscription plans of tools."

    #Fields
    name = fields.Char(string="Name", required=True)
    tool_id = fields.Many2one(string="Tool", comodel_name="toolshub.tools", ondelete="cascade")
    total_users = fields.Integer(string="Total Users", help="Max Number of Users allowed. Set 0 for unlimited.")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string="Price", currency_field="currency_id", required=True)