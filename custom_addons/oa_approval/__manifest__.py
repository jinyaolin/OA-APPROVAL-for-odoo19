# -*- coding: utf-8 -*-
{
    'name': 'OA Approval',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Approval',
    'summary': '簡易型 OA 審核系統 (MVP)',
    'description': '表單審核工作流系統 - MVP 版本，包含基本的表單填寫、線性審核鏈、通知功能',
    'author': 'Your Name',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/oa_approval_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        # Data
        'data/oa_approval_sequence.xml',
        'data/oa_approval_data.xml',
        'data/oa_form_selection_option_data.xml',
        'data/oa_approval_admin_access.xml',
        # 'data/oa_approval_mail_template.xml',  # Temporarily disabled

        # Views
        'views/oa_form_category_views.xml',
        'views/oa_form_template_views.xml',
        'views/oa_form_template_user_views.xml',
        'views/oa_form_field_views.xml',
        'views/oa_form_instance_views.xml',
        'views/oa_approval_chain_views.xml',
        'views/oa_approval_menu.xml',

        # Wizards
        'wizards/oa_form_wizard_views.xml',
        'wizards/oa_approval_chain_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oa_approval/static/src/js/oa_form_field_widget.js',
            'oa_approval/static/src/css/oa_approval.css',
        ],
        'web.assets_frontend': [
            'oa_approval/static/src/css/oa_approval.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
