# -*- coding: utf-8 -*-
from odoo import fields, models


class OaApprovalRecord(models.Model):
    """審核記錄"""
    _name = 'oa.approval.record'
    _description = '審核記錄'
    _order = 'create_date desc, id'

    instance_id = fields.Many2one('oa.form.instance', '表單執行個體', required=True, ondelete='cascade')
    step_id = fields.Many2one('oa.approval.step', '審核步驟', required=True, ondelete='restrict')
    approver_id = fields.Many2one('hr.employee', '審核人', required=True)

    action = fields.Selection([
        ('approve', '核准'),
        ('reject', '駁回'),
    ], '動作', required=True)

    comment = fields.Text('審核意見')
    approval_date = fields.Datetime('審核時間', default=fields.Datetime.now())
