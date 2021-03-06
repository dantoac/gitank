# -*- coding: utf-8 -*-

if False: from gluon import *

@auth.requires_login()
def view():
    from tools import prettydate
    project_slug = request.args(0)
    project_issue_number = request.args(1)
    
    project = _get_project_metadata(project_slug = project_slug)
    
    query = ((Issue.project_uuid == project.uuid)
             & (Issue.project_issue_number == project_issue_number))
    
    issue = db(query).select(limitby=(0,1)).first()

    commits_related = _get_git_data(project.repository, project.repository_branch) if project.repository else None
    
    commits = commits_related[issue.project_issue_number] if commits_related else ''

    ##comentarios
        
    context = request.get_vars.context
    db.menta_comment.menta_context.default = context
    db.menta_comment.menta_uuid.readable = False
    db.menta_comment.menta_uuid.writable = False
    db.menta_comment.menta_created_on.writable = False
    db.menta_comment.menta_created_on.readable = False
    db.menta_comment.menta_author.writable = False
    db.menta_comment.menta_author.readable = False
    db.menta_comment.menta_reply_to.writable = False
    db.menta_comment.menta_reply_to.readable = False
    db.menta_comment.menta_author.default = auth.user.email
    db.menta_comment.menta_title.writable = False
    db.menta_comment.menta_title.readable = False
    
    form = SQLFORM(db.menta_comment)

    if form.process().accepted:
        response.flash = 'OK'
        
    elif form.errors:
        response.flash = 'ERROR'

    context = request.get_vars.context
    menta = Menta(context=context)
    comments = menta.get_comments()

    return locals()

@auth.requires_login()
def edit():

    project = _get_project_metadata(project_slug = request.args(0))
    project_issue_number = request.args(1)

    # Crea lista de incidencias padre
    Issue.issue_parent.requires = IS_EMPTY_OR(
        IS_IN_DB(db((Issue.project_issue_number != project_issue_number)
                    & (Issue.project_uuid == project.uuid)
                    & (Issue.solved == False)),
             Issue.uuid, '#%(project_issue_number)s %(title)s'))
    
    query = ((Issue.project_uuid == project.uuid) &
             (Issue.project_issue_number == project_issue_number))
    
    issue_data = db(query).select(limitby=(0,1)).first()
    
    #form asap...
    form = SQLFORM(Issue, issue_data.id, formstyle='divs', showid=False)

    if form.process(dbio=False).accepted:

        #obtenemos los nuevos datos
        after = []
        for k,val in form.vars.iteritems():
            #si es una lista, es necesaria convertirla a
            #un objecto hashable.
            if isinstance(val, list):
                v = ','.join(val)
                after.append((k,v))
            else:
                after.append((k,val))

        flds = []
        for k in form.vars.keys():
            flds.append(db.issue[k])
            
        #obtenemos los valores anteriores de los
        #campos enviados
        before = []
        for k,val in db(db.issue.id == issue_data.id).select(*flds).first().as_dict().iteritems():
            if isinstance(val, list):
                v = ','.join(val)
                print(v)
                before.append((k,v))
            else:
                before.append((k,val))

        a = set(after)
        b = set(before)

        #obtiene la diferencia entre sets
        changed = list(a - b)

        menta_body = ''.join(['''
        <li>Modificado: {0}</li>
        '''.format(str(T(c[0]).title()),c[1]) for c in changed])

        if changed:
            db.menta_comment.insert(**dict(
                menta_context = issue_data.uuid,
                menta_title = 'issue-update',
                menta_body = menta_body,
                menta_created_on = request.now.now(),
                menta_author = auth.user.email)
                )
        #actualizamos la db
        db(db.issue._id == issue_data.id).update(**form.vars)
        #response.flash = 'Datos actualizados: {0}'.format(changed)
        
        redirect(URL(f='view', args=[project.slug, project_issue_number]))
        
    elif form.errors:
        response.flash = 'Hubo errores en el formulario'
    return locals()
    
@auth.requires_login()
def index():
    '''
    Lista las incidencias de todos los proyectos en general o alguno
    en particular, segun el request.args(0) que se entregue.
    '''
    # TODO: es necesario paginar...

    project_slug = request.args(0)
    solved = request.get_vars.solved or False

    if project_slug:
        project = _get_project_metadata(project_slug=project_slug)
        query = ((Issue.project_uuid == project.uuid)
                 & (Issue.solved == solved)
             )
        #commit_related = _get_git_data(project.repository, project.repository_branch) if project.repository else None
    else:
        query = ((Issue.id > 0) & (Issue.solved == solved))
        project = None
        #commit_related = None

        
    project_issues = db(query).select(Issue.id,
                                      Issue.project_uuid,
                                      Issue.project_issue_number,
                                      Issue.title,
                                      Issue.solved,
                                      cacheable = True,
                                      orderby = Issue.priority|Issue.solved|~Issue.id)

    return locals()



def new():

    if request.args(0):
        project = _get_project_metadata(project_slug=request.args(0))
        Issue.project_uuid.default = project.uuid
        Issue.project_issue_number.default = _last_project_issue_number(project.uuid)
        
        Issue.issue_parent.requires = IS_EMPTY_OR(
            IS_IN_DB(db((Issue.project_uuid == project.uuid)
                        & (Issue.solved == False)),
                     Issue.uuid, '#%(project_issue_number)s %(title)s'))


    else:
        Issue.issue_parent.writable = False
        Issue.issue_parent.readable = False
        Issue.project_uuid.requires = IS_IN_DB(db, 'project.uuid', 'project.title')
        Issue.project_uuid.writable = True
        Issue.project_uuid.label = 'Project'
        
    form = SQLFORM(Issue)

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

    record = db(Issue.uuid == issue_uuid).select(Issue.id, Issue.solved).first()
    
    solved = False if record.solved else True

    record.update_record(solved=solved)

    #responder un js en vez de redirigir
    if solved:
        session.flash = 'Incidencia Resuelta'
    else:
        session.flash = 'Incidencia Reabierta'

    redirect(URL(f='view', args=request.args, vars=request.get_vars), client_side=True)

