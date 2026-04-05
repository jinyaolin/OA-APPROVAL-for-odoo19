# -*- coding: utf-8 -*-
from odoo import api, fields, models
import json


class OaFormFieldValue(models.Model):
    """表單欄位值"""
    _name = 'oa.form.field.value'
    _description = '表單欄位值'
    _order = 'instance_id, field_id'

    instance_id = fields.Many2one('oa.form.instance', '表單執行個體', required=True, ondelete='cascade')
    field_id = fields.Many2one('oa.form.field', '欄位', required=True, ondelete='restrict')

    # 顯示欄位名稱（使用翻譯後的名稱）
    def _compute_display_name(self):
        """計算翻譯後的欄位名稱"""
        for record in self:
            if record.field_id and record.field_id.name:
                # 解析翻譯字典格式 {"en_US": "名稱"}
                try:
                    name_dict = json.loads(record.field_id.name)
                    if isinstance(name_dict, dict):
                        # 優先使用中文，其次英文
                        record.field_display_name = name_dict.get('zh_TW') or name_dict.get('en_US') or record.field_id.name
                    else:
                        record.field_display_name = record.field_id.name
                except:
                    record.field_display_name = record.field_id.name
            else:
                record.field_display_name = ''

    field_display_name = fields.Char(compute='_compute_display_name', string='欄位名稱')

    # 顯示欄位名稱（直接使用相關欄位）
    field_name = fields.Char(related='field_id.name', string='欄位名稱', readonly=True)
    field_type = fields.Selection(related='field_id.field_type', string='欄位類型', readonly=True)

    # 統一的顯示值
    display_value = fields.Char('欄位值', compute='_compute_display_value', store=False)

    @api.depends('field_type', 'value_char', 'value_text', 'value_integer',
                 'value_float', 'value_date', 'value_datetime',
                 'value_employee_id', 'value_department_id', 'value_filename')
    def _compute_display_value(self):
        """計算顯示值，根據欄位類型返回對應的值"""
        for record in self:
            if not record.field_type:
                record.display_value = ''
                continue

            if record.field_type == 'char':
                record.display_value = record.value_char or ''
            elif record.field_type == 'selection':
                record.display_value = record.value_char or ''
            elif record.field_type == 'text':
                record.display_value = record.value_text or ''
            elif record.field_type == 'integer':
                record.display_value = str(record.value_integer) if record.value_integer is not None else ''
            elif record.field_type == 'float':
                record.display_value = str(record.value_float) if record.value_float is not None else ''
            elif record.field_type == 'date':
                record.display_value = str(record.value_date) if record.value_date else ''
            elif record.field_type == 'datetime':
                record.display_value = str(record.value_datetime) if record.value_datetime else ''
            elif record.field_type == 'employee':
                record.display_value = record.value_employee_id.name if record.value_employee_id else ''
            elif record.field_type == 'department':
                record.display_value = record.value_department_id.name if record.value_department_id else ''
            elif record.field_type == 'file':
                record.display_value = record.value_filename or ''
            else:
                record.display_value = ''


    # 便利方法：取得選項列表
    def get_selection_options(self):
        """取得 selection 選項列表"""
        if self.field_id.field_type == 'selection' and self.field_id.selection_options:
            # 解析選項字串（格式：key1:值1;key2:值2）
            options = self.field_id.selection_options.split(';') if self.field_id.selection_options else []
            return [(opt.split(':')[0], opt.split(':')[1]) if ':' in opt else (opt, opt) for opt in options]
        return []

    # 顯示可用的選項列表（用於提示和驗證）
    @api.depends('field_id.selection_options')
    def _compute_available_options(self):
        """計算可用的選項列表"""
        for record in self:
            if record.field_id.field_type == 'selection' and record.field_id.selection_options:
                # 解析選項字串（格式：選項1,選項2,選項3）
                options = record.field_id.selection_options.split(',') if record.field_id.selection_options else []
                # 顯示為逗號分隔的字串
                record.available_options = ', '.join([opt.strip() for opt in options])
            else:
                record.available_options = ''

    available_options = fields.Char('可用選項', compute='_compute_available_options', store=False)

    # Selection 選項（用於下拉選單）
    value_selection_option_id = fields.Many2one('oa.form.selection.option', '選項')

    @api.onchange('field_id')
    def _onchange_field_id(self):
        """當欄位改變時，清空選擇的選項"""
        if self.field_id and self.field_id.field_type != 'selection':
            self.value_selection_option_id = False

    def write(self, vals):
        """重寫 write 方法，當更新選項時自動更新 value_char"""
        # 如果更新了 value_selection_option_id，同時更新 value_char
        if 'value_selection_option_id' in vals and vals['value_selection_option_id']:
            option = self.env['oa.form.selection.option'].browse(vals['value_selection_option_id'])
            if option.exists():
                vals['value_char'] = option.name

        return super(OaFormFieldValue, self).write(vals)

    @api.onchange('value_selection_option_id')
    def _onchange_value_selection_option_id(self):
        """當選擇選項時，自動更新 value_char"""
        if self.value_selection_option_id:
            self.value_char = self.value_selection_option_id.name

    @api.onchange('value_char')
    def _onchange_value_char(self):
        """當輸入文字時，如果是 selection 類型，自動更新選項"""
        if self.field_type == 'selection' and self.value_char:
            # 查找對應的選項記錄
            option = self.env['oa.form.selection.option'].search([
                ('field_id', '=', self.field_id.id),
                ('name', '=', self.value_char)
            ], limit=1)
            self.value_selection_option_id = option.id if option else False

            # 驗證是否在可用選項中
            if self.field_id.selection_options:
                options = [opt.strip() for opt in self.field_id.selection_options.split(',') if opt.strip()]
                if self.value_char not in options:
                    return {
                        'warning': {
                            'title': '無效的選項',
                            'message': f'請從以下選項中選擇：{", ".join(options)}'
                        }
                    }
    def _onchange_value_char(self):
        """當輸入文字時，如果是 selection 類型，驗證是否在可用選項中"""
        if self.field_type == 'selection' and self.value_char:
            if self.field_id.selection_options:
                options = [opt.strip() for opt in self.field_id.selection_options.split(',') if opt.strip()]
                if self.value_char not in options:
                    return {
                        'warning': {
                            'title': '無效的選項',
                            'message': f'請從以下選項中選擇：{", ".join(options)}'
                        }
                    }

    # 各種類型的值
    value_char = fields.Char('文字值')
    value_text = fields.Text('多行文字值')
    value_integer = fields.Integer('整數值')
    value_float = fields.Float('小數值')
    value_date = fields.Date('日期值')
    value_datetime = fields.Datetime('日期時間值')
    value_file = fields.Binary('附件值')
    value_filename = fields.Char('附件名稱')

    # 關聯欄位的值
    value_employee_id = fields.Many2one('hr.employee', '員工')
    value_department_id = fields.Many2one('hr.department', '部門')
