# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class OaFormTemplate(models.Model):
    """表單範本"""
    _name = 'oa.form.template'
    _description = '表單範本'
    _order = 'code, id'

    name = fields.Char('範本名稱', required=True, translate=True)
    code = fields.Char('範本代碼', required=True, copy=False)
    category_id = fields.Many2one('oa.form.category', '表單分類', ondelete='restrict')
    description = fields.Text('說明')
    
    state = fields.Selection([
        ('draft', '草稿'),
        ('published', '已發布'),
    ], '狀態', default='draft', required=True)
    
    approval_chain_id = fields.Many2one('oa.approval.chain', string='審核鏈')
    
    version = fields.Integer('版本', default=1)
    active = fields.Boolean('啟用', default=True)
    
    field_ids = fields.One2many('oa.form.field', 'template_id', '欄位')
    instance_ids = fields.One2many('oa.form.instance', 'template_id', '表單執行個體')
    
    instance_count = fields.Integer('使用次數', compute='_compute_instance_count')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', '範本代碼必須唯一！'),
    ]
    
    @api.depends('instance_ids')
    def _compute_instance_count(self):
        for template in self:
            template.instance_count = len(template.instance_ids)
    
    def action_publish(self):
        self.ensure_one()
        if not self.field_ids:
            raise UserError('請先配置表單欄位！')
        self.write({'state': 'published'})

    def action_create_form(self):
        """從範本創建表單執行個體 - 打開填寫向導"""
        self.ensure_one()

        # 打開填寫表單向導
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oa.form.fill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
            },
        }
