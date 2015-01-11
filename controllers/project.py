# -*- coding: utf-8 -*-

def index():

    projects = db(db.project).select()
    
    return {'projects': projects}



def new():
    #TODO: separar
    form = SQLFORM(db.project, request.args(0))
    
    if form.process().accepted:
        session.flash = 'Proyecto agregado'
        redirect(URL(f='index'))
    elif form.errors:
        response.flash = 'Atienda los errores del formulario'
        
    return {'form' : form}
