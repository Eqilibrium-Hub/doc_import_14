from odoo import fields,models,api

class HelpDeskTicket(models.Model):
    _name = 'help.desk.ticket'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('help.code') or '/'
        # self.env['ticket.support'].create(vals)
        res = super(HelpDeskTicket, self).create(vals)
        return res

    @api.model
    def default_get(self, fields):
        res = super(HelpDeskTicket, self).default_get(fields)
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
    company_id = fields.Many2one('res.company', string='Company', compute='compute_company')
    company_mail = fields.Char(compute='compute_company')
    module_name = fields.Many2one('module.list')
    customer_mail = fields.Char('Email')
    # description = fields.Text('Description')
    description = fields.Many2one('templates')
    image = fields.Binary('Screenshot',required=True)
    state = fields.Selection([('draft','Draft'),('post','Post'),('seen','Seen'),('forward to developer','Forward To Developer'),('testing','Testing'),('finished','Finished')],default='draft')
    reply = fields.Text()
    user_id = fields.Many2one('res.users', "User Id",
                              default=lambda self: self.env.user)
    admin_id = fields.Char('Admin Name')
    admin_mail = fields.Char('Admin Email')
    team_leader = fields.Char('Support Leader')
    team_mail = fields.Char('Team Email')
    your_username = fields.Char()
    your_password = fields.Char()
    solution = fields.Text()
    dead_line = fields.Datetime()

    @api.depends('company_id','company_mail')
    def compute_company(self):
        for line in self:
            line.company_id = self.env.user.company_id
            line.company_mail = line.company_id.email

    def post(self):
        self.state = 'post'
        self.env['ticket.support'].create({
            'name': self.name,
            'customer_id': self.customer_id,
            'company_id': self.company_id.id,
            'company_mail': self.company_mail,
            'module_name': self.module_name.id,
            'customer_mail': self.customer_mail,
            # 'description': self.description,
            'description': self.description.name,
            'image': self.image,
            'ticket_id': self.id,
            'your_username': self.your_username,
            'your_password': self.your_password,
            'dead_line':self.dead_line,
        })
        mail_template = self.env.ref('helpdesk_support.email_template_test_cus')
        mail_template.send_mail(self.id, force_send=True)
        mail_template_1 = self.env.ref('helpdesk_support.email_template_ticketcomp_test')
        mail_template_1.send_mail(self.id, force_send=True)
        mail_template_2 = self.env.ref('helpdesk_support.email_template_ticketadmin_test')
        mail_template_2.send_mail(self.id, force_send=True)
        mail_template_3 = self.env.ref('helpdesk_support.email_template_ticketsupport_test')
        mail_template_3.send_mail(self.id, force_send=True)
        print('hbkbjkb')

        # template_id = self.env.ref('helpdesk_support.email_template_ticketcomp').id
        # template = self.env['mail.template'].browse(template_id)
        # # template.send_mail(self.id, force_send=True)
        # template.send_mail(self.id, force_send=True)
        # template_id_1 = self.env.ref('helpdesk_support.email_template_ticketcus').id
        # template_1 = self.env['mail.template'].browse(template_id_1)
        # template_1.send_mail(self.id, force_send=True)
        # template_id_2 = self.env.ref('helpdesk_support.email_template_ticketadmin').id
        # template_2 = self.env['mail.template'].browse(template_id_2)
        # template_2.send_mail(self.id, force_send=True)
        # template_id_3 = self.env.ref('helpdesk_support.email_template_ticketsupport').id
        # template_3 = self.env['mail.template'].browse(template_id_3)
        # template_3.send_mail(self.id, force_send=True)
    # def send_mail_test(self):
    #     # mail_template = self.env.ref('helpdesk_support.email_template_ticketcus')
    #     mail_template = self.env.ref('helpdesk_support.email_template_test_cus')
    #     mail_template.send_mail(self.id, force_send=True)
    #     mail_template_1 = self.env.ref('helpdesk_support.email_template_ticketcomp_test')
    #     mail_template_1.send_mail(self.id, force_send=True)
    #     mail_template_2 = self.env.ref('helpdesk_support.email_template_ticketadmin_test')
    #     mail_template_2.send_mail(self.id, force_send=True)
    #     mail_template_3 = self.env.ref('helpdesk_support.email_template_ticketsupport_test')
    #     mail_template_3.send_mail(self.id, force_send=True)
    #     print('hbkbjkb')

    @api.onchange('company_id')
    def computecommail(self):
        if self.company_id:
            self.company_mail = self.company_id.email

    # @api.onchange('customer_id')
    # def compute_email(self):
    #     if self.customer_id:
    #         self.customer_mail = self.customer_id.email


    # def send_prearrival(self):
    #

class AdminConfig(models.Model):
    _name = 'admin.config'

    admin_id = fields.Char('Admin')
    admin_mail = fields.Char('Email')

    # @api.onchange('admin_id')
    # def compute_email(self):
    #     if self.admin_id:
    #         self.admin_mail = self.admin_id.email

class SupportConfig(models.Model):
    _name = 'support.config'

    name = fields.Char('Team Name')
    team_leader = fields.Char()
    team_mail = fields.Char('Email')

    # @api.onchange('team_leader')
    # def compute_email(self):
    #     if self.team_leader:
    #         self.team_mail = self.team_leader.email

class ModuleList(models.Model):
    _name = 'module.list'

    name = fields.Char()