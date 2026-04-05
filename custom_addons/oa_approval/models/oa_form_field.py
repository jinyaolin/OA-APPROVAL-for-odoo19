# -*- coding: utf-8 -*-
from odoo import fields, models


class OaFormField(models.Model):
    """表單欄位定義"""
    _name = 'oa.form.field'
    _description = '表單欄位'
    _order = 'template_id, sequence, id'

    template_id = fields.Many2one('oa.form.template', '表單範本', required=True, ondelete='cascade')
    name = fields.Char('欄位標籤', required=True, translate=True)
    code = fields.Char('代碼', required=True, copy=False)
    technical_name = fields.Char('技術名稱', copy=False)

    field_type = fields.Selection([
        ('char', '單行文字'),
        ('text', '多行文字'),
        ('integer', '整數'),
        ('float', '小數'),
        ('date', '日期'),
        ('datetime', '日期時間'),
        ('selection', '下拉選擇'),
        ('employee', '員工'),
        ('department', '部門'),
        ('file', '附件'),
    ], '欄位類型', required=True)

    required = fields.Boolean('必填', default=False)
    default_value = fields.Text('預設值')
    selection_options = fields.Text('選項')
    sequence = fields.Integer('順序', default=10)
    placeholder = fields.Char('占位符')
    help_text = fields.Text('提示文字')
