{
    'name': 'Argentina Auto Configuration',
    'version': '18.0.1.0.0',
    'category': 'Localization',
    'summary': 'Configuración automática de empresa argentina',
    'description': """
        Este módulo configura automáticamente:
        - Una empresa con datos argentinos
        - Localización argentina
        - Moneda ARS
        - Plan contable argentino
    """,
    'author': 'Tu Nombre',
    'depends': ['base', 'account'],
    'data': [
        'data/res_company_data.xml',
        'data/account_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}