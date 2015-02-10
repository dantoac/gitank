# -*- coding: utf-8 -*-

def index():
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
    db.menta_comment.menta_title.writable = False
    db.menta_comment.menta_title.readable = False
    db.menta_comment.menta_file.writable = False
    db.menta_comment.menta_file.readable = False
    db.menta_comment.menta_author.default = auth.user.email
    db.menta_comment.menta_body.label = 'Comentario'
    form = SQLFORM(db.menta_comment,
                   formstyle='divs'
    )

    if form.process().accepted:
        response.flash = 'OK'
        
    elif form.errors:
        response.flash = 'ERROR'

    menta = Menta(context=context)
    comments = menta.get_comments()

        
    return locals()

@auth.requires_signature()
def delete():
    uuid = request.args(0)
    deleted = db(db.menta_comment.menta_uuid == uuid).delete()
    #return response.json({'deleted': deleted})
    print(uuid)
    response.js = "$('#comment-%s').slideUp();" % uuid
    return response.json(dict(deleted=deleted))
