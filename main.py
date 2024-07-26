from permissions import clear_permissions, set_permission, create_user
from auth import AuthZ
from db import SQLiteClient

def get_posts():
    db_client = SQLiteClient(db_string="main.db")
    db_client.open_connection()
    res = db_client.execute("select * from posts").fetchall()
    return list(res)

clear_permissions(user_id=1)
auth_client = AuthZ(db_string="main.db")

# Uncomment this the first time you run to create a user. 
# Save the user_id and access_token for future use.
# res = create_user(email="test@gmail.com")
# print(res)

# Replace these values
user_id = 1
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.rpWgOBaCjeZW-34cmFQLmbJQ1gRbTyy-bycPYXc5Zts"

# =====================================================================================================================
# User tries to read values but doesn't have adequate permission.
res = auth_client.auth_execute(query="select id, content from posts", access_token=access_token)
print(res)

# Adding the permission to read content still doesn't give enough permission.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="column", column="content")
res = auth_client.auth_execute(query="select id, content from posts", access_token=access_token)
print(res)

# Having read permission on both columns finally alows them to access.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="column", column="id")
res = auth_client.auth_execute(query="select id, content from posts", access_token=access_token)
print(res)

clear_permissions(user_id=1)

# With full table read permission, the user can successfully query.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="table")
res = auth_client.auth_execute(query="select id, content from posts", access_token=access_token)
print(res)

# User tries to insert values into content column without having access and is denied because they don't have table
# level write access or column level write access for each column.
set_permission(user_id=user_id, table_name="posts", access_level="rw", type="column", column="id")
res = auth_client.auth_execute(query="insert into posts (id, content) values (4, 'post 4')", access_token=access_token)
print(res)
print(get_posts())

# Adding the permission to write to content allows them to modify the table.
set_permission(user_id=user_id, table_name="posts", access_level="rw", type="column", column="content")
res = auth_client.auth_execute(query="update posts set content = 'new content' where id = 1", access_token=access_token)
print(get_posts())

clear_permissions(user_id=1)

# With full table level write access, they can also modify the table.
set_permission(user_id=user_id, table_name="posts", access_level="rw", type="table")
res = auth_client.auth_execute(query="update posts set content = 'new content 2' where id = 1", access_token=access_token)
print(get_posts())

clear_permissions(user_id=1)

# Only having access to some of the data results in access denied.
set_permission(user_id=user_id, table_name="posts", access_level="rw", type="table")
res = auth_client.auth_execute(query="select * from posts join comments on posts.id = comments.post_id", access_token=access_token)
print(res)

# With full table access to both, the user can query.
set_permission(user_id=user_id, table_name="comments", access_level="rw", type="table")
res = auth_client.auth_execute(query="select * from posts join comments on posts.id = comments.post_id", access_token=access_token)
print(res)

clear_permissions(user_id=1)

# Without full column access to all the necessary columns, the user is denied.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="column", column="id")
set_permission(user_id=user_id, table_name="comments", access_level="r", type="column", column="content")
set_permission(user_id=user_id, table_name="comments", access_level="r", type="column", column="id")
res = auth_client.auth_execute(query="select posts.content, comments.content from posts join comments on posts.id = comments.post_id", access_token=access_token)
print(res)

# With full column access to all the necessary columns, they can query.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="column", column="content")
set_permission(user_id=user_id, table_name="comments", access_level="r", type="column", column="post_id")
res = auth_client.auth_execute(query="select posts.content, comments.content from posts join comments on posts.id = comments.post_id", access_token=access_token)
print(res)

clear_permissions(user_id=user_id)

# With mixed table-level and row-level permissions, the user can query.
set_permission(user_id=user_id, table_name="posts", access_level="r", type="table")
set_permission(user_id=user_id, table_name="comments", access_level="r", type="column", column="post_id")
set_permission(user_id=user_id, table_name="comments", access_level="r", type="column", column="content")
res = auth_client.auth_execute(query="select posts.content, comments.content from posts join comments on posts.id = comments.post_id", access_token=access_token)
print(res)
# =====================================================================================================================
