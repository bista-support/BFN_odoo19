{
    "name": "Partner Name Readonly Control",
    "version": "19.0.1.0.0",
    "category": "Partner",
    "summary": "Control name field readonly based on checkbox",
    "description": """
        This module adds a checkbox to control whether the partner name field 
        can be edited. When unchecked, the name field becomes readonly.
    """,
    "author": "MCSC",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_partner_accounting_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
