#encoding: utf8

if 0: from gluon import *

import uuid

dt = db.define_table

import string, time, math, random
 
def uniqid(prefix='', more_entropy=False):
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    if more_entropy:
        valid_chars = list(set(string.hexdigits.lower()))
        entropy_string = ''
        for i in range(0,10,1):
            entropy_string += random.choice(valid_chars)
        uniqid = uniqid + entropy_string
    uniqid = prefix + uniqid
    return uniqid

dt('project',
   Field('uuid', 'string', length=32, default=uuid.uuid4().hex,
         writable=False, readable=False, unique=True, required=True),
   Field('title', 'string', label='Nombre', required=True,
         unique=True, requires=[IS_NOT_EMPTY(),
                                IS_NOT_IN_DB(db,'project.title')]),
   Field('slug', compute=lambda n: IS_SLUG()(n['title'])[0]),
   Field('start_date', 'date', default=request.now,
         label='Fecha Inicio'),
   Field('end_date', 'date', represent = lambda v,r: v.date() if v else '',
         label='Fecha Término'),
   Field('closed', 'boolean', default=False, readable=False, writable=False),
   Field('repository', 'string', length=255, comment='(Repositorio Git)'),
   auth.signature,
   format = '%(title)s'
)

    
dt('issue',
   Field('uuid','string',length=32, default=uuid.uuid4().hex,
         writable=False, readable=False, unique=True, required=True,
         requires=IS_NOT_IN_DB(db, 'issue.uuid')
     ),
   Field('project_uuid', 'string', length=32,
         writable=False, readable=False, unique=True, required=True),
   Field('title', 'string', required=True, requires=IS_NOT_EMPTY()),
   Field('tag','list:string'),
   Field('description', 'text'),
   Field('priority', 'string', requires=IS_EMPTY_OR(IS_IN_SET([1,2,3,4,5])),
         label=T('Prioridad'),default='3'),
   Field('solved', 'boolean', default=False, writable=False, readable=False),
   Field('author','string', writable=False, readable=False),
   Field('issue_parent', label="Necesita"),
   Field('project_issue_number', 'integer',  writable=False, readable=False),
   auth.signature,
   #    Field('issue_child', label="Permite"),
   format = '%(title)s'
)
