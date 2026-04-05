# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """模組安裝後的自動鉤子"""
    # 獲取 OA 管理員群組
    oa_admin_group = env.ref('oa_approval.group_oa_admin', raise_if_not_found=False)
    oa_manager_group = env.ref('oa_approval.group_oa_manager', raise_if_not_found=False)

    if not oa_admin_group:
        return

    # 找到系統管理員群組
    admin_group = env.ref('base.group_system', raise_if_not_found=False)
    if not admin_group:
        return

    # 找到所有在系統管理員群組中的使用者
    admin_users = env['res.users'].search([
        ('groups_id', 'in', admin_group.id)
    ])

    # 將他們加入 OA 群組
    for user in admin_users:
        groups_to_add = []
        current_group_ids = user.groups_id.ids

        if oa_admin_group.id not in current_group_ids:
            groups_to_add.append(oa_admin_group.id)

        if oa_manager_group and oa_manager_group.id not in current_group_ids:
            groups_to_add.append(oa_manager_group.id)

        if groups_to_add:
            user.write({'groups_id': [(4, gid) for gid in groups_to_add]})
