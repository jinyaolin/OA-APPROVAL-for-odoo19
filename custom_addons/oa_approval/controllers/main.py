# -*- coding: utf-8 -*-
from odoo import http


class OaApprovalController(http.Controller):
    """OA 審核系統控制器"""

    @http.route('/oa/approval', type='json', auth='user')
    def get_my_pending_count(self):
        """獲取待辦數量"""
        count = self.env['oa.form.instance'].search_count([
            ('state', '=', 'pending'),
            ('approval_chain_id.step_ids.approver_id', '=', self.env.user.employee_id.id),
        ])
        return {'count': count}
