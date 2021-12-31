from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from datetime import date, datetime


class Commission_Invoice_Wizard(models.TransientModel):
    _name = "commission.invoice.wizard"

    def create_invoice(self):
        active_ids = self._context.get('active_ids')
        list_of_ids = []
        lab_req_obj = self.env['commission.line']
        account_invoice_obj = self.env['account.move']
        account_invoice_line_obj = self.env['invoice.commission.line']

        ir_property_obj = self.env['ir.property']
        for active_id in active_ids:
            lab_req = lab_req_obj.browse(active_id)
            lab_req.validity_status = 'invoice'
            if not lab_req.is_invoiced:
                sale_journals = self.env['account.journal'].search([('type', '=', 'sale')])
                invoice_vals = {
                'name': self.env['ir.sequence'].next_by_code('medical_app_inv_seq'),
                'invoice_origin': lab_req.partner_id or '',
                'move_type': 'out_invoice',
                'ref': False,
                'partner_id': lab_req.partner_id.id or False,
                'partner_shipping_id':lab_req.partner_id.id,
                'invoice_payment_term_id': False,
                'fiscal_position_id': lab_req.partner_id.property_account_position_id.id,
                'team_id': False,
                'invoice_date': date.today(),
                'company_id':lab_req.partner_id.company_id.id or False ,
                }
                res = account_invoice_obj.create(invoice_vals)

                invoice_line_vals = {
                    'product_id_selected': lab_req.product_id_selected.id ,
                    'qty': lab_req.qty,
                    'commission_value': lab_req.commission_value,
                    'total_commission_per_line': lab_req.total_commission_per_line,
                    'total_commission_order': lab_req.total_commission_order,
                }

                res1 = res.write({'invoice_commission_line_id': ([(0, 0, invoice_line_vals)])})
                list_of_ids.append(res.id)
                if list_of_ids:
                    imd = self.env['ir.model.data']
                    lab_req_obj_brw = lab_req_obj.browse(self._context.get('active_id'))
                    lab_req_obj_brw.write({'is_invoiced': True})
                    action = imd.xmlid_to_object('account.action_move_out_invoice_type')
                    list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
                    form_view_id = imd.xmlid_to_res_id('account.view_move_form')
                    result = {
                        'name': action.name,
                        'help': action.help,
                        'type': action.type,
                        'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                        'target': action.target,
                        'context': action.context,
                        'res_model': action.res_model,

                    }
                    if list_of_ids:
                        result['domain'] = "[('id','in',%s)]" % list_of_ids
            else:
                raise Warning('All ready Invoiced.')
            return result

