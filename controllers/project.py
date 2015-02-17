# -*- coding: utf-8 -*-

@auth.requires_login()
def index():

    projects = db(db.project).select(orderby=~db.project.id)
    
    return {'projects': projects}


@auth.requires_login()
def new():
    #TODO: separar
    form = SQLFORM(db.project, request.args(0))
    
    if form.process().accepted:
        session.flash = 'Proyecto agregado'
        redirect(URL(f='index'))
    elif form.errors:
        response.flash = 'Atienda los errores del formulario'
        
    return {'form' : form}
