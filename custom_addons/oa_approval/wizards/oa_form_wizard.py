# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class OaFormTemplateSelectWizard(models.TransientModel):
    """表單範本選擇精靈"""
    _name = 'oa.form.template.select.wizard'
    _description = '選擇表單範本'

    category_id = fields.Many2one('oa.form.category', '表單分類', domain="[('active', '=', True)]")
    template_id = fields.Many2one(
        'oa.form.template',
        '表單範本',
        required=True,
        domain="[('state', '=', 'published'), ('category_id', '=', category_id)]",
    )

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """當選擇分類時，清空已選的範本"""
        if self.category_id:
            self.template_id = False

    def action_create_form(self):
        """創建表單執行個體"""
        self.ensure_one()

        if not self.template_id:
            raise UserError('請選擇表單範本！')

        # 創建表單執行個體
        instance = self.env['oa.form.instance'].create({
            'template_id': self.template_id.id,
        })

        # 返回表單視圖
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oa.form.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def action_show_templates(self):
        """顯示該分類下的所有範本"""
        self.ensure_one()

        if not self.category_id:
            raise UserError('請先選擇表單分類！')

        # 返回範本列表視圖
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oa.form.template',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.category_id.id), ('state', '=', 'published')],
            'target': 'new',
            'name': self.category_id.name,
        }


class OaFormFillWizard(models.TransientModel):
    """表單填寫向導"""
    _name = 'oa.form.fill.wizard'
    _description = '填寫表單內容'

    template_id = fields.Many2one('oa.form.template', '表單範本', required=True, readonly=True)
    applicant_id = fields.Many2one('hr.employee', '申請人', required=True,
                                   default=lambda self: self.env.user.employee_id)

    # 動態欄位（支持最多10個欄位）
    field_1_label = fields.Char('欄位1標籤', compute='_compute_field_labels')
    field_1_type = fields.Char('欄位1類型', compute='_compute_field_labels')
    field_1_char = fields.Char('欄位1')
    field_1_selection_id = fields.Many2one('oa.form.selection.option', '選項',
                                           domain="[('field_id', '=', field_1_id)]")
    field_1_id = fields.Many2one('oa.form.field', '欄位1', compute='_compute_field_labels')
    field_1_text = fields.Text('欄位1')
    field_1_integer = fields.Integer('欄位1')
    field_1_float = fields.Float('欄位1')
    field_1_date = fields.Date('欄位1')
    field_1_datetime = fields.Datetime('欄位1')
    field_1_employee_id = fields.Many2one('hr.employee', '欄位1')
    field_1_department_id = fields.Many2one('hr.department', '欄位1')
    field_1_file = fields.Binary('欄位1')
    field_1_filename = fields.Char('文件名')

    field_2_label = fields.Char('欄位2標籤', compute='_compute_field_labels')
    field_2_type = fields.Char('欄位2類型', compute='_compute_field_labels')
    field_2_char = fields.Char('欄位2')
    field_2_selection_id = fields.Many2one('oa.form.selection.option', '選項',
                                           domain="[('field_id', '=', field_2_id)]")
    field_2_id = fields.Many2one('oa.form.field', '欄位2', compute='_compute_field_labels')
    field_2_text = fields.Text('欄位2')
    field_2_integer = fields.Integer('欄位2')
    field_2_float = fields.Float('欄位2')
    field_2_date = fields.Date('欄位2')
    field_2_datetime = fields.Datetime('欄位2')
    field_2_employee_id = fields.Many2one('hr.employee', '欄位2')
    field_2_department_id = fields.Many2one('hr.department', '欄位2')
    field_2_file = fields.Binary('欄位2')
    field_2_filename = fields.Char('文件名')

    field_3_label = fields.Char('欄位3標籤', compute='_compute_field_labels')
    field_3_type = fields.Char('欄位3類型', compute='_compute_field_labels')
    field_3_char = fields.Char('欄位3')
    field_3_selection_id = fields.Many2one('oa.form.selection.option', '選項',
                                           domain="[('field_id', '=', field_3_id)]")
    field_3_id = fields.Many2one('oa.form.field', '欄位3', compute='_compute_field_labels')
    field_3_text = fields.Text('欄位3')
    field_3_integer = fields.Integer('欄位3')
    field_3_float = fields.Float('欄位3')
    field_3_date = fields.Date('欄位3')
    field_3_datetime = fields.Datetime('欄位3')
    field_3_employee_id = fields.Many2one('hr.employee', '欄位3')
    field_3_department_id = fields.Many2one('hr.department', '欄位3')
    field_3_file = fields.Binary('欄位3')
    field_3_filename = fields.Char('文件名')

    field_4_label = fields.Char('欄位4標籤', compute='_compute_field_labels')
    field_4_type = fields.Char('欄位4類型', compute='_compute_field_labels')
    field_4_char = fields.Char('欄位4')
    field_4_selection_id = fields.Many2one('oa.form.selection.option', '選項',
                                           domain="[('field_id', '=', field_4_id)]")
    field_4_id = fields.Many2one('oa.form.field', '欄位4', compute='_compute_field_labels')
    field_4_text = fields.Text('欄位4')
    field_4_integer = fields.Integer('欄位4')
    field_4_float = fields.Float('欄位4')
    field_4_date = fields.Date('欄位4')
    field_4_datetime = fields.Datetime('欄位4')
    field_4_employee_id = fields.Many2one('hr.employee', '欄位4')
    field_4_department_id = fields.Many2one('hr.department', '欄位4')
    field_4_file = fields.Binary('欄位4')
    field_4_filename = fields.Char('文件名')

    field_5_label = fields.Char('欄位5標籤', compute='_compute_field_labels')
    field_5_type = fields.Char('欄位5類型', compute='_compute_field_labels')
    field_5_char = fields.Char('欄位5')
    field_5_selection_id = fields.Many2one('oa.form.selection.option', '選項',
                                           domain="[('field_id', '=', field_5_id)]")
    field_5_id = fields.Many2one('oa.form.field', '欄位5', compute='_compute_field_labels')
    field_5_text = fields.Text('欄位5')
    field_5_integer = fields.Integer('欄位5')
    field_5_float = fields.Float('欄位5')
    field_5_date = fields.Date('欄位5')
    field_5_datetime = fields.Datetime('欄位5')
    field_5_employee_id = fields.Many2one('hr.employee', '欄位5')
    field_5_department_id = fields.Many2one('hr.department', '欄位5')
    field_5_file = fields.Binary('欄位5')
    field_5_filename = fields.Char('文件名')

    @api.depends('template_id')
    def _compute_field_labels(self):
        """計算欄位標籤和類型"""
        for wizard in self:
            if wizard.template_id:
                fields = wizard.template_id.field_ids.sorted('sequence')
                for idx, field in enumerate(fields, 1):
                    if idx <= 5:
                        setattr(wizard, f'field_{idx}_label', field.name)
                        setattr(wizard, f'field_{idx}_type', field.field_type)
                        setattr(wizard, f'field_{idx}_id', field.id)
                    else:
                        break
            else:
                for idx in range(1, 6):
                    setattr(wizard, f'field_{idx}_label', False)
                    setattr(wizard, f'field_{idx}_type', False)
                    setattr(wizard, f'field_{idx}_id', False)

    def action_create_form(self):
        """創建表單"""
        self.ensure_one()

        # 創建表單實例
        instance = self.env['oa.form.instance'].create({
            'template_id': self.template_id.id,
            'applicant_id': self.applicant_id.id,
        })

        # 填充欄位值
        for idx, field in enumerate(self.template_id.field_ids.sorted('sequence'), 1):
            if idx > 5:
                break

            field_value = instance.field_value_ids.filtered(lambda v: v.field_id.id == field.id)
            if not field_value:
                continue

            field_value = field_value[0]
            field_type = field.field_type

            # 根據欄位類型和索引設置值
            if idx == 1:
                value = self._get_field_value(1, field_type)
                filename = self.field_1_filename
            elif idx == 2:
                value = self._get_field_value(2, field_type)
                filename = self.field_2_filename
            elif idx == 3:
                value = self._get_field_value(3, field_type)
                filename = self.field_3_filename
            elif idx == 4:
                value = self._get_field_value(4, field_type)
                filename = self.field_4_filename
            elif idx == 5:
                value = self._get_field_value(5, field_type)
                filename = self.field_5_filename
            else:
                value = None
                filename = None

            # 設置欄位值
            if field_type == 'char':
                field_value.value_char = value
            elif field_type == 'text':
                field_value.value_text = value
            elif field_type == 'integer':
                field_value.value_integer = value
            elif field_type == 'float':
                field_value.value_float = value
            elif field_type == 'date':
                field_value.value_date = value
            elif field_type == 'datetime':
                field_value.value_datetime = value
            elif field_type == 'selection':
                field_value.value_char = value
                # 同時設置選項 ID
                if value:
                    option = self.env['oa.form.selection.option'].search([
                        ('field_id', '=', field.id),
                        ('name', '=', value)
                    ], limit=1)
                    field_value.value_selection_option_id = option.id if option else False
            elif field_type == 'employee':
                field_value.value_employee_id = value
            elif field_type == 'department':
                field_value.value_department_id = value
            elif field_type == 'file':
                field_value.value_file = value
                field_value.value_filename = filename

        # 返回到表單視圖
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oa.form.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_field_value(self, idx, field_type):
        """獲取欄位值"""
        if field_type == 'char':
            return getattr(self, f'field_{idx}_char')
        elif field_type == 'text':
            return getattr(self, f'field_{idx}_text')
        elif field_type == 'integer':
            return getattr(self, f'field_{idx}_integer')
        elif field_type == 'float':
            return getattr(self, f'field_{idx}_float')
        elif field_type == 'date':
            return getattr(self, f'field_{idx}_date')
        elif field_type == 'datetime':
            return getattr(self, f'field_{idx}_datetime')
        elif field_type == 'selection':
            # 從 selection_id 獲取選項值
            selection_id = getattr(self, f'field_{idx}_selection_id')
            return selection_id.name if selection_id else False
        elif field_type == 'employee':
            return getattr(self, f'field_{idx}_employee_id').id
        elif field_type == 'department':
            return getattr(self, f'field_{idx}_department_id').id
        elif field_type == 'file':
            return getattr(self, f'field_{idx}_file')
        return None
