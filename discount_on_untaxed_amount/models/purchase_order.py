from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.depends('order_line')
    def compute_total_before_discount(self):
        total = 0
        for line in self.order_line:
            total += line.price
        self.total_before_discount = total

    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='amount')
    discount_rate = fields.Float(string='Discount Rate', digits=(16, 3),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default=0.0)
    discount = fields.Monetary(string='Discount', digits=(16, 3), default=0.0,
                               store=True, compute='compute_lines_discount', track_visibility='always')
    total_before_discount = fields.Monetary(string='Total Before Discount', digits=(16, 3), store=True, compute='compute_total_before_discount')

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def set_lines_discount(self):
        if self.discount_type == 'percentage':
            for line in self.order_line:
                line.discount = self.discount_rate
        else:
            total = discount = 0.0
            for line in self.order_line:
                total += (line.product_qty * line.price_unit)
            if self.discount_rate != 0:
                discount = (self.discount_rate / total) * 100
            else:
                discount = self.discount_rate
            for line in self.order_line:
                line.discount = discount

    @api.one
    @api.depends('order_line.price')
    def compute_lines_discount(self):
        discount = 0
        for line in self.order_line:
            discount += line.discount * (line.product_qty * line.price_unit) / 100
        self.discount = discount

    @api.multi
    def button_dummy(self):
        self.set_lines_discount()
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': line.product_qty * line.price_unit - (line.discount * (line.product_qty * line.price_unit) / 100),
            })

    @api.one
    @api.depends('product_qty', 'price_unit', 'discount')
    def compute_line_price(self):
        self.price = self.product_qty * self.price_unit

    discount = fields.Float(string='Discount (%)', digits=(16, 3), default=0.0)
    price = fields.Float(string='Price', digits=(16, 3), store=True, compute='compute_line_price')
