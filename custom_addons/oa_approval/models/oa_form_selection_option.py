# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OaFormSelectionOption(models.Model):
    """表單選項值（用於下拉選單）"""
    _name = 'oa.form.selection.option'
    _description = '表單選項值'
    _order = 'field_id, sequence, name'

    field_id = fields.Many2one('oa.form.field', '欄位', required=True, ondelete='cascade')
    sequence = fields.Integer('順序', default=10)
    name = fields.Char('選項值', required=True)

    _sql_constraints = [
        ('name_field_unique', 'UNIQUE(field_id, name)', '同一欄位的選項值不能重複'),
    ]
