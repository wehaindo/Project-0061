# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Weha Supplier Management",
    "summary": "Supplier Management",
    "version": "16.0.1.0.0",
    "category": "Agreement",
    "website": False,
    "author": "WEHA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base", "agreement", "multi_branch_base"],
    "data": [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "views/inherit_res_partner_view.xml",
        "views/res_branch_view.xml",
    ],
}
