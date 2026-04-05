# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OaApprovalStep(models.Model):
    """審核步驟"""
    _name = 'oa.approval.step'
    _description = '審核步驟'
    _order = 'chain_id, sequence'

    chain_id = fields.Many2one('oa.approval.chain', '審核鏈', required=True, ondelete='cascade')
    sequence = fields.Integer('順序', required=True)
    name = fields.Char('步驟名稱', required=True)

    # 審核人類型
    approver_type = fields.Selection([
        ('manager', '直屬主管'),
        ('specific', '指定人員'),
        ('department_head', '部門主管'),
    ], '審核人類型', required=True, default='manager')

    # 審核人配置
    specific_approver_id = fields.Many2one('hr.employee', '指定審核人', required=False)
    department_id = fields.Many2one('hr.department', '部門')

    timeout_hours = fields.Integer('超時時限(小時)', default=72)

    @api.constrains('approver_type', 'specific_approver_id')
    def _check_approver_config(self):
        """驗證審核人配置"""
        for step in self:
            if step.approver_type == 'specific' and not step.specific_approver_id:
                raise ValidationError(_('當審核人類型為「指定人員」時，必須選擇審核人！'))

    def _get_approver(self, instance):
        """
        根據審核步驟配置獲取審核人
        :param instance: oa.form.instance 執行個體
        :return: hr.employee 記錄或空記錄集
        """
        self.ensure_one()

        if self.approver_type == 'manager':
            # 返回申請人的直屬主管
            result = instance.applicant_id.parent_id

        elif self.approver_type == 'specific':
            # 返回指定審核人 - 確保返回空記錄集而不是 None
            result = self.specific_approver_id if self.specific_approver_id else self.env['hr.employee']

        elif self.approver_type == 'department_head':
            # 返回部門主管
            if self.department_id:
                result = self.department_id.manager_id
            else:
                # 如果沒有指定部門，使用申請人部門的主管
                if instance.applicant_id.department_id:
                    result = instance.applicant_id.department_id.manager_id
                else:
                    result = self.env['hr.employee']
        else:
            result = self.env['hr.employee']

        # 確保返回的是記錄集對象（檢查 None 或 False）
        if result is None or result is False:
            result = self.env['hr.employee']

        return result
