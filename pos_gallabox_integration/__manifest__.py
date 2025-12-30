{
    "name": "POS Gallabox WhatsApp Integration",
    "version": "1.0",
    "category": "Point of Sale",
    "summary": "Integrates Gallabox WhatsApp API with POS Custom Receipts",
    "depends": [
        "point_of_sale", 
        "portal",
        "custom_receipts_for_pos" # Essential for the dynamic XML bridge
    ],
    "data": [
        "security/ir.model.access.csv",      # Required for model permissions
        "views/pos_config_view.xml",
        "views/res_config_settings_view.xml",
        "views/report_receipt_template.xml", # For PDF generation logic
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_gallabox_integration/static/src/js/OrderReceipt.js",
            "pos_gallabox_integration/static/src/xml/pos_receipt.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}