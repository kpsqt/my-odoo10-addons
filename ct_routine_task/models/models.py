# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
import time, datetime, dateutil


class Task(models.Model):
    _name = 'ct_routine_task.task'
    _description = 'Routine Task'
    _order = 'sequence'

    # @api.multi
    # def _compute_stage(self):
    #     for record in self:
    #         record_date = time.strptime(record.create_date, '%Y-%m-%d')
    #         if record_date == datetime.date.today():
    #             record.stage_id = self.env.ref('ct_routine_task.today').id
    #         elif record_date.

    @api.multi
    def write(self, vals):
        # print self.env.context
        if vals.has_key('stage_id'):
            del vals['stage_id']
            raise UserError(_('It is not allowed to change the stage of the task.'))
        result = super(Task, self).write(vals)

        return result
    
    def _compute_stage_display(self):
        for rec in self:
            if len(rec.mapped('stage_id')) == 1:
                rec.stage_display = rec.stage_id
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        stage_id = self.env.context.get('default_stage_id', False)
        if not stage_id:
            #print self.env.ref('ct_routine_task.today')
            return self.env.ref('ct_routine_task.today').id
        return self.stage_find(stage_id, [('fold', '=', False)])
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # print '_read_group_stage_ids, ', stages
        search_domain = [('active','=',True)]

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        # print stage_ids
        return stages.browse(stage_ids)
    
#     @api.onchange('stage_id')
#     def _onchange_stage(self):
#         if self.stage_id:
#             print 'TEST'
#         else:
#             print 'TEST'
            
    @api.multi
    def add_detail(self):
        '''
        This function opens a window to insert a detail without being in edit mode
        '''
        view = self.env.ref('ct_routine_task.ct_routine_task_task_detail_edit_form')
        context = dict()
        context.update({
            'default_task_id': self[0].id,
        })
        return {
            'name': 'Add detail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ct_routine_task.task_detail',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
    
#     STAGES = [
#         ('a_today', 'Today'),
#         ('b_current_week', 'Current Week'),
#         ('c_current_month', 'Current Month'),
#         ('d_current_quarter', 'Current Quarter'),
#         ('e_current_year', 'Current Year'),
#     ]

    name = fields.Char(string='Task Title', required=True, translate=True)
    
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user , string='Assigned User')
    stage_id = fields.Many2one('ct_routine_task.task_stage', string='Stage', track_visibility='onchange', index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids', copy=False, domain=[('active','=',True)])
    stage_display = fields.Many2one('ct_routine_task.task_stage', string='Stage', compute='_compute_stage_display')
#     stage = fields.Selection(STAGES, default='a_today', string='Stage',
#     required=True, readonly=True,
#     group_expand='_read_group_stages',
#     copy=False)
    sequence = fields.Integer()
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], default='1', required=True)
    
    tag_ids = fields.Many2many('ct_routine_task.tag', string='Tags')
    
    detail_ids = fields.One2many(
        'ct_routine_task.task_detail', 'task_id', string='Details')
    color = fields.Integer(string='Color Index')
	description = fields.Text(string='Description')
    



class TaskStage(models.Model):
    _name = 'ct_routine_task.task_stage'
    #_order = 'sequence'
    
    name = fields.Char(translate=True)
    #sequence = fields.Integer()
    fold = fields.Boolean('Folded by Default')
    active = fields.Boolean('Active')
    

class TaskDetail(models.Model):
    _name = 'ct_routine_task.task_detail'
    _description = 'Routine Task Tag'
    _order = 'handled desc'
    
    @api.multi
    def save(self):
        return{
            'type':'ir.actions.act_window_close'
        }
        
    
    @api.multi
    def edit_detail(self):
        '''
        This function opens a window to edit a detail without being in edit mode
        '''
        view = self.env.ref('ct_routine_task.ct_routine_task_task_detail_edit_form')
        context = dict()
        context.update({
            'default_task_id': self[0].task_id.id,
        })
        return {
            'name': 'Edit Detail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ct_routine_task.task_detail',
            'res_id':self[0].id,
            'target': 'new',
            'context': context,
        }
    
    
    handled = fields.Datetime(default=fields.Datetime.now(), string='Handled at', required=True)
    description = fields.Text(string='Description', required=True)
    task_id = fields.Many2one('ct_routine_task.task', string='Task', required=True)
    description_display = fields.Char(compute='_description_display')

    @api.multi
    def _description_display(self):
        for record in self:
            new_display = ""
            if len(record.description) > 36:
                new_display = '%s...' % record.description[0:32]
            else:
                new_display = record.description
            record.description_display = new_display
    

class TaskTags(models.Model):
    _name = 'ct_routine_task.tag'
    _description = 'Routine Task Tag'
    

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name already exists !'),
    ]
    

    
