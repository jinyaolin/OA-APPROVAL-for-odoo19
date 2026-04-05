# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class OaFormInstance(models.Model):
    """表單執行個體"""
    _name = 'oa.form.instance'
    _description = '表單執行個體'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    # 基本資訊
    name = fields.Char('表單編號', readonly=True, copy=False, default='New')
    template_id = fields.Many2one(
        'oa.form.template', '表單範本',
        required=True,
        domain="[('state', '=', 'published')]",
    )
    applicant_id = fields.Many2one(
        'hr.employee', '申請人',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )

    # 狀態
    state = fields.Selection([
        ('draft', '草稿'),
        ('pending', '待審核'),
        ('approved', '已通過'),
        ('rejected', '已駁回'),
    ], '狀態', default='draft', tracking=True)

    # 欄位值（簡化版：使用標準 One2many）
    field_value_ids = fields.One2many('oa.form.field.value', 'instance_id', '欄位值')

    # 審核進度
    current_step = fields.Integer('目前步驟', default=0)
    current_step_name = fields.Char('目前步驟名稱', compute='_compute_current_step_name')
    approval_chain_id = fields.Many2one(related='template_id.approval_chain_id')

    # 時間
    submit_date = fields.Datetime('提交時間', readonly=True, copy=False)
    complete_date = fields.Datetime('完成時間', readonly=True)

    # 審核記錄
    approval_record_ids = fields.One2many('oa.approval.record', 'instance_id', '審核記錄')

    # 動態表單 HTML
    form_html = fields.Html('表單內容', compute='_compute_form_html')

    def _compute_current_step_name(self):
        """計算當前步驟名稱"""
        for instance in self:
            if instance.current_step > 0 and instance.approval_chain_id:
                step = instance.approval_chain_id.step_ids.filtered(
                    lambda s: s.sequence == instance.current_step
                )
                instance.current_step_name = step.name if step else ''
            else:
                instance.current_step_name = ''

    def _compute_form_html(self):
        """動態生成表單 HTML"""
        for instance in self:
            if not instance.template_id:
                instance.form_html = ''
                continue

            # 生成動態表單 HTML
            html = '<div class="oa-form-dynamic">'
            html += '<style>'
            html += '.oa-form-dynamic .form-group { margin-bottom: 16px; }'
            html += '.oa-form-dynamic .form-label { font-weight: bold; margin-bottom: 4px; color: #666; }'
            html += '.oa-form-dynamic .form-field { }'
            html += '.oa-form-dynamic .required-label::after { content: " *"; color: red; }'
            html += '</style>'

            # 按順序顯示欄位
            for field in instance.template_id.field_ids.sorted('sequence'):
                field_value = instance.field_value_ids.filtered(lambda v: v.field_id.id == field.id)
                if not field_value:
                    continue

                field_value = field_value[0]
                required_class = 'required-label' if field.required else ''

                html += f'<div class="form-group" data-field-id="{field.id}">'
                html += f'<div class="form-label {required_class}">{field.name}</div>'
                html += '<div class="form-field">'

                # 根據欄位類型渲染不同的輸入組件
                if field.field_type == 'char':
                    html += f'<input type="text" class="form-control" data-field-name="value_char" value="{field_value.value_char or ""}" placeholder="請輸入{field.name}"/>'

                elif field.field_type == 'text':
                    html += f'<textarea class="form-control" rows="3" data-field-name="value_text" placeholder="請輸入{field.name}">{field_value.value_text or ""}</textarea>'

                elif field.field_type == 'integer':
                    html += f'<input type="number" class="form-control" data-field-name="value_integer" value="{field_value.value_integer or 0}" step="1"/>'

                elif field.field_type == 'float':
                    html += f'<input type="number" class="form-control" data-field-name="value_float" value="{field_value.value_float or 0.0}" step="0.01"/>'

                elif field.field_type == 'date':
                    date_val = field_value.value_date or ''
                    html += f'<input type="date" class="form-control" data-field-name="value_date" value="{date_val}" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}"/>'

                elif field.field_type == 'datetime':
                    dt_val = field_value.value_datetime or ''
                    html += f'<input type="datetime-local" class="form-control" data-field-name="value_datetime" value="{dt_val}" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}"/>'

                elif field.field_type == 'employee':
                    employees = instance.env['hr.employee'].search([])
                    employee_id = field_value.value_employee_id.id if field_value.value_employee_id else ''
                    html += f'<select class="form-control" data-field-name="value_employee_id" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}">'
                    html += '<option value="">請選擇員工</option>'
                    for emp in employees:
                        selected = 'selected' if emp.id == employee_id else ''
                        html += f'<option value="{emp.id}" {selected}>{emp.name}</option>'
                    html += '</select>'

                elif field.field_type == 'department':
                    departments = instance.env['hr.department'].search([])
                    dept_id = field_value.value_department_id.id if field_value.value_department_id else ''
                    html += f'<select class="form-control" data-field-name="value_department_id" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}">'
                    html += '<option value="">請選擇部門</option>'
                    for dept in departments:
                        selected = 'selected' if dept.id == dept_id else ''
                        html += f'<option value="{dept.id}" {selected}>{dept.name}</option>'
                    html += '</select>'

                elif field.field_type == 'selection':
                    options = field.selection_options.split('\n') if field.selection_options else []
                    selected_val = field_value.value_char or ''
                    html += f'<select class="form-control" data-field-name="value_char" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}">'
                    html += '<option value="">請選擇</option>'
                    for opt in options:
                        opt = opt.strip()
                        if opt:
                            selected = 'selected' if opt == selected_val else ''
                            html += f'<option value="{opt}" {selected}>{opt}</option>'
                    html += '</select>'

                elif field.field_type == 'file':
                    if field_value.value_file:
                        html += f'<input type="file" class="form-control" data-field-name="value_file" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}"/>'
                        html += f'<small>已上傳：{field_value.value_filename or "file"}</small>'
                    else:
                        html += f'<input type="file" class="form-control" data-field-name="value_file" data-target-model="oa.form.field.value" data-target-field-id="{field_value.id}"/>'

                html += '</div></div>'

            html += '</div>'

            # 添加 JavaScript 來同步值到 One2many
            html += '''
            <script>
            (function() {
                const container = document.querySelector('.oa-form-dynamic');
                if (!container) return;

                // 監聽所有輸入變化
                container.addEventListener('change', function(e) {
                    const input = e.target;
                    const targetModel = input.dataset.targetModel;
                    const targetFieldId = input.dataset.targetFieldId;
                    const fieldName = input.dataset.fieldName;

                    if (targetModel && targetFieldId && fieldName) {
                        // 這裡需要通過 RPC 調用來更新字段值
                        // 暫時使用 onchange 方式
                    }
                });
            })();
            </script>
            '''

            instance.form_html = html
        """當選擇範本時，自動建立對應的欄位值記錄"""
        if self.template_id and self.state == 'draft':
            # 清除舊的欄位值
            self.field_value_ids = [(5, 0, 0)]

            # 為範本的每個欄位建立值記錄
            field_values = []
            for field in self.template_id.field_ids:
                field_values.append((0, 0, {
                    'field_id': field.id,
                }))
            self.field_value_ids = field_values

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('oa.form.instance') or 'New'

            # 如果選擇了範本，自動創建對應的欄位值記錄
            template_id = vals.get('template_id')
            if template_id and not vals.get('field_value_ids'):
                template = self.env['oa.form.template'].browse(template_id)
                if template.exists():
                    # 創建欄位值記錄
                    field_values = []
                    for field in template.field_ids:
                        field_values.append((0, 0, {
                            'field_id': field.id,
                            'instance_id': 0,  # 稍後會更新
                        }))
                    vals['field_value_ids'] = field_values

        instances = super().create(vals_list)

        # 更新欄位值記錄的 instance_id
        for instance in instances:
            if instance.field_value_ids:
                instance.field_value_ids.write({'instance_id': instance.id})

        return instances

    def action_submit(self):
        """提交表單"""
        self.ensure_one()
        
        # 驗證必填欄位
        self._validate_required_fields()
        
        # 流轉到第一個審核步驟
        self._start_approval()
        
        # 更新狀態
        self.write({
            'state': 'pending',
            'submit_date': fields.Datetime.now(),
        })

    def _validate_required_fields(self):
        """驗證必填欄位"""
        required_fields = self.template_id.field_ids.filtered('required')
        for field in required_fields:
            value = self.field_value_ids.filtered(lambda v: v.field_id.id == field.id)
            if not value or not self._get_field_value(value):
                raise UserError(f"必填欄位「{field.name}」不能為空！")

    def _get_field_value(self, field_value):
        """獲取欄位值"""
        ft = field_value.field_id.field_type
        if ft == 'char':
            return field_value.value_char
        elif ft == 'text':
            return field_value.value_text
        elif ft == 'integer':
            return field_value.value_integer
        elif ft == 'float':
            return field_value.value_float
        elif ft == 'date':
            return field_value.value_date
        elif ft == 'datetime':
            return field_value.value_datetime
        elif ft == 'selection':
            return field_value.value_char  # selection 值存在 value_char
        elif ft == 'employee':
            return field_value.value_employee_id
        elif ft == 'department':
            return field_value.value_department_id
        elif ft == 'file':
            return field_value.value_file
        return None

    def _start_approval(self):
        """開始審核流程"""
        self.current_step = 1
        self._create_approval_activity()

    def _create_approval_activity(self):
        """為當前審核步驟創建活動"""
        chain = self.approval_chain_id
        if not chain:
            return

        step = chain.step_ids.filtered(lambda s: s.sequence == self.current_step)
        if not step:
            return

        approver = step._get_approver(self)

        # 驗證審核人是否存在 - 使用 exists() 檢查
        if not approver or not approver.exists():
            # 根據審核人類型提供具體的錯誤訊息
            if step.approver_type == 'manager':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：直屬主管\n'
                              f'申請人「{self.applicant_id.name}」尚未設定直屬主管。\n\n'
                              f'請前往「員工」設定頁面，為「{self.applicant_id.name}」設定直屬主管後再重新提交。')
            elif step.approver_type == 'specific':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：指定人員\n'
                              f'尚未選擇具體的審核人員。\n\n'
                              f'請前往「審核鏈」設定頁面，為步驟「{step.name}」選擇指定審核人。')
            elif step.approver_type == 'department_head':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：部門主管\n'
                              f'部門尚未設定主管。\n\n'
                              f'請前往「部門」設定頁面，為相關部門設定主管後再重新提交。')
            else:
                raise UserError(f'無法找到審核人！請檢查審核步驟「{step.name}」的配置。')

        if not approver.user_id:
            raise UserError(f'審核人「{approver.name}」沒有關聯的系統用戶！\n\n'
                          f'請前往「員工」設定頁面，為「{approver.name}」關聯系統用戶後再重新提交。')

        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('oa_approval.mail_activity_approval').id,
            'summary': f'待審核：{self.template_id.name} - {self.name}',
            'user_id': approver.user_id.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get_id(self._name),
            'date_deadline': self._calculate_deadline(),
        })

        # 發送郵件通知
        self._send_approval_notification_email(approver)

    def _calculate_deadline(self):
        """計算截止日期"""
        # 可以配置為 24-72 小時後
        from datetime import timedelta
        return fields.Datetime.now() + timedelta(hours=72)

    def get_form_url(self):
        """獲取表單URL"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&model=oa.form.instance&view_type=form"

    def _send_approval_notification_email(self, approver):
        """發送審核通知郵件"""
        self.ensure_one()
        if not approver or not approver.user_id:
            return

        # 獲取審核人的 email (從 partner)
        email = approver.user_id.partner_id.email if approver.user_id.partner_id else approver.work_email
        if not email:
            return

        try:
            # 創建簡單的郵件內容
            subject = f"待審核通知：{self.template_id.name} - {self.name}"
            body = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">
                <p>您好 {approver.name or ''}，</p>
                <p>您有一個新的表單需要審核：</p>
                <ul>
                    <li>表單編號：{self.name}</li>
                    <li>表單類型：{self.template_id.name}</li>
                    <li>申請人：{self.applicant_id.name}</li>
                    <li>提交時間：{self.submit_date or ''}</li>
                </ul>
                <p>請登入系統查看詳情並進行審核。</p>
            </div>
            """

            # 創建郵件（使用隊列，異步發送）
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email,
                'email_from': self.env.user.email_formatted or 'noreply@odoo.com',
            }

            # 創建郵件但不立即發送（會進入隊列）
            self.env['mail.mail'].create(mail_values)

        except Exception as e:
            # 記錄錯誤但不影響審核流程
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"創建審核通知郵件失敗: {str(e)}")

    def _send_approved_notification_email(self):
        """發送審核通過通知郵件給申請人"""
        self.ensure_one()
        if not self.applicant_id or not self.applicant_id.user_id:
            return

        # 獲取申請人的 email (從 partner)
        email = self.applicant_id.user_id.partner_id.email if self.applicant_id.user_id.partner_id else self.applicant_id.work_email
        if not email:
            return

        try:
            # 創建簡單的郵件內容
            subject = f"表單審核通過：{self.template_id.name} - {self.name}"
            body = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">
                <p>您好 {self.applicant_id.name or ''}，</p>
                <p>您的表單已經審核通過：</p>
                <ul>
                    <li>表單編號：{self.name}</li>
                    <li>表單類型：{self.template_id.name}</li>
                    <li>完成時間：{self.complete_date or ''}</li>
                </ul>
                <p>請登入系統查看詳情。</p>
            </div>
            """

            # 創建郵件（使用隊列，異步發送）
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email,
                'email_from': self.env.user.email_formatted or 'noreply@odoo.com',
            }

            # 創建郵件但不立即發送（會進入隊列）
            self.env['mail.mail'].create(mail_values)

        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"創建審核通過通知郵件失敗: {str(e)}")

    def _send_rejected_notification_email(self):
        """發送審核駁回通知郵件給申請人"""
        self.ensure_one()
        if not self.applicant_id or not self.applicant_id.user_id:
            return

        # 獲取申請人的 email (從 partner)
        email = self.applicant_id.user_id.partner_id.email if self.applicant_id.user_id.partner_id else self.applicant_id.work_email
        if not email:
            return

        try:
            # 創建簡單的郵件內容
            subject = f"表單審核駁回：{self.template_id.name} - {self.name}"
            body = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">
                <p>您好 {self.applicant_id.name or ''}，</p>
                <p>您的表單已被駁回：</p>
                <ul>
                    <li>表單編號：{self.name}</li>
                    <li>表單類型：{self.template_id.name}</li>
                    <li>審核時間：{self.complete_date or ''}</li>
                </ul>
                <p>請登入系統查看詳情。</p>
            </div>
            """

            # 創建郵件（使用隊列，異步發送）
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email,
                'email_from': self.env.user.email_formatted or 'noreply@odoo.com',
            }

            # 創建郵件但不立即發送（會進入隊列）
            self.env['mail.mail'].create(mail_values)

        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"創建審核駁回通知郵件失敗: {str(e)}")

    def action_approve(self):
        """通過審核"""
        self.ensure_one()

        if self.state != 'pending':
            raise UserError('只能審核待審核狀態的表單！')

        chain = self.approval_chain_id
        if not chain:
            return

        # 記錄審核
        self._create_approval_record('approve')

        # 檢查是否是最後一步
        total_steps = len(chain.step_ids)
        if self.current_step >= total_steps:
            # 審核完成
            self.write({
                'state': 'approved',
                'complete_date': fields.Datetime.now(),
                'current_step': 0,
            })
            # 發送審核通過通知給申請人
            self._send_approved_notification_email()
        else:
            # 流轉到下一步
            self.current_step += 1
            self._create_approval_activity()

    def action_reject(self):
        """駁回審核"""
        self.ensure_one()

        if self.state != 'pending':
            raise UserError('只能審核待審核狀態的表單！')

        # 記錄審核
        self._create_approval_record('reject')

        # 更新狀態為駁回
        self.write({
            'state': 'rejected',
            'complete_date': fields.Datetime.now(),
            'current_step': 0,
        })

        # 發送審核駁回通知給申請人
        self._send_rejected_notification_email()

    def _create_approval_record(self, action):
        """創建審核記錄"""
        chain = self.approval_chain_id
        step = chain.step_ids.filtered(lambda s: s.sequence == self.current_step)

        approver = step._get_approver(self)

        # 驗證審核人是否存在 - 使用 exists() 檢查記錄是否真實存在
        if not approver or not approver.exists():
            # 根據審核人類型提供具體的錯誤訊息
            if step.approver_type == 'manager':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：直屬主管\n'
                              f'申請人：「{self.applicant_id.name}」尚未設定直屬主管。\n\n'
                              f'請前往「員工」設定頁面，為「{self.applicant_id.name}」設定直屬主管後再重新提交。')
            elif step.approver_type == 'specific':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：指定人員\n'
                              f'尚未選擇具體的審核人員。\n\n'
                              f'請前往「審核鏈」設定頁面，為步驟「{step.name}」選擇指定審核人。')
            elif step.approver_type == 'department_head':
                raise UserError(f'無法找到審核人！\n\n'
                              f'審核步驟：「{step.name}」\n'
                              f'審核人類型：部門主管\n'
                              f'部門尚未設定主管。\n\n'
                              f'請前往「部門」設定頁面，為相關部門設定主管後再重新提交。')
            else:
                raise UserError(f'無法找到審核人！請檢查審核步驟「{step.name}」的配置。')

        if not approver.user_id:
            raise UserError(f'審核人「{approver.name}」沒有關聯的系統用戶！\n\n'
                          f'請前往「員工」設定頁面，為「{approver.name}」關聯系統用戶後再重新提交。')

        self.env['oa.approval.record'].sudo().create({
            'instance_id': self.id,
            'step_id': step.id,
            'approver_id': approver.id,
            'action': action,
        })

    def action_view_approval_chain(self):
        """查看審核鏈詳情"""
        self.ensure_one()

        if not self.approval_chain_id:
            raise UserError('此表單沒有設置審核流程')

        # 創建 wizard 實例
        wizard = self.env['oa.approval.chain.view.wizard'].create({
            'chain_id': self.approval_chain_id.id,
            'name': self.approval_chain_id.name,
            'description': self.approval_chain_id.description,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'oa.approval.chain.view.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self.env.context,
        }
