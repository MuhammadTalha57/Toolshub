from odoo import fields, models, api
from datetime import datetime, timedelta

class ToolshubRentedTools(models.Model):
    _name = "toolshub.rented.tools"
    _description = "Model for Rented Toos."

    # Fields
    rent_listing_id = fields.Many2one("toolshub.tool.rent.listings", string="Rent Listing", readonly=True, required=True)
    lender_id = fields.Many2one("res.users", string="Lender", required=True, ondelete="cascade", readonly=True)
    is_active = fields.Boolean("Is Active")
    
    login = fields.Char("Login")
    password = fields.Char("Password")

    rented_date = fields.Datetime(
        string="Rented Date",
        default=fields.Datetime.now,
        readonly=True,
        required=True,
        help="Date and time when the tool was rented"
    )
    
    expiry_date = fields.Datetime(
        string="Expiry Date",
        compute="_compute_expiry_date",
        store=True,
        readonly=True,
        help="Date and time when the rental expires (None if unlimited access)"
    )
    
    remaining_usage = fields.Char(
        string="Remaining Usage",
        compute="_compute_remaining_usage",
        help="Remaining time until expiry (-1 for unlimited access)"
    )


    # Compute expiry date based on listing duration
    @api.depends('rent_listing_id', 'rent_listing_id.plan_id.is_unlimited', 
                 'rent_listing_id.plan_id.duration_years', 
                 'rent_listing_id.plan_id.duration_months', 
                 'rent_listing_id.plan_id.duration_days',
                 'rented_date')
    def _compute_expiry_date(self):
        for record in self:
            # if not record.rent_listing_id or not record.rent_listing_id.plan_id:
            #     record.expiry_date = False
            #     continue
            
            plan = record.rent_listing_id.plan_id
            
            # If unlimited access, no expiry date
            if plan.is_unlimited:
                record.expiry_date = False
                continue
            
            # Calculate expiry date from rented_date + duration
            rented_dt = record.rented_date or fields.Datetime.now()
            
            years = plan.duration_years or 0
            months = plan.duration_months or 0
            days = plan.duration_days or 0
            
            # Calculate total days (approximate: 1 year = 365 days, 1 month = 30 days)
            total_days = (years * 365) + (months * 30) + days
            
            if total_days > 0:
                record.expiry_date = rented_dt + timedelta(days=total_days)
    
    # Compute remaining usage
    @api.depends('rent_listing_id', 'rent_listing_id.plan_id.is_unlimited', 
                 'expiry_date', 'rented_date')
    def _compute_remaining_usage(self):
        for record in self:
            
            plan = record.rent_listing_id.plan_id
            
            # If unlimited access, return -1
            if plan.is_unlimited:
                record.remaining_usage = "Unlimited Access"
                continue
            
            # If no expiry date, can't calculate
            if not record.expiry_date:
                record.remaining_usage = "N/A"
                continue
            
            # Calculate remaining time
            now = fields.Datetime.now()
            
            # If already expired
            if now >= record.expiry_date:
                record.remaining_usage = "Expired"
                continue
            
            # Calculate difference
            delta = record.expiry_date - now
            
            days = delta.days
            record.remaining_usage = ""
            
            usage_string = ""
            # Format remaining time
            if days >= 365:
                years = days // 365
                days = days % 365
                record.remaining_usage += f"{years} year(s) "

            if days >= 30:
                months = days // 30
                days = days % 30
                record.remaining_usage += f"{months} month(s) "
                
            if days > 0:
                record.remaining_usage += f"{days} day(s)"

    
    # Compute is_active based on expiry
    @api.depends('rent_listing_id', 'rent_listing_id.plan_id.is_unlimited', 
                 'expiry_date', 'payment_status')
    def _compute_is_active(self):
        for record in self:
            
            plan = record.rent_listing_id.plan_id
            
            # If unlimited access, always active (unless payment failed)
            if plan.is_unlimited:
                record.is_active = True
                continue
            
            # If no expiry date, can't determine
            if not record.expiry_date:
                record.is_active = True
                continue
            
            # Active if current time is before expiry
            now = fields.Datetime.now()
            record.is_active = now < record.expiry_date

