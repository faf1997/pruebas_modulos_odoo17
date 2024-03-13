# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CreditCardCouponReconcile(models.Model):
    _name = "credit.card.coupon.reconcile"
    _description = "Liquidación de Cupones de Tarjetas de Crédito"

    name = fields.Char(
        string="Número de liquidación",
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner bancario",
        required=True
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Diario",
        domain="[('type','in',('cash', 'bank'))]",
        required=True,
    )
    currency_id = fields.Many2one(
        related='journal_id.currency_id',
        string="Moneda",
        store=True
    )
    company_id = fields.Many2one(
        related='journal_id.company_id',
        string='Compañía',
        store=True
    )
    credit_card_coupon_ids = fields.One2many(
        comodel_name='credit.card.coupon',
        inverse_name='credit_card_coupon_reconcile_id',
        string="Cupones"
    )
    state = fields.Selection(
        [('draft','Borrador'),
        ('to_confirm', 'Para validar'),
        ('done','Validada')],
        string="Estado",
        default='draft',
        required=True,
        readonly=True
    )
    acreditation_date = fields.Date(
        string="Fecha de acreditación",
        required=True
    )
    origin = fields.Char(
        string="Documento de origen"
    )
    coupons_total = fields.Monetary(
        string="Total de cupones",
        compute='_get_coupons_total',
        currency_field='currency_id',
        store=True
    )
    credited_total = fields.Monetary(
        string='Total a cobrar',
        currency_field='currency_id',
        compute='_get_credited_total',
        store=True
    )
    customer_multiple_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de pago múltiple',
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '=', 'document_book')]",
        help="Diario utilizado en el pago de cliente generado",
        default=lambda self: self._get_default_multiple_journal_id(),
        check_company=True
    )
    supplier_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de pago',
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '!=', 'document_book')]",
        help="Diario utilizado en el pago de proveedor generado",
        default=lambda self: self._get_default_supplier_journal_id(),
        check_company=True
    )
    receivable_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Método de pago',
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '=', 'payment_type')]",
        help="Diario utilizado como método de pago del pago de cliente generado",
        default=lambda self: self._get_default_receivable_journal_id(),
        check_company=True
    )
    sale_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de ventas',
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),('type', '=', 'sale')]",
        default=lambda self: self._get_default_move_journal_id(type='sale'),
        check_company=True
    )
    purchase_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de compras',
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),('type', '=', 'purchase')]",
        default=lambda self: self._get_default_move_journal_id(type='purchase'),
        check_company=True
    )
    discount_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto "descuentos ganados"',
        default=lambda self: self._get_default_discount_product_id()
    )
    coupons_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de cupones',
        default=lambda self: self._get_default_coupons_account_id()
    )
    in_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string="Factura de proveedor",
        ondelete='set null',
        readonly=True
    )
    supplier_payment_id = fields.Many2one(
        comodel_name='account.payment',
        string="Pago de proveedor",
        ondelete='set null',
        readonly=True
    )
    out_receipt_id = fields.Many2one(
        comodel_name='account.move',
        string="Recibo de venta",
        ondelete='set null',
        readonly=True
    )
    customer_payment_id = fields.Many2one(
        comodel_name='account.payment',
        string="Pago de cliente",
        ondelete='set null',
        readonly=True
    )
    tax_line_ids =  fields.One2many(
        comodel_name='credit.card.coupon.reconcile.tax.line',
        inverse_name='credit_card_coupon_reconcile_id',
        string="Gastos bancarios"
    )
    perception_line_ids =  fields.One2many(
        comodel_name='credit.card.coupon.reconcile.perception.line',
        inverse_name='credit_card_coupon_reconcile_id',
        string="Percepciones"
    )
    retention_line_ids =  fields.One2many(
        comodel_name='credit.card.coupon.reconcile.retention.line',
        inverse_name='credit_card_coupon_reconcile_id',
        string="Retenciones"
    )
    document_to_create = fields.Boolean(compute="compute_document_to_create")

    _sql_constraints = [('unique_name', 'unique(name,company_id)', 'Ya existe una liquidación con el mismo número.')]

    @api.onchange('company_id')
    def onchange_company_id(self):
        # Quito todos los valores dependientes de la compañía cuando esta cambia
        vals = dict((key, False) for key in self.get_documents_data_fields())
        self.update(vals)
        lines = self.get_tax_lines_fields()
        lines.extend(self.get_retention_lines_fields())
        for line in lines:
            getattr(self, line).unlink()

    def compute_document_to_create(self):
        for reconcile in self:
            if any(not getattr(reconcile, field) for field in reconcile.get_documents_fields()):
                reconcile.document_to_create = True
            else:
                reconcile.document_to_create = False

    def _get_default_discount_product_id(self):
        return self.env['res.company'].browse(self._context.get('force_company', self.env.company.id)).credit_card_coupon_reconcile_discount_product_id

    def _get_default_coupons_account_id(self):
        return self.env['res.company'].browse(self._context.get('force_company', self.env.company.id)).credit_card_coupon_reconcile_coupons_account_id

    def _get_default_supplier_journal_id(self):
        return self.env['res.company'].browse(self._context.get('force_company', self.env.company.id)).credit_card_coupon_reconcile_supplier_journal_id

    def _get_default_receivable_journal_id(self):
        return self.env['res.company'].browse(self._context.get('force_company', self.env.company.id)).credit_card_coupon_reconcile_receivable_journal_id

    def _get_default_multiple_journal_id(self):
        return self.env['account.journal'].search([('payment_usage', '=', 'document_book'), ('company_id', '=', self.env.company.id), ('company_id', '=', self.env.company.id)], limit=1)

    def _get_default_move_journal_id(self, type):
        company_id = self._context.get('force_company', self.env.company.id)
        domain = [('company_id', '=', company_id), ('type', '=', type)]
        journal = self.env['account.journal'].search(domain, limit=1)
        return journal

    @api.depends('credit_card_coupon_ids', 'currency_id')
    def _get_coupons_total(self):
        for reconcile in self:
            reconcile.coupons_total = sum(coupon.amount_reconcile_currency for coupon in reconcile.credit_card_coupon_ids)

    def get_documents_fields(self):
        return ['in_invoice_id', 'out_receipt_id', 'supplier_payment_id', 'customer_payment_id']

    def get_documents_data_fields(self):
        return ['customer_multiple_journal_id','supplier_journal_id','receivable_journal_id',
        'sale_journal_id', 'purchase_journal_id', 'discount_product_id', 'coupons_account_id']

    def get_tax_lines_fields(self):
        return ['tax_line_ids','perception_line_ids']

    def get_retention_lines_fields(self):
        return ['retention_line_ids']

    def get_tax_lines_amounts(self):
        amounts = []
        for line in self.get_tax_lines_fields():
            amounts.extend(getattr(self, line).mapped(lambda l: (l.base if hasattr(l, 'base') else 0) + l.amount))
        return amounts

    def get_retention_lines_amounts(self):
        amounts = []
        for line in self.get_retention_lines_fields():
            amounts.extend(getattr(self, line).mapped(lambda l: l.amount))
        return amounts

    @api.depends('coupons_total', 'tax_line_ids', 'tax_line_ids.base', 'tax_line_ids.amount', 'perception_line_ids',
    'perception_line_ids.amount', 'retention_line_ids', 'retention_line_ids.amount')
    def _get_credited_total(self):
        for reconcile in self:
            amounts = reconcile.get_tax_lines_amounts()
            amounts.extend(reconcile.get_retention_lines_amounts())
            reconcile.credited_total = reconcile.coupons_total - sum(amounts) if reconcile.coupons_total >= 0 \
                else reconcile.coupons_total + sum(amounts)

    def validate_documents_fields(self):
        for reconcile in self:
            if any(not getattr(reconcile, field) for field in reconcile.get_documents_fields()):
                raise ValidationError("Deben generarse todos los documentos para poder validar la liquidación.")

    def action_confirm(self):
        self.ensure_one()
        if self.state != 'to_confirm':
            raise ValidationError("La liquidación debe estar en estado 'A validar' para validar sus documentos.")
        self.validate_documents_fields()
        documents = self.get_documents_fields()
        for document in documents:
            getattr(self, document).action_post()
        self.credit_card_coupon_ids.write({'state': 'settled'})
        self.write({'state': 'done'})

    def unlink(self):
        for reconcile in self:
            if reconcile.state != 'draft':
                raise ValidationError("No se puede borrar una liquidación a validar o validada.")
            closed_coupon_ids = reconcile.credit_card_coupon_ids.filtered(lambda x: x.closure_date)
            approved_coupon_ids = reconcile.credit_card_coupon_ids - closed_coupon_ids
            closed_coupon_ids.write({'state': 'closed'})
            approved_coupon_ids.write({'state': 'approved'})
        return super(CreditCardCouponReconcile, self).unlink()

    def action_unlink_documents(self):
        self.ensure_one()
        if self.state != 'to_confirm':
            raise ValidationError("La liquidación debe estar en estado 'A validar' para eliminar sus documentos.")
        documents = self.get_documents_fields()
        # Recorro la lista de documentos en sentido inverso
        # para asegurarme de eliminar primero los pagos
        # ya que estos tienen relación a las facturas
        for document in documents[::-1]:
            getattr(self, document).unlink()
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.ensure_one()
        if self.state != 'done':
            raise ValidationError("La liquidación debe estar validada para ser cancelada.")
        # Anulo la liquidación de los cupones, pasándolos a cerrado o aprobado según corresponda
        closed_coupon_ids = self.credit_card_coupon_ids.filtered(lambda x: x.closure_date)
        approved_coupon_ids = self.credit_card_coupon_ids - closed_coupon_ids
        closed_coupon_ids.write({'state': 'closed'})
        approved_coupon_ids.write({'state': 'approved'})
        # Para cada uno de los documentos asociados me fijo si está cancelado y lo desvinculo de la liquidación
        for document in self.get_documents_fields():
            if getattr(self, document).state not in ('cancel', 'cancelled'):
                raise ValidationError("Para cancelar una liquidación debe primero cancelar sus documentos.")
            setattr(self, document, False)
        self.write({'state': 'draft'})

    def validate_tax_lines(self):
        if any(not reconcile.tax_line_ids for reconcile in self):
            raise ValidationError("Debe completar la grilla de 'Gastos bancarios' de la página 'Datos fiscales'.")

    def validate_documents_data_fields(self):
        for reconcile in self:
            if any(not getattr(reconcile, field) for field in reconcile.get_documents_data_fields()):
                raise ValidationError("Debe completar todos los datos de la página 'Datos de documentos'.")

    def action_create_documents(self):
        self.ensure_one()
        if self.state not in ['draft', 'to_confirm']:
            raise ValidationError("La liquidación debe estar en estado 'Borrador' o 'A validar' para crear sus documentos.")
        self.validate_documents_data_fields()
        self.validate_tax_lines()
        self.create_documents()

    def get_in_invoice_perception_vals(self):
        perception_vals = []
        for perception in self.perception_line_ids:
            perception_vals.append((0,0, self.get_perception_vals(perception.perception_id, round(perception.amount,2))))

        return perception_vals

    def get_in_invoice_line_vals(self):
        invoice_line_vals = []
        for tax in self.tax_line_ids:
            name = "BASE {}".format(tax.tax_id.name)
            invoice_line_vals.append((0,0, self.get_invoice_line_vals(name, tax.base,
                                                                    product=self.discount_product_id, tax=tax.tax_id)))
        return invoice_line_vals

    def get_invoice_line_vals(self, name, price_unit, product=None, account=None, tax=None):
        vals = {
            'name': name,
            'price_unit': abs(price_unit),
            'quantity': 1,
        }
        if product:
            vals['product_id'] = product.id
        if account:
            vals['account_id'] = account.id
        if tax:
            vals['tax_ids'] = [(4, tax.id)]
        return vals

    def get_perception_vals(self, perception, amount):
        return {
            'name': perception.name,
            'perception_id': perception.id,
            'amount': abs(amount),
            'jurisdiction': perception.jurisdiction
        }

    def get_move_vals(self, type):
        vals = {
            'voucher_name': self.name,
            'move_type': type,
            'partner_id': self.partner_id.id,
            'invoice_date': self.acreditation_date,
            'date': self.acreditation_date,
        }
        if type == 'in_invoice':
            vals['journal_id'] = self.purchase_journal_id.id
        elif type == 'out_receipt':
            vals['journal_id'] = self.sale_journal_id.id
            vals['ref'] = self.name
        return vals

    def get_customer_payment_retention_vals(self):
        retention_line_vals = []
        for retention in self.retention_line_ids:
            retention_line_vals.append((0,0, self.get_retention_vals(retention.journal_id,
                                                                    retention.retention_id, retention.amount)))
        return retention_line_vals

    def get_retention_vals(self, journal, retention, amount):
        return {
            'journal_id': journal.id,
            'retention_id': retention.id,
            'amount': abs(amount),
            'certificate_no': self.name,
            'jurisdiction': retention.jurisdiction,
            'date': self.acreditation_date
        }

    def get_payment_type_line_vals(self, journal, amount):
        return {
            'name': journal.name,
            'journal_id': journal.id,
            'amount': abs(amount),
        }

    def get_payment_imputation_vals(self, move_line, amount):
        return {
            'move_line_id': move_line.id,
            'amount': abs(amount),
            'concile': True
        }

    def get_payment_vals(self, type, journal_id, amount):
        vals = {
            'journal_id': journal_id.id,
            'partner_id': self.partner_id.id,
            'payment_type': type,
            'amount': abs(amount),
            'date': self.acreditation_date,
            'ref': self.name,
            'payment_method_id': journal_id.inbound_payment_method_line_ids[0].payment_method_id.id
        }
        if type == 'outbound':
            vals['partner_type'] = 'supplier'
        elif type == 'inbound':
            vals['partner_type'] = 'customer'
        return vals

    def create_documents(self):
        account_move_proxy = self.env['account.move']
        account_payment_proxy = self.env['account.payment']

        for each in self:

            supplier_voucher_amount = sum(each.get_tax_lines_amounts())
            retention_total = sum(each.get_retention_lines_amounts())

            # SE COMPLETAN Y CREAN LOS COMPROBANTES
            if not each.in_invoice_id:
                in_invoice_vals = each.get_move_vals('in_invoice')
                if each.credited_total < 0:
                    in_invoice_vals['move_type'] = 'in_refund'
                in_invoice = account_move_proxy.with_context(force_company=each.company_id.id).create(in_invoice_vals)
                in_invoice._onchange_partner_id()
                in_invoice.write({'invoice_line_ids': each.get_in_invoice_line_vals(),
                                  'perception_ids': each.get_in_invoice_perception_vals()})
                # Ejecuto el onchange de las percepciones para que estas se asignen a las líneas de facturas
                in_invoice.onchange_perception_ids()
                # Escribo la posición fiscal y el tipo de comprobante para asegurarme de que sean de tipo "O"
                in_invoice.write({
                    'fiscal_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_other').id,
                    'voucher_type_id': self.env.ref('l10n_ar_afip_tables.afip_voucher_type_099').id,
                })
                each.in_invoice_id = in_invoice

            if not each.supplier_payment_id:
                if not each.supplier_journal_id.pos_ar_id:
                    raise ValidationError('El diario de pago de proveedor tiene que tener un punto de venta asociado.')
                supplier_payment_vals = self.get_payment_vals('outbound', each.supplier_journal_id, round(supplier_voucher_amount, 4))
                if each.credited_total < 0:
                    supplier_payment_vals['payment_type'] = 'inbound'
                move_line = each.in_invoice_id.line_ids.filtered(lambda aml: aml.account_id.user_type_id.type == 'payable')[0]
                supplier_payment_vals['payment_imputation_ids'] = [(0,0, self.get_payment_imputation_vals(move_line, round(supplier_voucher_amount, 4)))]
                supplier_payment = account_payment_proxy.with_context(force_company=each.company_id.id).create(supplier_payment_vals)
                each.supplier_payment_id = supplier_payment

            if not each.out_receipt_id:
                out_receipt_vals = each.get_move_vals('out_receipt' if each.credited_total >= 0 else 'in_receipt')
                out_receipt_vals['invoice_line_ids'] = [(0,0, each.get_invoice_line_vals('TOTAL CUPONES', each.coupons_total,
                                                                                        account=each.coupons_account_id))]
                out_receipt = account_move_proxy.with_context(force_company=each.company_id.id).create(out_receipt_vals)
                each.out_receipt_id = out_receipt

            if not each.customer_payment_id:
                if not each.customer_multiple_journal_id.pos_ar_id:
                    raise ValidationError('El diario de pago de cliente tiene que tener un punto de venta asociado.')
                customer_payment_vals = self.get_payment_vals('inbound', each.customer_multiple_journal_id, each.coupons_total)
                if each.credited_total < 0:
                    customer_payment_vals['payment_type'] = 'outbound'
                move_line = each.out_receipt_id.line_ids.filtered(lambda aml: aml.account_id.user_type_id.type == ('receivable' if each.credited_total >= 0 else 'payable'))[0]
                customer_payment_vals['payment_imputation_ids'] = [(0,0, self.get_payment_imputation_vals(move_line, each.coupons_total))]
                customer_payment_vals['payment_type_line_ids'] = [(0,0, self.get_payment_type_line_vals(each.receivable_journal_id, abs(each.coupons_total) - retention_total))]
                customer_payment_vals['retention_ids'] = self.get_customer_payment_retention_vals()
                customer_payment = account_payment_proxy.with_context(force_company=each.company_id.id).create(customer_payment_vals)
                # Ejecuto el onchange de las cotizaciones y los montos para que se carguen en los métodos de pago
                for payment_line in customer_payment.payment_type_line_ids:
                    payment_line.onchange_update_rate()
                    payment_line.onchange_amount()
                for retention_line in customer_payment.retention_ids:
                    retention_line.onchange_update_rate()
                    retention_line.onchange_amount()
                each.customer_payment_id = customer_payment

            each.write({'state': 'to_confirm'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
