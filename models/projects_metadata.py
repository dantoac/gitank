
def _get_project_issue_progress(project_uuid):
    solved_count = db((db.issue.project_uuid == project_uuid)
                      &(db.issue.solved==True)).count()
    
    total_count = db((db.issue.project_uuid == project_uuid)).count() or 100

    progress = solved_count * 100 / total_count

    return progress
