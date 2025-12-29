{
    'name': 'POS Gallabox WhatsApp Integration',
    'version': '1.0',
    'depends': ['point_of_sale', 'pos_custom_sequence', 'portal'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_view.xml',
        'views/res_config_settings_view.xml',
        'report/pos_order_report.xml',      # Must match image_e2fb9d.png
        'views/report_receipt_template.xml', # Must match image_e2fb9d.png
    ],
    'installable': True,
}