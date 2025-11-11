from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ToolshubToolRentListings(models.Model):
    _name = "toolshub.tool.rent.listings"
    _description = "Listing for Rentable Tools"

    # Fields
    tool_id = fields.Many2one("toolshub.tools", string="Tool", required=True)
    plan_id = fields.Many2one("toolshub.tool.plans", string="Plan", required=True, domain="[('tool_id', '=', tool_id)]")
    rented_tools_ids = fields.One2many("toolshub.rented.tools", "rent_listing_id", string="Rented Tools")
    subscribers_count = fields.Integer("Total Subscribers", compute="_compute_subscribers_count", store=True)

    total_users = fields.Integer(strign="Total Users")
    unlimited_users = fields.Boolean("Unlimited Users")
    available_users = fields.Integer(string="Available Users", compute="_compute_available_users", store=True, readonly=True)
    is_active = fields.Boolean("Is Active", default=True)

    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string="Price Per User", currency_field="currency_id", required=True)
    owner_id = fields.Many2one("res.users", string="Owner", required=True, default=lambda self: self.env.user, ondelete="cascade")

    

    # SQL Constraints
    _sql_constraints = [

        ('tool_id_not_null', 'CHECK(tool_id IS NOT NULL)', 'Tool must be set.'),
        ('plan_id_not_null', 'CHECK(plan_id IS NOT NULL)', 'Plan must be set.'),
        ('positive_subscribers_count', 'CHECK(subscribers_count >= 0)', 'Subscribers count cannot be negative.'),
        ('positive_price', 'CHECK(price >= 0)', 'Price cannot be negative.'),
        ('positive_total_users', 'CHECK(total_users >= 0)', 'Total Users cannot be negative.'),
        
    ]

    # Python Constraints
    @api.constrains("unlimited_users")
    def _check_unlimited_users(self):
        for record in self:
            if (not record.plan_id.unlimited_users) and record.unlimited_users:
                raise ValidationError("Selected Plan doesn't allow Unlimited Users.")

    @api.constrains("subscribers_count", "plan_id", "unlimited_users")
    def _check_subscribers_count(self):
        for record in self:
            if not record.unlimited_users:
                if record.subscribers_count > record.plan_id.total_users:
                    raise ValidationError("Subscribers Count cannot exceed total available users.")

    @api.constrains("total_users")
    def _check_total_users_count(self):
        for record in self:
            if not record.unlimited_users:
                if record.total_users > record.plan_id.total_users:
                    raise ValidationError("Total Users cannot exceed plan's total available users.")



    # Computing Available Users
    @api.depends('subscribers_count', "plan_id.total_users", "unlimited_users")
    def _compute_available_users(self):
        if not self.unlimited_users:
            for record in self:
                record.available_users = record.total_users - record.subscribers_count

    # Calculating subscribers
    @api.depends('rented_tools_ids')
    def _compute_subscribers_count(self):
        for record in self:
            record.subscribers_count = len(record.rented_tools_ids)

    
    # Toggling unlimited_users
    @api.onchange('unlimited_users')
    def _onchange_unlimited_users(self):
        self.total_users = 0
        


    def action_open_rent_wizard(self):
        return {
            'name': 'Rent Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'toolshub.rent.wizard',
            'view_mode': 'form',
            'target': 'new',  # this makes it a popup
            'context': {'default_rent_listing_id': self.id}  # pass current listing
        }