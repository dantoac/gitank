# -*- coding: utf-8 -*-


import os,uuid

db.define_table('menta_comment',
                Field('menta_uuid', default=uuid.uuid4()),
                Field('menta_context', label='Contexto', 
                      default = request.vars.context,
                      readable=False, writable=False),
                Field('menta_title'),
                Field('menta_body', 'text'),
                Field('menta_reply_to',
                      requires=IS_EMPTY_OR(
                          IS_IN_DB(db, 
                                   'menta_comment.menta_uuid', 
                                   'menta_comment.menta_title'))
                  ),
                Field('menta_file', 'upload',
                      uploadfolder=os.path.join(request.folder,'static/uploads'),
                      represent = lambda v,r: A(IMG(_src=URL(c='static',f='uploads',args=v),
                                                    _style='max-width:6em;height:6em;'), 
                                                _href=URL(c='static',f='uploads',args=v))),
                Field('menta_author', requires=[IS_NOT_EMPTY(),IS_EMAIL()]),
                Field('menta_created_on', 'datetime', default=request.now),
                Field('menta_modified_on', 'datetime', compute=lambda r: request.now.now()),
                )


class Menta:
    '''
    Esta clase obtiene los comentarios en un contexto determinado,
    representado por una UUID.
    Retorna un objeto serializable en JSON que representa comentarios 
    y subcomentarios.
    '''

    def __init__(self, context, orderby = (db.menta_comment.id)):
        self.context = context
        self.orderby = orderby
        if not context: return None

    def get_comments(self):
        '''
        Obtiene la raiz del arbol de comentarios
        Su parametro es el "contexto", es decir, el UUID objeto referente 
        del comentario.
        Devuelve una lista recursiva de comentarios y subcomentarios como el siguiente:

        comments = [{
        "body": "primer comentario",
        "sub": [{
            "body": "segundo comentario",
            "sub": [{
                "body": "tercer comentario",
                "sub": [{
                    "body": "cuarto comentario",
                    "sub": [ ],
                    "uuid": "e028e2de-d67d-406e-adee-acf6c3570494",
                    "file": "",
                    "title": "cuarto comentario"
                    }],
                "uuid": "d1359029-dcba-4686-a6d8-0b15b2504341",
                "file": "menta_comment.menta_file.9a294f3b84cf04ca.72775f616c6c2e6d3375.m3u",
                "title": "tercer comentario"
                }],
            "uuid": "b7957f8b-7755-44a6-9524-f97758b32fe6",
            "file": "",
            "title": "segundo comentario"
            }],
        "uuid": "68a50fea-a885-463d-9b42-8ce2db5b6fb5",
        "file": "",
        "title": "primer comentario"
        }]

        '''

        context = self.context

        query = ((db.menta_comment.menta_context == context)
                 & (db.menta_comment.menta_reply_to == None))

        ORDERBY = self.orderby
        dataset = db(query).select(orderby = ORDERBY)

        comment = []

        for d in dataset:
            comment.append({
                #'id': d.id,
                'uuid': d.menta_uuid,
                'author': d.menta_author,
                'created_on': d.menta_created_on,
                'modified_on': d.menta_modified_on,
                'title': d.menta_title,
                'body': d.menta_body,
                'file': d.menta_file,
                'sub': Menta.get_subcomment(self, d.menta_uuid)
            })

        self.comment = comment or EM(T('No hay comentarios'))

        return self.comment

    @staticmethod
    def get_subcomment(self, comment_uuid):
        '''
        Obtiene recursivamente los comentarios hechos de otro comentario,
        ordenandolos en cascada.
        Obtiene como parametro el UUID del comentarios padre.
        Devuelve una lista de diccionarios (objeto Comentario)
        '''

        ORDERBY = self.orderby
        query = (db.menta_comment.menta_reply_to == comment_uuid)

        subcomment = [{
            'uuid': sub['menta_uuid'],
            'author': sub['menta_author'],
            'created_on': sub['menta_created_on'],
            'modified_on': sub['menta_modified_on'],
            'title': sub['menta_title'],
            'body': sub['menta_body'],
            'file': sub['menta_file'],
            'sub': Menta.get_subcomment(sub['menta_uuid'])
        } for sub in db(query).select(orderby=ORDERBY)]

        return subcomment

