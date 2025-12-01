"""made a separate file for these to avoid clutter
also made them w/ JSON encoding in mind since that's what im more used to; still based on abnf protocol
written. the goal with all these functions is basically to return a dictionary that matches the protocol
specs while being flexible with input
"""

def make_login_request(username: str):
    return {
        "tffp":{
            "type":"seek",
            "body":{
                "command":"login",
                "args":username
            }
        }
    }

def make_sign_up_request(username: str):
    return {
        "tffp":{
            "type":"seek",
            "body":{
                "command":"sign_up",
                "args":username
            }
        }
    }

#returns message for users who are trying to join some group
def make_join_request(group: str):
    return {
        "tffp":{
            "type":"seek",
            "body":{
                "group": group,
                "command":"join"
            }
        }
    }

def make_leave_request(group: str):
    return {
        "tffp":{
            "type":"seek",
            "body":{
                "group": group,
                "command":"leave"
            }
        }
    }

#message for making a new post to group
def make_new_post_request(group:str, subject:str, content:str):
    return {
        "tffp": {
            "type": "seek",
            "body": {
                "group": group,
                "command": "post",
                "args": {
                    "subject": subject,
                    "content": content
                }
            }
        }
    }

#requesting a previous message's content by id
def make_content_request(group:str, post_id:int):
    return {
        "tffp": {
            "type": "seek",
            "body": {
                "group": group,
                "command": "content",
                "args": post_id
            }
        }
    }

#requests a list of the group's users
def make_group_users_request(group):
    return {
        "tffp": {
            "type": "seek",
            "body": {
                "group": group,
                "command": "users"
            }
        }
    }

#sends request to remove user from all groups and terminate connection
def make_quit_request():
    return {
        "tffp": {
            "type": "seek",
            "body": {
                "group": "public",
                "command": "quit"
            }
        }
    }


#requests a list of all groups from the server
def make_groups_request():
    return {
        "tffp": {
            "type": "seek",
            "body": {
                "group":"public",
                "command": "groups"
            }
        }
    }

#server accepts user request
def make_accept_response(text:str):
    return {
        "tffp": {
            "type": "good",
            "body": text
        }
    }

#server denies user request
def make_deny_response(text:str):
    return {
        "tffp": {
            "type": "moot",
            "body": text
        }
    }

#updates posts for everyone in the group with a new post
def make_new_post_update(group:str, post_id:int, sender:str, date:str, subject:str):
    return {
        "tffp": {
            "type": "hoot",
            "body": {
                "group": group,
                "command": "post",
                "args": {
                    "id": post_id,
                    "sender": sender,
                    "date": date,
                    "subject": subject
                }
            }
        }
    }

#updates that a user has joined
def make_join_update(group:str, user:str):
    return {
        "tffp": {
            "type": "hoot",
            "body": {
                "group": group,
                "command": "join",
                "args": user
            }
        }
    }

#updates that a user has left
def make_leave_update(group:str, user:str):
    return {
        "tffp": {
            "type": "hoot",
            "body": {
                "group": group,
                "command": "leave",
                "args": user
            }
        }
    }
