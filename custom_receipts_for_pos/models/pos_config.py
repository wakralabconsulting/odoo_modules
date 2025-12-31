from odoo.exceptions import ValidationError
from odoo import fields, models, api, _
from odoo.tools import formatLang, float_is_zero
from datetime import date, datetime, time
from collections import defaultdict, Counter
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import AND
import re

class PosConfig(models.Model):
				"""
								This is an Odoo model for Point of Sale (POS).
								It inherits the 'pos.config' model to add new fields.
				"""
				_inherit = 'pos.config'
				
				receipt_design = fields.Many2one('pos.receipt', string='Receipt Design',
								help='Choose any receipt design')
				design_receipt = fields.Text(related='receipt_design.design_receipt',
								string='Receipt XML')
				logo = fields.Binary(related='company_id.logo', string='Logo',
								readonly=False)
				is_custom_receipt = fields.Boolean(string='Is Custom Receipt',
								help='Indicates the receipt  design is '
								     'custom or not')
				sequence_id=fields.Many2one('ir.sequence',string='Order IDs Sequence')
				seq_no=fields.Integer(related='sequence_id.number_next_actual',string='Sequence NO')
				namm = fields.Integer("VVVVVVVVVV")
				
				def open_ui(self):
								data_p = self.status
								res = super().open_ui()
								if data_p =='inactive':
											self.namm = 0
								
								return res
				def getorder_name(self,dataid=False):
								order={'conf':""}
								print(dataid, "aaaaaaaaaaaaaaaaaaaa")
								if dataid:
												dataid=self.env['pos.config'].sudo().browse(dataid)
												if dataid:
																dataid.namm = dataid.namm+1
																order.update({'conf':str((dataid.namm))})
								return order




class PosOrder(models.Model):
				_inherit = 'pos.order'
				_order="top_customer"
				
				custom_note = fields.Char(string="Custom Reference")
				top_customer = fields.Boolean(related="partner_id.top_customer")
				vendor_id=fields.Many2one('res.partner',string="Vendor")
				get_number = fields.Integer("Total Orders")
				
				
				
				
				
				@api.model
				def search_paid_order_ids(self,config_id,domain,limit,offset):
								"""Search for 'paid' orders that satisfy the given domain, limit and offset."""
								default_domain=[('state','!=','draft'),('state','!=','cancel')]
								if domain==[]:
												real_domain=AND([[['config_id','=',config_id]],default_domain])
								else:
												real_domain=AND([domain,default_domain])
								orders=self.search(real_domain,limit=limit,offset=offset,order='id desc')
								# We clean here the orders that does not have the same currency.
								# As we cannot use currency_id in the domain (because it is not a stored field),
								# we must do it after the search.
								pos_config=self.env['pos.config'].browse(config_id)
								orders=orders.filtered(lambda order:order.currency_id==pos_config.currency_id)
								orderlines=self.env['pos.order.line'].search(
												['|',('refunded_orderline_id.order_id','in',orders.ids),('order_id','in',orders.ids)])
								
								# We will return to the frontend the ids and the date of their last modification
								# so that it can compare to the last time it fetched the orders and can ask to fetch
								# orders that are not up-to-date.
								# The date of their last modification is either the last time one of its orderline has changed,
								# or the last time a refunded orderline related to it has changed.
								orders_info=defaultdict(lambda:datetime.min)
								for orderline in orderlines:
												key_order=orderline.order_id.id if orderline.order_id in orders else orderline.refunded_orderline_id.order_id.id
												if orders_info[key_order]<orderline.write_date:
																orders_info[key_order]=orderline.write_date
								totalCount=self.search_count(real_domain)
								return {'ordersInfo':list(orders_info.items())[::-1],'totalCount':totalCount}
				
				
				@api.model
				def create_from_ui(self,orders,draft=False):
								orders=super().create_from_ui(orders,draft=draft)
								order_ids=self.browse([order['id'] for order in orders])
								for order in order_ids:
												
												plastic = self.env['plastic.free']
												for line in order.lines:
																tag_ids = line.product_id.product_tag_ids.filtered(lambda tag: tag.name == 'empty_bottle')
																if tag_ids:
																				line_dic = {
																								'product_id': line.product_id.id,
																								'price_unit': line.price_unit,
																								'qty': line.qty,
																								'price_subtotal_incl': line.price_subtotal_incl,
																								'price_subtotal': line.price_subtotal,
																								'total_cost': line.total_cost,
																								'discount': line.discount,
																								'full_product_name': line.full_product_name,
																								'name': order.name,
																								'date_order': order.date_order,
																								'sequence_number': order.sequence_number,
																								'user_id': order.user_id.id,
																								'order_id': order.id,
																								'company_id': order.company_id.id,
																								'amount_total': order.amount_total,
																								'amount_paid': order.amount_paid,
																								'partner_id': order.partner_id.id,
																								'session_id': order.session_id.id,
																								'config_id': order.config_id.id,
																				}
																				plastic.create(line_dic)
								return orders
				
				def _export_for_ui(self,order):
								# EXTENDS 'point_of_sale'
								vals=super()._export_for_ui(order)
								vals['custom_note']=order.custom_note
								vals['order_name']=order.name
								return vals
				
				def _order_fields(self,ui_order):
								# EXTENDS 'point_of_sale'
								vals=super()._order_fields(ui_order)
								vals['custom_note']=ui_order.get('custom_note')
								return vals
				
				def _prepare_invoice_vals(self):
								vals = super()._prepare_invoice_vals()
								vals['custom_note'] = self.custom_note
								if self.custom_note:
												vals['ref'] = vals['ref']+'-'+self.custom_note
								return vals


class AccountMove(models.Model):
				_inherit = 'account.move'
				
				custom_note = fields.Char(string="Custom Note")



class PosPayment(models.Model):
				_inherit="pos.payment"
				
				def _create_payment_moves(self,is_reverse=False):
								result=self.env['account.move']
								for payment in self:
												order=payment.pos_order_id
												payment_method=payment.payment_method_id
												if payment_method.type=='pay_later' or float_is_zero(payment.amount,
																precision_rounding=order.currency_id.rounding):
																continue
												accounting_partner=self.env["res.partner"]._find_accounting_partner(payment.partner_id)
												pos_session=order.session_id
												journal=pos_session.config_id.journal_id
												payment_move=self.env['account.move'].with_context(default_journal_id=journal.id).create({
																'journal_id':journal.id,'date':fields.Date.context_today(order,order.date_order),
																'ref':_('Invoice payment for %s (%s) using %s',order.name,order.account_move.name,payment_method.name),
																'pos_payment_ids':payment.ids,})
												result|=payment_move
												if order.custom_note:
																payment_move.ref = payment_move.ref +'_'+ order.custom_note
												payment.write({'account_move_id':payment_move.id})
												amounts=pos_session._update_amounts({'amount':0,'amount_converted':0},{'amount':payment.amount},
																payment.payment_date)
												credit_line_vals=pos_session._credit_amounts({
																'account_id':accounting_partner.with_company(order.company_id).property_account_receivable_id.id,
																# The field being company dependant, we need to make sure the right value is received.
																'partner_id':accounting_partner.id,'move_id':payment_move.id,},amounts['amount'],
																amounts['amount_converted'])
												is_split_transaction=payment.payment_method_id.split_transactions
												if is_split_transaction and is_reverse:
																reversed_move_receivable_account_id=accounting_partner.with_company(
																				order.company_id).property_account_receivable_id.id
												elif is_reverse:
																reversed_move_receivable_account_id=payment.payment_method_id.receivable_account_id.id or self.company_id.account_default_pos_receivable_account_id.id
												else:
																reversed_move_receivable_account_id=self.company_id.account_default_pos_receivable_account_id.id
												debit_line_vals=pos_session._debit_amounts({
																'account_id':reversed_move_receivable_account_id,'move_id':payment_move.id,
																'partner_id':accounting_partner.id if is_split_transaction and is_reverse else False,},
																amounts['amount'],amounts['amount_converted'])
												self.env['account.move.line'].create([credit_line_vals,debit_line_vals])
												payment_move._post()
								return result



class PosPayment(models.Model):
				_inherit="pos.session"
				
				def load_pos_data(self):
								loaded_data={}
								self=self.with_context(loaded_data=loaded_data)
								for model in self._pos_ui_models_to_load():
												loaded_data[model]=self._load_model(model)
								
								partner =  loaded_data['res.partner']
								self._pos_data_process(loaded_data)
								exist=[]
								top =[]
								top_pa = self.env['res.partner'].search([('top_customer', '=', True)])
								if top_pa:
												for line in partner:
																if line['id'] in top_pa.ids:
																				top.append(line)
																else:
																				exist.append(line)
								return loaded_data
				
				
				def _loader_params_res_partner(self):
								result=super()._loader_params_res_partner()
								result['search_params']['fields'].extend(['top_customer'])
								return result


class ResPartner(models.Model):
				_inherit="res.partner"
				
				top_customer = fields.Boolean()


class Plasticfree(models.Model):
				_name="plastic.free"
				
				name=fields.Char(string='Order Ref',required=True,readonly=True,copy=False,default='/')
				last_order_preparation_change=fields.Char(string='Last preparation change',help="Last printed state of the order")
				date_order=fields.Datetime(string='Date',readonly=True,index=True,default=fields.Datetime.now)
				user_id=fields.Many2one(comodel_name='res.users',string='Responsible',
								help="Person who uses the cash register. It can be a reliever, a student or an interim employee.",
								default=lambda self:self.env.uid,)
				amount_tax=fields.Float(string='Taxes',digits=0,readonly=True,)
				amount_total=fields.Float(string='Total',digits=0,readonly=True,)
				amount_paid=fields.Float(string='Paid',digits=0)
				amount_return=fields.Float(string='Returned',digits=0,readonly=True)
				top_customer=fields.Boolean(related="partner_id.top_customer",string="Top Customer")
				
				line_ids=fields.One2many('plastic.free.line','plastic_id',string='Order Lines',copy=True)
				company_id=fields.Many2one('res.company',string='Company',readonly=True,index=True)
				country_code=fields.Char(related='company_id.account_fiscal_country_id.code')
				pricelist_id=fields.Many2one('product.pricelist',string='Pricelist')
				partner_id=fields.Many2one('res.partner',string='Customer',change_default=True,index='btree_not_null')
				sequence_number=fields.Integer(string='Sequence Number',help='A session-unique sequence number for the order',
								default=1)
				order_id=fields.Many2one('pos.order',string='Pos Ref')
				
				session_id=fields.Many2one('pos.session',string='Session',index=True,
								domain="[('state', '=', 'opened')]")
				config_id=fields.Many2one('pos.config',related='session_id.config_id',string="Point of Sale",readonly=False,
								store=True)
				state=fields.Selection(
								[('collected','Collected'),('verify','Verified'),('wash','Washed'),('inventory','Inventory Updated')],'Status',
								readonly=True,copy=False,default='collected',index=True)
				
				product_id=fields.Many2one('product.product',string='Product',domain=[('sale_ok','=',True)],change_default=True)
				price_unit=fields.Float(string='Unit Price',digits=0)
				qty=fields.Float('Quantity',digits='Product Unit of Measure',default=1)
				price_subtotal=fields.Float(string='Subtotal w/o Tax',digits=0,readonly=True)
				price_subtotal_incl=fields.Float(string='Subtotal',digits=0,readonly=True)
				price_extra=fields.Float(string="Price extra")
				total_cost=fields.Float(string='Total cost',digits='Product Price',readonly=True)
				is_total_cost_computed=fields.Boolean(help="Allows to know if the total cost has already been computed or not")
				discount=fields.Float(string='Discount (%)',digits=0,default=0.0)
				tax_ids=fields.Many2many('account.tax',string='Taxes',readonly=True)
				
				full_product_name=fields.Char('Full Product Name')
				customer_note=fields.Char('Customer Note')
				stock_picking_id = fields.Many2one('stock.picking',"Picking")
				
				uuid=fields.Char(string='Uuid',readonly=True,copy=False)
				
				def submit_to_verify(self):
								tag_ids=self.filtered(lambda tag:tag.state != 'collected')
								if tag_ids:
												raise ValidationError("Please select all collected state record to proceed.")
								
								else:
												for data in self:
																data.state='verify'
				
				def submit_to_wash(self):
								tag_ids=self.filtered(lambda tag:tag.state != 'verify')
								if tag_ids:
												raise ValidationError("Please select all verify state record to proceed.")
								
								else:
												for data in self:
																data.state='wash'
				
				
				def submit_to_inventory(self):
								picking= self.env['stock.picking']
								picking_type= self.env['stock.picking.type'].search([('warehouse_id.name', '=', 'Torba Store'),('code', '=', 'internal')],limit=1)
								tag_ids=self.filtered(lambda tag:tag.state != 'wash')
								pick_id=""
								if tag_ids:
												raise ValidationError("Please select all wash state record to proceed.")
								
								else:
												invent_lines = []
												
												
												pick_id = picking.create({
																'picking_type_id': picking_type.id,
																'location_id': picking_type.default_location_src_id.id,
																'location_dest_id': picking_type.default_location_dest_id.id,
												})
												if pick_id:
																for data in self:
																				self.env['stock.move'].create({
																								'product_id':data.product_id.alias_id.id,'product_uom_qty':data.qty,
																								'picking_id': pick_id.id,
																								'name': pick_id.name,'location_id':picking_type.default_location_src_id.id,
																								'location_dest_id':picking_type.default_location_dest_id.id,
																								
																				})
																				data.stock_picking_id=pick_id.id
																				data.state='inventory'
								return {
												'type':  'ir.actions.act_window','name':'Related Record','view_mode':'form','res_model':'stock.picking',
												'res_id':pick_id.id,'target':'current',  # or 'new' to open in a popup
								}
				
				
				
				def button_verify(self):
								self.state='verify'
				
				def button_wash(self):
								self.state='wash'
				
				def button_inventory(self):
								self.state='inventory'


class PlasticFreeLines(models.Model):
				_name= 'plastic.free.line'
				
				product_id=fields.Many2one('product.product',string='Product',domain=[('sale_ok','=',True)],
								change_default=True)
				
				price_unit=fields.Float(string='Unit Price',digits=0)
				qty=fields.Float('Quantity',digits='Product Unit of Measure',default=1)
				price_subtotal=fields.Float(string='Subtotal w/o Tax',digits=0,readonly=True)
				price_subtotal_incl=fields.Float(string='Subtotal',digits=0,readonly=True)
				price_extra=fields.Float(string="Price extra")
				total_cost=fields.Float(string='Total cost',digits='Product Price',readonly=True)
				is_total_cost_computed=fields.Boolean(help="Allows to know if the total cost has already been computed or not")
				discount=fields.Float(string='Discount (%)',digits=0,default=0.0)
				plastic_id=fields.Many2one('plastic.free',string='Plastic Free Ref',ondelete='cascade',index=True)
				order_id=fields.Many2one('pos.order',string='Pos Ref')
				tax_ids=fields.Many2many('account.tax',string='Taxes',readonly=True)
				
				product_uom_id=fields.Many2one('uom.uom',string='Product UoM',related='product_id.uom_id')
				full_product_name=fields.Char('Full Product Name')
				customer_note=fields.Char('Customer Note')
				
				uuid=fields.Char(string='Uuid',readonly=True,copy=False)



class ProductProduct(models.Model):
				_inherit='product.product'
				
				alias_id = fields.Many2one('product.product',"Alias")
				is_published = fields.Boolean()