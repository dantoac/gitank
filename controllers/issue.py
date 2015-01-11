# -*- coding: utf-8 -*-

if False: from gluon import *
from gittle import Gittle

def view():
    from tools import prettydate
    project_slug = request.args(0)
    project_issue_number = request.args(1)
    
    project = _get_project_metadata(project_slug = project_slug)

    
    query = ((db.issue.project_uuid == project.uuid)
             & (db.issue.project_issue_number == project_issue_number))
    
    issue = db(query).select(limitby=(0,1)).first()

    commits_related = _get_git_data(project.repository)
    commits = commits_related[issue.project_issue_number]
    
    return locals()


def edit():

    project = _get_project_metadata(project_slug = request.args(0))
    project_issue_number = request.args(1)

    query = ((db.issue.project_uuid == project.uuid) &
             (db.issue.project_issue_number == project_issue_number))
    
    issue_id = db(query).select(db.issue.id, limitby=(0,1)).first().id

    #form asap...
    form = SQLFORM(db.issue, issue_id)

    if form.process().accepted:
        session.flash = 'Datos actualizados'     
        redirect(URL(f='view', args=[project.slug, project_issue_number]))
        
    elif form.errors:
        response.flash = 'Hubo errores en el formulario'
    return locals()
    
@auth.requires_login()
def index():
    # TODO: es necesario paginar...

    project_slug = request.args(0)
    
    project = _get_project_metadata(project_slug=project_slug)
    
    query = ((db.issue.project_uuid == project.uuid)
             & (db.issue.solved == False)
         )
    
    project_issues = db(query).select(db.issue.id,
                                      db.issue.project_uuid,
                                      db.issue.project_issue_number,
                                      db.issue.title,
                                      db.issue.solved,
                                      cacheable = True,
                                      orderby = db.issue.priority|~db.issue.id)

    commit_related = _get_git_data(project.repository)

    
    
    #response.view = 'views/generic.html'
    
    return locals()



def new():

    project = _get_project_metadata(project_slug=request.args(0))

    project_issues = _get_project_issues(project.uuid)
    
    db.issue.project_uuid.default = project.uuid
    db.issue.project_issue_number.default = _last_project_issue_number(project.uuid)
    
    form = SQLFORM(db.issue)

    if form.process().accepted:
        session.flash = 'Incidencia Registrada exitosamente'
        redirect(URL(f='index', args=project.slug))
    elif form.errors:
        response.flash = 'Atienda los errores en el formulario'
    
    return {'form' : form}

    
def solve():
    '''
    Resuelve o reabre una incidencia
    '''

    issue_uuid = request.get_vars.issue_uuid

    record = db(db.issue.uuid == issue_uuid).select(db.issue.id, db.issue.solved).first()
    
    solved = False if record.solved else True

    record.update_record(solved=solved)

    #responder un js en vez de redirigir
    if solved:
        session.flash = 'Incidencia Resuelta'
    else:
        session.flash = 'Incidencia Reabierta'

    redirect(URL(f='view', args=request.args), client_side=True)

