"""made a separate file for these to avoid clutter
also made them w/ JSON encoding in mind since that's what im more used to; still based on abnf protocol
written. the goal with all these functions is basically to return a dictionary that matches the protocol
specs while being flexible with input
"""



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

#don't really need text to be a parameter but wasn't sure what the default message should be,
#feel free to change
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
                "update": "post",
                "data": {
                    "id": post_id,
                    "sender": sender,
                    "date": date,
                    "subject": subject
                }
            }
        }
    }

#updates the members of the group
def make_group_update(group:str, user_list):
    return {
        "tffp": {
            "type": "hoot",
            "body": {
                "group": group,
                "update": "users",
                "data": user_list
            }
        }
    }