# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID, models


class OaApprovalAutoAssign(models.AbstractModel):
    """OA Approval 自動權限分配"""
    _name = 'oa.approval.auto.assign'
    _description = 'OA Approval 自動權限分配'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        return records

    def _add_admin_to_oa_groups(self):
        """將系統管理員加入 OA 管理員群組"""
        # 獲取 OA 管理員群組
        oa_admin_group = self.env.ref('oa_approval.group_oa_admin', raise_if_not_found=False)
        oa_manager_group = self.env.ref('oa_approval.group_oa_manager', raise_if_not_found=False)

        if not oa_admin_group:
            return

        # 找到所有系統管理員
        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        if admin_group:
            # 遍歷所有使用者，找到在系統管理員群組中的使用者
            admin_users = self.env['res.users'].search([
                ('groups_id', 'in', admin_group.id)
            ])

            # 將他們加入 OA 管理員和經理群組
            for user in admin_users:
                groups_to_add = [oa_admin_group.id, oa_manager_group.id]
                # 過濾掉已經在的群組
                current_groups = user.groups_id.ids
                for group_id in groups_to_add:
                    if group_id not in current_groups:
                        user.write({'groups_id': [(4, group_id)]})

        return True
