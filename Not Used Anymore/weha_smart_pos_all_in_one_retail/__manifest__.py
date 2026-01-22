# Part of Softhealer Technologies.
{
    "name": "Operacion Retail Grupo San Luis",
    "author": "Sinergia Asesores",
    "website": "https://www.sinergia-e.com",
    "support": "soporte@sinergia-e.com",
    "category": "Point of Sale",
    "summary": "Funciones para operacion retail en Abarrotes San Luis",
    "description": """ Modulos Retail.  """,
    "version": "14.0.4",
    "depends": ["base", "web", "utm", "point_of_sale", "hr", "portal", "pos_hr", 'sale'],
    "application": True,
    "license": "OPL-1",
    "data": [
        'security/ir.model.access.csv',
        'security/access_rights_data.xml',
        'security/pos_sh_pos_cancel_security.xml',
        'data/sh_pos_receipt_report_paperformat.xml',
        'reports/pos_order_report.xml',
        'data/sh_pos_loyalty_data.xml',
        'data/sh_pos_cancel_demo_data.xml',
        'data/keyboard_demo_data.xml',
        'data/sh_pos_receipt_pos_order_mail_template.xml',
        'data/sh_cash_in_paper_format.xml',

        'sh_portal_pos/security/ir.model.access.csv',
        'sh_portal_pos/views/sh_portal_pos_view.xml',

        'sh_pos_cancel/views/pos_order_cancel_config_settings.xml',
        'sh_pos_cancel/views/orderviews.xml',

        'sh_pos_keyboard_shortcut/security/ir.model.access.csv',
        'sh_pos_note/security/ir.model.access.csv',
        "pos_product_suggestion/security/ir.model.access.csv",
        "sh_pos_theme_responsive/security/ir.model.access.csv",

        'sh_pos_rounding/data/data.xml',
        "sh_pos_theme_responsive/data/pos_theme_settings_data.xml",

        'sh_pos_loyalty/views/pos_loyalty.xml',
        'sh_pos_loyalty/views/sh_pos_loyalty.xml',
        'sh_pos_keyboard_shortcut/views/pos_quick_order_tmpl.xml',
        'sh_pos_keyboard_shortcut/views/pos_config.xml',

        'sh_pos_note/views/sh_pos_note.xml',
        'sh_pos_note/views/pos_config.xml',
        'sh_pos_note/views/pos_order.xml',
        'sh_pos_note/views/pre_define_note.xml',

        "sh_pos_theme_responsive/views/sh_pos_theme_responsive.xml",
        "sh_pos_theme_responsive/views/pos_config_view.xml",

        "sh_pos_counter/views/custom_pos_view.xml",
        "sh_pos_counter/views/views.xml",

        "sh_pos_logo/views/logo_assets.xml",
        "sh_pos_logo/views/pos_config_settings.xml",

        'sh_pos_bag_charges/views/pos_config.xml',
        'sh_pos_bag_charges/views/assets.xml',

        'sh_pos_default_invoice/views/pos_config_setting.xml',
        'sh_pos_default_invoice/views/sh_pos_default_invoice_apply.xml',

        'sh_pos_receipt_extend/views/pos_config_settings.xml',
        'sh_pos_receipt_extend/views/sh_pos_receipt_extend.xml',

        'sh_pos_default_customer/views/pos_config_settings.xml',
        'sh_pos_default_customer/views/default_customer_assets.xml',

        'sh_pos_remove_cart_item/views/remove_cart_pos_config_settings.xml',
        'sh_pos_remove_cart_item/views/sh_pos_remove_cart_item.xml',

        'sh_pos_wh_stock/views/pos_config_settings.xml',
        'sh_pos_wh_stock/views/assets.xml',

        'sh_pos_auto_lock/views/pos_config_settings.xml',
        'sh_pos_auto_lock/views/assets.xml',

        'sh_pos_product_creation/views/pos_config.xml',
        'sh_pos_product_creation/views/assets.xml',

        'sh_pos_rounding/views/pos_config_settings.xml',
        'sh_pos_rounding/views/assets.xml',

        "sh_pos_whatsapp_integration/views/res_users_inherit_view.xml",
        "sh_pos_whatsapp_integration/views/views.xml",
        "sh_pos_whatsapp_integration/views/templates.xml",

        "pos_product_suggestion/views/pos_product_suggestion_config.xml",
        "pos_product_suggestion/views/product_view.xml",

        'sh_pos_order_list/views/pos_config.xml',
        'sh_pos_order_list/views/sh_pos_order_list.xml',

        'sh_pos_order_discount/views/pos_custom_view.xml',
        'sh_pos_order_discount/views/pos_config_setting.xml',

        'sh_pos_direct_login/views/res_users_view.xml',
        'sh_pos_direct_login/views/sh_pos_direct_login.xml',

        'sh_pos_access_rights/views/assets.xml',

        'sh_pos_fronted_cancel/views/sh_pos_fronted_cancel.xml',

        'sh_pos_customer_order_history/views/pos_config_settings.xml',
        'sh_pos_customer_order_history/views/sh_pos_customer_order_history.xml',

        'sh_pos_multi_barcode/views/sh_pos_multi_barcode.xml',

        'sh_pos_order_return_exchange/views/pos_config.xml',
        'sh_pos_order_return_exchange/views/product_template.xml',
        'sh_pos_order_return_exchange/views/sh_pos_order_return_exchange.xml',

        'sh_pos_order_return_exchange_barcode/views/sh_pos_order_return_exchange_barcode.xml',

        'sh_pos_order_signature/views/pos_config_settings.xml',
        'sh_pos_order_signature/views/pos_order_view.xml',
        'sh_pos_order_signature/views/sh_pos_order_signature.xml',

        'sh_pos_receipt/views/pos_view.xml',
        'sh_pos_line_pricelist/views/pos_config.xml',
        'sh_pos_line_pricelist/views/sh_pos_line_pricelist.xml',
        'sh_pos_product_bundle/views/templates.xml',
        'sh_pos_product_bundle/views/views.xml',
        'sh_base_bundle/views/sh_product_view.xml',
        'sh_pos_switch_view/views/pos_view.xml',
        'sh_pos_switch_view/views/assets.xml',

        'sh_product_multi_barcode/views/res_config_settings.xml',
        'sh_product_multi_barcode/views/product_view.xml',

        "sh_pos_chatter/views/pos_order_view.xml",

        "sh_auto_validate_pos/views/log_track_view.xml",
        "sh_auto_validate_pos/security/ir.model.access.csv",
        "sh_auto_validate_pos/data/cron_view.xml",

        "sh_mass_product_update_pos/security/ir.model.access.csv",
        "sh_mass_product_update_pos/wizards/mass_product_update_pos_view.xml",

        'sh_pos_customer_discount/views/assets.xml',
        'sh_pos_customer_discount/views/pos_config.xml',

        'sh_pos_discount/security/ir.model.access.csv',
        'sh_pos_discount/views/pos_discount_menu.xml',
        'sh_pos_discount/views/pos_discount.xml',

        'sh_pos_multiples_qty/views/multi_product_qty.xml',
        'sh_pos_multiples_qty/views/multi_qty_assets.xml',

        'sh_pos_own_customers/views/sales_person.xml',
        'sh_pos_own_customers/views/assets.xml',

        'sh_pos_own_products/views/assets.xml',
        'sh_pos_own_products/views/pos_config.xml',

        'sh_pos_quick_print_receipt/views/pos_config.xml',
        'sh_pos_quick_print_receipt/views/sh_pos_quick_print_receipt.xml',

        "security/mass_tag_update_rights.xml",
        "sh_product_tags/security/ir.model.access.csv",
        "sh_product_tags/views/product_tag.xml",
        "sh_product_tags/views/product_tmpl.xml",
        "sh_product_tags/views/mass_tag_update_wizard_view.xml",
        "sh_product_tags/views/mass_tag_update_action.xml",

        'sh_pos_tags/views/assets.xml',
        'sh_pos_tags/views/pos.xml',

        "sh_message/security/ir.model.access.csv",
        "sh_message/wizard/sh_message_wizard.xml",

        'security/import_pos_security.xml',
        'sh_import_pos/security/ir.model.access.csv',
        'sh_import_pos/wizard/import_pos_wizard.xml',
        'sh_import_pos/views/pos_view.xml',

        'sh_pos_categories_merge/security/ir.model.access.csv',
        'sh_pos_categories_merge/views/pos_config_settings.xml',
        'sh_pos_categories_merge/views/view.xml',
        'sh_pos_categories_merge/wizard/merge_category_wizard_view.xml',

        'sh_pos_order_label/data/data.xml',
        'sh_pos_order_label/views/assets.xml',
        'sh_pos_order_label/views/pos_order.xml',
        'sh_pos_order_label/views/pos_config.xml',

        "sh_product_secondary/views/sh_product_custom.xml",
        "sh_product_secondary/views/sh_product_template_custom.xml",

        "sh_pos_secondary/views/templates.xml",
        "sh_pos_secondary/views/views.xml",

        'sh_pos_weight/views/assets.xml',
        'sh_pos_weight/views/pos_config.xml',

        "sh_base_uom_qty_pack/views/sh_product_template_custom.xml",

        'sh_pos_product_code/views/pos_view.xml',

        'sh_pos_product_qty_pack/views/assets.xml',
        'sh_pos_product_qty_pack/views/product.xml',

        'sh_pos_cash_in_out/views/cash_in_out_menu.xml',
        'sh_pos_cash_in_out/views/pos_config_settings.xml',
        'sh_pos_cash_in_out/views/sh_pos_cash_in_out.xml',

        'sh_pos_product_template/views/pos_template_product.xml',
        'sh_pos_product_template/views/pos_custom.xml',
    ],
    "qweb": [
        "static/sh_pos_loyalty/static/src/xml/pos.xml",
        "static/sh_pos_order_list/static/src/xml/action_button.xml",
        "static/sh_pos_order_list/static/src/xml/screen.xml",
        "static/sh_pos_note/static/src/xml/*.xml",
        "static/sh_pos_rounding/static/src/xml/pos.xml",
        "static/sh_pos_keyboard_shortcut/static/src/xml/action_button.xml",
        "static/sh_pos_keyboard_shortcut/static/src/xml/popup.xml",
        "static/pos_product_suggestion/static/src/xml/*.xml",
        "static/sh_pos_theme_responsive/static/src/xml/pos.xml",
        "static/sh_pos_theme_responsive/static/src/xml/orderline.xml",
        "static/sh_pos_theme_responsive/static/src/xml/action_pad_widget.xml",
        "static/sh_pos_theme_responsive/static/src/xml/client_list_screen.xml",
        "static/sh_pos_theme_responsive/static/src/xml/client_line.xml",
        "static/sh_pos_theme_responsive/static/src/xml/ticket_screen.xml",
        "static/sh_pos_theme_responsive/static/src/xml/payment_screen.xml",
        "static/sh_pos_theme_responsive/static/src/xml/client_details_edit.xml",
        "static/sh_pos_theme_responsive/static/src/xml/receipt_screen.xml",
        "static/sh_pos_theme_responsive/static/src/xml/mobile_order_widget.xml",
        "static/sh_pos_theme_responsive/static/src/xml/order_summary.xml",
        "static/sh_pos_theme_responsive/static/src/xml/chrome.xml",
        "static/sh_pos_theme_responsive/static/src/xml/product_widget_control_panel.xml",
        "static/sh_pos_theme_responsive/static/src/xml/cash_opening.xml",
        "static/sh_pos_theme_responsive/static/src/xml/order_management.xml",
        "static/sh_pos_counter/static/src/xml/sh_pos_template.xml",
        "static/sh_pos_logo/static/src/xml/pos.xml",
        "static/sh_pos_bag_charges/static/src/xml/bag_charges.xml",
        "static/sh_pos_receipt_extend/static/src/xml/pos.xml",

        "static/sh_pos_remove_cart_item/static/src/xml/action_button.xml",

        "static/sh_pos_discount/static/src/xml/pos.xml",

        "static/sh_pos_wh_stock/static/src/xml/pos.xml",

        "static/sh_pos_product_creation/static/src/xml/product_button.xml",
        "static/sh_pos_product_creation/static/src/xml/product_popup.xml",

        "static/sh_pos_whadtsapp_integration/static/src/xml/pos.xml",

        "static/sh_pos_order_discount/static/src/xml/action_button.xml",
        "static/sh_pos_order_discount/static/src/xml/popup.xml",
        "static/sh_pos_order_discount/static/src/xml/pos_custom_view.xml",


        "static/sh_pos_customer_order_history/static/src/xml/pos.xml",

        "static/sh_pos_whatsapp_integration/static/src/xml/pos.xml",

        "static/sh_pos_order_return_exchange/static/src/xml/popup.xml",

        "static/sh_pos_order_return_exchange/static/src/xml/screen.xml",

        "static/sh_pos_order_return_exchange_barcode/static/src/xml/popup.xml",

        "static/sh_pos_order_signature/static/src/xml/action_button.xml",
        "static/sh_pos_order_signature/static/src/xml/popup.xml",
        "static/sh_pos_order_signature/static/src/xml/receipt.xml",

        "static/sh_pos_line_pricelist/static/src/xml/popup.xml",
        "static/sh_pos_product_bundle/static/src/xml/pos.xml",
        "static/sh_pos_switch_view/static/src/xml/pos.xml",

        "static/sh_pos_customer_discount/static/src/xml/pos.xml",

        'static/sh_pos_quick_print_receipt/static/src/xml/action_button.xml',

        'static/sh_pos_order_label/static/src/xml/pos.xml',

        'static/sh_pos_weight/static/src/xml/pos.xml',

        'static/sh_pos_secondary/static/src/xml/pos.xml',

        'static/sh_pos_product_qty_pack/static/src/xml/product.xml',

        'static/sh_pos_cash_in_out/static/src/xml/*.xml',

        "static/sh_pos_product_template/static/src/xml/*.xml",

    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 214,
    "currency": "EUR",
}
