from odoo import fields, models, api,_


class LgpsFailureProduct(models.Model):
    _inherit = 'product.template'

    categories_list_id = fields.Many2one(
        comodel_name="lgps.failures_categories_list",
        string=_("Failure Categories"),
        ondelete="restrict",
        index=True,
    )
