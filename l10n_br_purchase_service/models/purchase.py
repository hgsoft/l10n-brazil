# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_invoice_create(self):
        inv_obj = self.env['account.invoice']
        inv_id = super(PurchaseOrder, self).action_invoice_create()
        for po in self:
            lines_service = []

            for line in po.order_line:
                if line.product_id.fiscal_type == 'service':
                    lines_service.append(line.invoice_lines.id)
            if len(lines_service) > 0:
                inv_data = po._prepare_invoice(po, lines_service)
                inv_data['fiscal_type'] = 'service'
                inv_service_id = inv_obj.create(inv_data)

                inv_service_id.button_compute(set_total=True)
                inv_obj.browse(inv_id).button_compute(set_total=True)

                # Link this new invoice to related purchase order
                po.write({'invoice_ids': [(4, inv_service_id.id)]})

        return inv_id
