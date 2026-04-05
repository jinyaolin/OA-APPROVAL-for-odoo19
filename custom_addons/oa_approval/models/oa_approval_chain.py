# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OaApprovalChain(models.Model):
    """審核鏈"""
    _name = 'oa.approval.chain'
    _description = '審核鏈'
    _order = 'name'

    name = fields.Char('審核鏈名稱', required=True)
    code = fields.Char('代碼', required=True)
    description = fields.Text('說明')
    active = fields.Boolean('啟用', default=True)

    step_ids = fields.One2many('oa.approval.step', 'chain_id', '審核步驟')

    # 統計
    instance_count = fields.Integer('使用次數', compute='_compute_instance_count')

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', '審核鏈代碼必須唯一！'),
    ]

    @api.depends('step_ids')
    def _compute_instance_count(self):
        for chain in self:
            chain.instance_count = self.env['oa.form.instance'].search_count([
                ('approval_chain_id', '=', chain.id),
            ])
