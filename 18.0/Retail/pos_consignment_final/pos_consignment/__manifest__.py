
{
    "name": "POS Consignment",
    "version": "16.0.3.0.0",
    "summary": "Manage consignment products in POS with vendor contracts, settlements, portal, and POS UI",
    "category": "Point of Sale",
    "author": "ChatGPT",
    "depends": ["base", "stock", "point_of_sale", "portal", "account", "website"],
    "data": [
        "security/ir.model.access.csv",
        "views/consignment_views.xml",
        "views/consignment_portal_templates.xml",
        "views/consignment_reports.xml",
        "data/consignment_data.xml",
        "data/cron_consignment_settlement.xml",
        "data/email_templates.xml"
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_consignment_final/static/src/js/consignment_pos.js",
            "pos_consignment_final/static/src/css/consignment_pos.css"
        ]
    },
    "license": "LGPL-3",
    "installable": True,
    "application": False
}
