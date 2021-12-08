from odoo import fields,models,api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class TicketSupport(models.Model):
    _name = 'ticket.support'

    @api.model
    def default_get(self, fields):
        res = super(TicketSupport, self).default_get(fields)
        admin_details = self.env['admin.config'].search([])
        support_details = self.env['support.config'].search([])
        count_1 = 0
        if admin_details:
            for line_1 in admin_details:
                if count_1 == 0:
                    res.update({
                        'admin_id': line_1.admin_id,
                        'admin_mail': line_1.admin_mail,
                    })
                    count_1 += 1
        return res

    name = fields.Char(default='New')
    customer_id = fields.Char('Customer')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    company_mail = fields.Char()
    module_name = fields.Many2one('module.list')
    customer_mail = fields.Char()
    description = fields.Text('Description')
    image = fields.Binary('Screenshot')
    status = fields.Selection(
        [('draft', 'Draft'),('seen','Seen'),('forward to developer', 'Forward To Developer'), ('testing', 'Testing'), ('finished', 'Finished')],
        default='draft')
    assign_to = fields.Char('Assign To')
    assign_mail = fields.Char('Employee Mail')
    test_username = fields.Char()
    password = fields.Char()
    ticket_id = fields.Many2one('help.desk.ticket')
    user_id = fields.Many2one('res.users', "User Id",
                              default=lambda self: self.env.user)
    your_username = fields.Char('Their Username')
    your_password = fields.Char('Their Password')
    solution = fields.Text()
    sloution_form_developer = fields.Text()
    admin_id = fields.Char('Admin Name')
    admin_mail = fields.Char('Admin Email')
    start_time = fields.Datetime('Employee Start')
    stop_time = fields.Datetime('Employee Stop')
    progress = fields.Float("Progress", store=True, group_operator="avg",compute='_compute_progress_hours', help="Display progress of current task.")
    duration = fields.Float()
    # subtask_effective_hours = fields.Float("Sub-tasks Hours Spent",store=True, help="Sum of actually spent hours on the subtask(s)", oldname='children_hours')
    planned_hours = fields.Float(
        string='Planned Hours',
        track_visibility='onchange',
    )
    effective_hours = fields.Float(compute='compute_duration')
    effective_lines = fields.One2many('time.line.help','ticket_id')
    dead_line = fields.Datetime()
    emp_duration = fields.Float()
    emp_deadline = fields.Datetime()

    @api.depends('effective_lines')
    def compute_duration(self):
        time_taken = 0
        for line in self:
            if line.effective_lines:
                for time in line.effective_lines:
                    time_taken = time_taken + time.unit_amount

                line.effective_hours = time_taken
    # @api.depends('timesheet_ids.unit_amount')
    # def _compute_effective_hours(self):
    #     for task in self:
    #         task.effective_hours = round(sum(task.timesheet_ids.mapped('unit_amount')), 2)
    # subtask_effective_hours = fields.Float("Sub-tasks Hours Spent", compute='_compute_subtask_effective_hours', store=True, help="Sum of actually spent hours on the subtask(s)", oldname='children_hours')
    # progress = fields.Float("Progress", compute='_compute_progress_hours', store=True, group_operator="avg", help="Display progress of current task.")


    @api.depends('effective_hours', 'planned_hours')
    def _compute_progress_hours(self):
        for task in self:
            if (task.planned_hours > 0.0):
                task_total_hours = task.effective_hours
                if task_total_hours > task.planned_hours:
                    task.progress = 100
                else:
                    task.progress = round(100.0 * task_total_hours / task.planned_hours, 2)
            else:
                task.progress = 0.0

    def finished(self):
        if self.solution:
            self.status = 'finished'
            self.ticket_id.state = 'finished'
            # template_id = self.env.ref('helpdesk_support.email_template_ticketsupportempcompany').id
            # template = self.env['mail.template'].browse(template_id)
            # template.send_mail(self.id, force_send=True)
            # template_id_1 = self.env.ref('helpdesk_support.email_template_ticketsupportempcustomer').id
            # template_1 = self.env['mail.template'].browse(template_id_1)
            # template_1.send_mail(self.id, force_send=True)
            # template_id_2 = self.env.ref('helpdesk_support.email_template_ticketsupportempcustomeradmin').id
            # template_2 = self.env['mail.template'].browse(template_id_2)
            # template_2.send_mail(self.id, force_send=True)

            mail_template_comp = self.env.ref('helpdesk_support.email_template_ticketsupportempcompany_test')
            mail_template_comp.send_mail(self.id, force_send=True)
            mail_template_cus = self.env.ref('helpdesk_support.email_template_ticketsupportempcustomer_test')
            mail_template_cus.send_mail(self.id, force_send=True)
            mail_template_admin = self.env.ref('helpdesk_support.email_template_ticketsupportempcustomeradmin_test')
            mail_template_admin.send_mail(self.id, force_send=True)



    def testing(self):
        self.status = 'testing'
        self.ticket_id.state = 'testing'

    def seen_ticket(self):
        self.status = 'seen'
        self.ticket_id.state = 'seen'

    def assigntodeveloper(self):
        if self.assign_to:
            if self.assign_mail:
                if self.test_username:
                    if self.password:
                        if self.ticket_id:
                            self.status = 'forward to developer'
                            self.ticket_id.state = 'forward to developer'
                            self.env['assign.ticket.work'].create({
                                'module_name': self.module_name.id,
                                'your_username': self.test_username,
                                'your_password': self.password,
                                'description': self.description,
                                'image': self.image,
                                'ticket_id': self.ticket_id.id,
                                'name': self.name,
                                'emp_duration':self.emp_duration,
                                'emp_deadline':self.emp_deadline,
                                'customer_id':self.customer_id,
                            })
                            # template_id = self.env.ref('helpdesk_support.email_template_ticketsupportemp').id
                            # template = self.env['mail.template'].browse(template_id)
                            # template.send_mail(self.id, force_send=True)
                            # template_id_1 = self.env.ref('helpdesk_support.email_template_ticketsupportempadmin').id
                            # template_1 = self.env['mail.template'].browse(template_id_1)
                            # template_1.send_mail(self.id, force_send=True)

                            mail_template_emp = self.env.ref('helpdesk_support.email_template_ticketsupportemp_test')
                            mail_template_emp.send_mail(self.id, force_send=True)
                            mail_template_admin = self.env.ref('helpdesk_support.email_template_ticketsupportempadmin_test')
                            mail_template_admin.send_mail(self.id, force_send=True)



class TimeLineHelp(models.Model):
    _name = 'time.line.help'

    ticket_id = fields.Many2one('ticket.support')
    date = fields.Date(default=datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT))
    employee_id = fields.Many2one('res.users',
                              default=lambda self: self.env.user)
    description = fields.Char()
    unit_amount = fields.Float(default=0.0,string='Duration(Hours(s))')