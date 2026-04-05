# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OaApprovalChainViewWizard(models.TransientModel):
    """審核鏈查看精靈"""
    _name = 'oa.approval.chain.view.wizard'
    _description = '查看審核鏈'

    chain_id = fields.Many2one('oa.approval.chain', '審核鏈', required=True, readonly=True)
    name = fields.Char('審核鏈名稱', readonly=True)
    description = fields.Text('說明', readonly=True)

    # 顯示審核步驟的文本信息
    step_summary = fields.Text('審核步驟', compute='_compute_step_summary')

    @api.depends('chain_id')
    def _compute_step_summary(self):
        """計算審核步驟摘要"""
        for wizard in self:
            if wizard.chain_id:
                steps = []
                for step in wizard.chain_id.step_ids.sorted('sequence'):
                    step_info = f"步驟 {step.sequence}: {step.name}"
                    if step.approver_type == 'manager':
                        step_info += " (直屬主管)"
                    elif step.approver_type == 'specific':
                        step_info += f" (指定人員: {step.specific_approver_id.name if step.specific_approver_id else '未設置'})"
                    elif step.approver_type == 'department_head':
                        dept_name = step.department_id.name if step.department_id else '申請人部門'
                        step_info += f" (部門主管: {dept_name})"
                    steps.append(step_info)
                wizard.step_summary = '\n'.join(steps)
            else:
                wizard.step_summary = ''

    def action_close(self):
        """關閉視窗"""
        return {'type': 'ir.actions.act_window_close'}
