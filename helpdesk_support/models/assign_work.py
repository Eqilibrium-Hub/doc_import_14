from odoo import fields,models,api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT

class AssignTicketWork(models.Model):
    _name = 'assign.ticket.work'

    @api.model
    def default_get(self, fields):
        res = super(AssignTicketWork, self).default_get(fields)
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
        count_2 = 0
        if support_details:
            for line_2 in support_details:
                if count_2 == 0:
                    res.update({
                        'team_leader': line_2.team_leader,
                        'team_mail': line_2.team_mail,
                    })
                    count_2 += 1

        return res

    name = fields.Char(default='New')
    customer_id = fields.Char('Customer')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    company_mail = fields.Char()
    module_name = fields.Many2one('module.list')
    customer_mail = fields.Char('Email')
    description = fields.Text('Description')
    image = fields.Binary('Screenshot')
    status = fields.Selection(
        [('draft', 'Draft'),('start', 'Start'), ('stop', 'Stop'),('solved','Solved')],
        default='draft')
    # solved_issue = fields.Text()
    your_username = fields.Char('Test Username')
    your_password = fields.Char('Test Password')
    ticket_id = fields.Many2one('help.desk.ticket')
    solutions = fields.Text()
    user_id = fields.Many2one('res.users', "User Id",
                              default=lambda self: self.env.user)
    admin_id = fields.Char('Admin Name')
    admin_mail = fields.Char('Admin Email')
    team_leader = fields.Char('Support Leader')
    team_mail = fields.Char('Team Email')
    start_time = fields.Datetime()
    stop_time = fields.Datetime()
    total_duration = fields.Float(string='Duration(in Hours)',default=0.0)
    emp_duration = fields.Float()
    emp_deadline = fields.Datetime()

    # @api.onchange('start_time','stop_time')
    # def compute_duration(self):
    #     if self.start_time:
    #         if self.stop_time:
    #             self.total_duration =


    def start_work(self):
        self.status = 'start'
        self.start_time = datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def stop_work(self):
        self.status = 'stop'
        self.stop_time = datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def finished(self):
        self.status = 'solved'
        self.env['time.line.help'].create({
            'ticket_id':self.env['ticket.support'].search([('name','=',self.name)]).id,
            'date':datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT),
            'employee_id':(self.env.user).id,
            'description':'Developer Worked',
            'unit_amount':self.total_duration

        })
        self.env['ticket.support'].search([('ticket_id','=',self.ticket_id.id)]).update({
            'sloution_form_developer':self.solutions,
            'start_time':self.start_time,
            'stop_time':self.stop_time,

        })
        # template_id = self.env.ref('helpdesk_support.email_template_ticketemployeefinishadm').id
        # template = self.env['mail.template'].browse(template_id)
        # template.send_mail(self.id, force_send=True)
        # template_id_1 = self.env.ref('helpdesk_support.email_template_ticketemployeefinishsup').id
        # template_1 = self.env['mail.template'].browse(template_id_1)
        # template_1.send_mail(self.id, force_send=True)
        mail_template_finishadm = self.env.ref('helpdesk_support.email_template_ticketemployeefinishadm_test')
        mail_template_finishadm.send_mail(self.id, force_send=True)
        mail_template_finishup = self.env.ref('helpdesk_support.email_template_ticketemployeefinishsup_test')
        mail_template_finishup.send_mail(self.id, force_send=True)
