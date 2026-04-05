# -*- coding: utf-8 -*-
from odoo import fields, models


class OaFormCategory(models.Model):
    """表單分類"""
    _name = 'oa.form.category'
    _description = '表單分類'
    _order = 'sequence, id'

    name = fields.Char('分類名稱', required=True, translate=True)
    code = fields.Char('分類代碼', required=True, copy=False)
    parent_id = fields.Many2one('oa.form.category', '上級分類', ondelete='restrict')
    sequence = fields.Integer('順序', default=10)
    active = fields.Boolean('啟用', default=True)
    description = fields.Text('說明')

    # 新增：顯示該分類下的範本
    template_ids = fields.One2many('oa.form.template', 'category_id', '表單範本')
