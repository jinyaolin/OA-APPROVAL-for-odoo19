from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    job_grade_id = fields.Many2one('oa.job.grade', string='Job Grade', groups="hr.group_hr_user")
    job_level_id = fields.Many2one(
        'oa.job.level', string='Job Level',
        domain="[('grade_id', '=', job_grade_id)]",
        groups="hr.group_hr_user",
    )
    job_title_oa_id = fields.Many2one(
        'oa.job.title', string='Job Title (OA)',
        domain="[('level_id', '=', job_level_id)]",
        groups="hr.group_hr_user",
    )

    @api.onchange('job_grade_id')
    def _onchange_job_grade_id(self):
        self.job_level_id = False
        self.job_title_oa_id = False

    @api.onchange('job_level_id')
    def _onchange_job_level_id(self):
        self.job_title_oa_id = False
