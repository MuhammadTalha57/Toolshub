from odoo import fields, models

class ToolshubTools(models.Model):
    _name = "toolshub.tools"
    _description = "Model for Toolshub Tools"

    # Fields
    name = fields.Char(string="Name", required=True)
    icon = fields.Image(string="Icon", required=True, max_width=64, max_height=64, verify_resolution=True)
    image_url = fields.Char(string="URL", required=True)
    plan_ids = fields.One2many(comodel_name="toolshub.tool.plans", inverse_name="tool_id", string="Plans")


    # SQL Constraints
    _sql_constraints = [
        ("unique_name", "unique(name)", "Name of the tool should be unique.")
    ]