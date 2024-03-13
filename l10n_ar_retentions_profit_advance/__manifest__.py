# -*- coding: utf-8 -*

{
    # Product Info
    'name': 'Custom AR Retentions Profit Advance',
    'version': '15.0.1.4.9',
    'license': 'OPL-1',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'This Module helps you to manage the custom changes of the  AR Retentions Profit Advance',
    
    # Writer
    'author': 'Moogah',
    'maintainer': 'Moogah',
    'website':'https://www.moogah.com/',
    'support':'info@moogah.com',
    
    # Dependencies
    'depends': [
        'l10n_ar_retentions_advance',
        'payment_imputation',
        'account',
    ],
    
    # View
    'data': ['security/ir.model.access.csv',
            'data/ywt_moogah_profit_scales_tables_data.xml',
            'data/retention_rules_profit.xml',
            'views/retention_retention_rule_views.xml',
            'views/ywt_moogah_profit_scales_tables_views.xml'],
    
    # Technical 
    'installable': True,
    'auto_install': False,
    'application': True,
    
}
