
def _get_git_data(project_repository=None,
                  project_branch=None):
    '''
    Obtiene los commits relacionados a un issue:
    issue_related = {1 : [{'sha': SHA,
                           'message' : TEXT,
                           'time': TIMESTAMP
                            }],
                     3 : [{'sha': SHA,
                           'message' : TEXT,
                           'time': TIMESTAMP
                            }],
                     5 : [{'sha': SHA,
                           'message' : TEXT,
                           'time': TIMESTAMP
                            }],
                     ...}
    '''
    import re 
    from gittle import Gittle
    from collections import defaultdict
    from datetime import datetime
    
    related_flag = ';'
    
    
    print(project_repository)
    print(type(project_repository))

    repo = Gittle(project_repository)

    #establece la rama a cotejar con las incidencias
    # try:
    #     repo.switch_branch(project_branch)
    #     print("RAMA: ", project_branch)
    #     pass
    # except Exception as e:
    #     repo.switch_branch('master')
    #     print('32@issue_utils.py: %s' % e)

        
    issue_related = defaultdict(list)

    for commit in repo.log():
        #busca una referencia a un issue dentro de un commit
        pp = re.findall('[0-9]+{0}'.format(related_flag), commit['message'])
        for p in pp:
            #crea una tupla id, sha del commit
            related_issue_id = int(p.strip(related_flag))
            issue_related[related_issue_id].append({'sha': commit['sha'],
                                                    'message': commit['message'],
                                                    'time': datetime.utcfromtimestamp(int(commit['time']))
                                                })

    return issue_related


def _get_project_metadata(project_uuid=None,
                      project_id=None,
                      project_slug=None):
    '''
    Obtiene los datos de la tabla Project segun
    project_uuid, project_id o project_slug dado.

    Retorna un objeto Rows (storage/dict).
    '''
    if project_uuid and isinstance(project_uuid, str):
        query = (db.project.uuid == project_uuid)
    elif isinstance(project_slug, str):
        query = (db.project.slug == project_slug)
    elif isinstance(project_id, int):
        query = (db.project.id == project_id)
    else:
        raise HTTP(400)
        
    project = db(query).select(db.project.ALL,
                               #cache = (cache.ram, 3600),
                               cacheable = True,
                               limitby=(0,1)).first()
    
    if not project: raise HTTP(404)
    
    return project


def _get_project_issues(project_uuid, fields=None):

    if fields:
        fields_selected = fields
    else:
        fields_selected = db.issue.ALL

    query = ((db.issue.project_uuid == project_uuid)
             & (db.issue.project_uuid == db.project.uuid)
             & (db.issue.solved == False)
         )

    try:
        project_issues = db(query).select(fields_selected,
                                          cacheable = True,
                                          #cache = (cache.ram, 60),
                                          )
    except Exception as e:
        raise e
    return project_issues



def _last_project_issue_number(project_uuid):
    '''
    Obtiene un numero entero identificado por "last_project_issue_number"
    correspondiente al ultimo issue registrado en un proyecto determinado 
    por "project_uuid".
    '''
    
    project_issue = db(db.issue.project_uuid == project_uuid).select(
        db.issue.project_issue_number,
        orderby=~db.issue.id,
        limitby=(0,1),
        cacheable=True).first()

    if project_issue:
        # incrementamos el contador del issue en el proyecto
        project_issue_number = project_issue['project_issue_number'] + 1
    else:
        # si no existe, entonces esta es la primera issue
        project_issue_number = 1

    return project_issue_number


