{
    "name": "Toolshub",
    "depends": [
        "base", "web", "website"
    ],
    "application": True,
    "installable": True,

    'assets': {

        'web.assets_frontend': [
            'toolshub/static/src/xml/*',
            'toolshub/static/src/js/*',
            'toolshub/static/src/scss/*',
        ],

        'toolshub.frontend_assets': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            'web/static/lib/bootstrap/scss/_buttons.scss',
            ('include', 'web._assets_bootstrap'),
            ('include', 'web._assets_core'),
            'web/static/src/libs/fontawesome/css/font-awesome.css',
            'toolshub/static/src/**/*',
            'toolshub/static/src/xml/*',


            # Bootstrap core partials
            "web/static/lib/bootstrap/scss/mixins/_banner.scss",
            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            "web/static/lib/bootstrap/scss/_variables-dark.scss",
            "web/static/lib/bootstrap/scss/_maps.scss",
            "web/static/lib/bootstrap/scss/_mixins.scss",
            "web/static/lib/bootstrap/scss/_utilities.scss",

            # Layout & components
            "web/static/lib/bootstrap/scss/_root.scss",
            "web/static/lib/bootstrap/scss/_reboot.scss",
            "web/static/lib/bootstrap/scss/_type.scss",
            "web/static/lib/bootstrap/scss/_images.scss",
            "web/static/lib/bootstrap/scss/_containers.scss",
            "web/static/lib/bootstrap/scss/_grid.scss",
            "web/static/lib/bootstrap/scss/_tables.scss",
            "web/static/lib/bootstrap/scss/_forms.scss",
            "web/static/lib/bootstrap/scss/_buttons.scss",
            "web/static/lib/bootstrap/scss/_transitions.scss",
            "web/static/lib/bootstrap/scss/_dropdown.scss",
            "web/static/lib/bootstrap/scss/_button-group.scss",
            "web/static/lib/bootstrap/scss/_nav.scss",
            "web/static/lib/bootstrap/scss/_navbar.scss",
            "web/static/lib/bootstrap/scss/_card.scss",
            "web/static/lib/bootstrap/scss/_accordion.scss",
            "web/static/lib/bootstrap/scss/_breadcrumb.scss",
            "web/static/lib/bootstrap/scss/_pagination.scss",
            "web/static/lib/bootstrap/scss/_badge.scss",
            "web/static/lib/bootstrap/scss/_alert.scss",
            "web/static/lib/bootstrap/scss/_progress.scss",
            "web/static/lib/bootstrap/scss/_list-group.scss",
            "web/static/lib/bootstrap/scss/_close.scss",
            "web/static/lib/bootstrap/scss/_toasts.scss",
            "web/static/lib/bootstrap/scss/_modal.scss",
            "web/static/lib/bootstrap/scss/_tooltip.scss",
            "web/static/lib/bootstrap/scss/_popover.scss",
            "web/static/lib/bootstrap/scss/_carousel.scss",
            "web/static/lib/bootstrap/scss/_spinners.scss",
            "web/static/lib/bootstrap/scss/_offcanvas.scss",
            "web/static/lib/bootstrap/scss/_placeholders.scss",

            # Helpers & utilities
            "web/static/lib/bootstrap/scss/_helpers.scss",
            "web/static/lib/bootstrap/scss/utilities/_api.scss",

        ],
    },

    "data": [
        "security/ir.model.access.csv",
        "security/toolshub_security.xml",
        "views/toolshub_tools_views.xml",
        "views/toolshub_tool_plans_views.xml",
        "views/toolshub_tool_plan_features_views.xml",
        "views/toolshub_tool_rent_listings_views.xml",
        "views/toolshub_rented_tools_views.xml",
        "views/toolshub_menus.xml",
        "views/toolshub_main_template.xml",
    ]
}