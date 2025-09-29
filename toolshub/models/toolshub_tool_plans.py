from odoo import fields, models, api

class ToolshubToolPlans(models.Model):
    _name = "toolshub.tool.plans"
    _description = "Model for subscription plans of tools."

    # Fields
    name = fields.Char(string="Name", required=True)
    tool_id = fields.Many2one(string="Tool", comodel_name="toolshub.tools", ondelete="cascade", required=True)
    total_users = fields.Integer(string="Total Users", help="Max Number of Users allowed. Set 0 for unlimited.")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string="Price", currency_field="currency_id", required=True)


    # Subscription Duration
    duration_years = fields.Integer(string="Years", default=0)
    duration_months = fields.Integer(string="Months", default=0)
    duration_days = fields.Integer(string="Days", default=0)
    is_unlimited = fields.Boolean(string="Unlimited Access", default=True)

    # Features
    feature_ids = fields.One2many(comodel_name="toolshub.tool.plan.features", inverse_name="plan_id")


    # SQL Constraints
    _sql_constraints = [
        ('unique_name_tool', 'unique(name, tool_id)', 'The combination of Name and Tool must be unique.'),
        ('positive_total_users', 'CHECK(total_users >= 0)', 'Total Users cannot be negative.'),
        ('positive_price', 'CHECK(price >= 0)', 'Price cannot be negative.'),
        ('positive_duration_years', 'CHECK(duration_years >= 0)', 'Years cannot be negative.'),
        ('positive_duration_months', 'CHECK(duration_months >= 0)', 'Months cannot be negative.'),
        ('positive_duration_days', 'CHECK(duration_days >= 0)', 'Days cannot be negative.'),
        ('name_not_null', 'CHECK(name IS NOT NULL AND name <> \'\')', 'Name cannot be null or empty.'),
        ('tool_id_not_null', 'CHECK(tool_id IS NOT NULL)', 'Tool must be set.'),
    ]
    
    # When Users toggle is_unlimited
    @api.onchange('is_unlimited')
    def _onchange_is_unlimited(self):
        if self.is_unlimited:
            self.duration_years = 0
            self.duration_months = 0
            self.duration_days = 0
