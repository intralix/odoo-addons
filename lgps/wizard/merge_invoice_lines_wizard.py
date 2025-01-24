# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class MergeInvoiceLinesWizard(models.TransientModel):
    _name = "lgps.merge_invoice_lines_wizard"
    _description = _("Merge Invoice Lines Wizard")

    def merge_lines(self):

        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        for r in active_records:
            result = []
            # _logger.warning('Invoice: %s', r)
            #_logger.warning('Status: %s', r.state)
            if r.state == 'draft':
                ordered_items = r.invoice_line_ids.sorted('product_id')
                #_logger.warning('ordered_items: %s', ordered_items)
                size = len(ordered_items)
                for i in range(size):
                    j=i+1
                    #_logger.warning('iteration: %s', i)
                    current_line = ordered_items[i]
                    for line in ordered_items[j:]:
                        #_logger.warning('current_line: %s vs %s', current_line, line)
                        if (
                                current_line.product_id == line.product_id and
                                current_line.name == line.name and
                                current_line.price_unit == line.price_unit
                        ):
                            #_logger.warning('same_line: %s', current_line)
                            current_line.quantity += line.quantity
                            result.append(line.id)
                        # else:
                        #     _logger.warning('Not match line')

                # _logger.warning('result: %s', result)
                records_to_remove = self.env['account.move.line'].browse(result)
                # _logger.warning('records_to_remove: %s', records_to_remove)
                #new_ordered_items = ordered_items - records_to_remove
                total_merged = len(records_to_remove)
                if total_merged > 0:
                    body = str(total_merged) + ' registro(s) han sido agrupado(s) tomando como referencia, servicio, descripción y precio'
                else:
                    body = 'No se encontraron servicios para agrupar tomando como referencia, servicio, descripción y precio'
                # _logger.warning('new_ordered_items: %s', new_ordered_items)
                r.update({
                    'invoice_line_ids': [(fields.Command.unlink(records_to_remove.ids))]
                })

                r.message_post(body=body)
            else:
                raise ValidationError(_('No puedes hacer esta operación en una factura confirmada o cancelada'))
