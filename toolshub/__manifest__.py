{
    "name": "Toolshub",
    "depends": [
        "base"
    ],
    "application": True,
    'assets': {
    'web.assets_backend': [
        'toolshub/static/src/js/stripe_wizard.js',
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/toolshub_tools_views.xml",
        "views/toolshub_tool_plans_views.xml",
        "views/toolshub_tool_plan_features_views.xml",
        "views/toolshub_tool_rent_listings_views.xml",
        "views/toolshub_rented_tools_views.xml",
        "views/toolshub_rent_wizard_views.xml",
        "views/toolshub_menus.xml",
    ]
}