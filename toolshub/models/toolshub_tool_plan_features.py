from odoo import fields, models

class ToolshubToolPlanFeatures(models.Model):
    _name = "toolshub.tool.plan.features"
    _description = "Model for Toolshub Tool plan features"

    # Fields
    name = fields.Char(string="Name", required=True)
    plan_id = fields.Many2one(string="Plan", comodel_name="toolshub.tool.plans", ondelete="cascade", required=True, domain="[('tool_id', '=', tool_id)]")


    # SQL Constraints
    _sql_constraints = [
        ("unique_name", "unique(name, plan_id, plan_id.tool_id)", "Name, Tool and the Plan of the feature should be unique."),
        ('name_not_null', 'CHECK(name IS NOT NULL)', 'Name cannot be null or empty.'),
        ('plain_id_not_null', 'CHECK(plan_id IS NOT NULL)', 'Plan must be set when creating Feature.'),
    ]