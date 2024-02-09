from odoo import fields, models, api,_
import re
import logging
_logger = logging.getLogger(__name__)


class LgpsFailureProduct(models.Model):
    _inherit = 'product.template'

    categories_list_id = fields.Many2one(
        comodel_name="lgps.failures_categories_list",
        string=_("Failure Categories"),
        ondelete="restrict",
        index=True,
    )
