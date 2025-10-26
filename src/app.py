import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


# root endpoint included in the starter code
@app.route("/")
def hello_world():
    return "Hello world!"


# posts: Dict[int, Dict]
# Maps post_id -> post object.
# Post object schema:
# {
#   "id": int,
#   "upvotes": int,
#   "title": str,
#   "link": str(URL),
#   "username": str
# }
posts = {}
post_id_counter = 1  # one more than the current posts for create

# comments: Dict[int, Dict]
# Maps post_id -> { "comment_id_counter": int, "data": Dict[int, Comment] }
# - "comment_id_counter" is the next comment id to assign for that post.
# - "data" maps comment_id -> comment object.
# Comment object schema:
# {
#   "id": int,
#   "upvotes": int,
#   "text": str,
#   "username": str
# }
comments = {}


# get all posts, without returning their comments
@app.route("/api/posts/", methods=["GET"])
def get_posts():
    """List all posts (without their comments).
    Response JSON:
        {
        "posts": [Post, ...]
        }
    Status Codes:
        200: Success
    """
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200


# create a post it starts with no comments by default
@app.route("/api/posts/", methods=["POST"])
def create_post():
    """Create a new post.
    Request JSON:
        {
          "title": "hello post",
          "link": "https://i.imgur.com/jseZqNK.jpg",
          "username": "randy1234"
        }
    Status Codes:
        201: Created new post
        400: Missing/invalid fields
    """
    global post_id_counter
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")

    if not title or not link or not username:
        return json.dumps({"error": "Bad request"}), 400

    # initialize the post
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username,
    }
    posts[post_id_counter] = post
    # add to corresponding comments dict with 0 comments
    comments[post_id_counter] = {"comment_id_counter": 1, "data": {}}

    post_id_counter += 1
    return json.dumps(post), 201


# get a specific post by its "id" not including any of its comments
@app.route("/api/posts/<int:post_id>/", methods=["GET"])
def get_post_by_id(post_id):
    """get a single post (no comments).
    Path Params: post_id
    Status Codes:
        200: Success
        404: Post not found with id=post_id
    """
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps(post), 200


# delete a specific post by its id. this action also deletes that post's comments if it had any.
@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def remove_post_by_id(post_id):
    """Delete a post and all its comments.
    Path Params: post_id
    Status Codes:
        200: Deleted post and comments
        404: Post not found
    """
    # delete the post
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    # delete the comments, which are guaranteed to exist if the post existed
    del comments[post_id]
    # return the deleted post
    return json.dumps(post), 200


# GET all comments for post with id=post_id
@app.route("/api/posts/<int:post_id>/comments/", methods=["GET"])
def get_comments_by_id(post_id):
    """List all comments for a post.
    Path Params: post_id
    Response JSON:
        {
          "comment_id_counter": int,
          "data": { <comment_id>: Comment, ... }
        }
    Status Codes:
        200: Success (empty set allowed)
        404: Post not found
    """
    if not posts.get(post_id):
        return json.dumps({"error": "Post not found"}), 404
    post_comments = comments[post_id]["data"]
    return_comments = {"comments": list(post_comments.values())}
    return json.dumps(return_comments), 200


# POST a comment for a specific post with id=post_id. Initialize with 1 upvote and text = body["text"].
@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    """Create a new comment on a post.
    Path Params: post_id
    Request JSON:
        {
            "text": "what a cute puppy aww",
            "username": "raahi014"
        }
    Status Codes:
        201: Created new comment
        400: Missing/invalid text field
        404: Post not found
    """
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")

    if not text or not username:
        return json.dumps({"error": "Bad request"}), 400

    if not posts.get(post_id):
        return json.dumps({"error": "Post not found"}), 404

    comment = {
        "id": comments[post_id]["comment_id_counter"],
        "upvotes": 1,
        "text": text,
        "username": username,
    }
    comment_id = comments[post_id]["comment_id_counter"]
    comments[post_id]["comment_id_counter"] += 1
    comments[post_id]["data"][comment_id] = comment

    return json.dumps(comment), 201


# edit a comment for a specific post. this should only update the text field of the comment
@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def edit_comment(post_id, comment_id):
    """Edit an existing comment's text
    Path Params: post_id, comment_id
    Request JSON:
        {
            "text": "updated text"
        }
    Status Codes:
        200: Updated
        404: Post not found
        404: Comment not found
    """
    body = json.loads(request.data)
    text = body.get("text")

    if not text:
        return json.dumps({"error": "Bad request"}), 400

    if not posts.get(post_id):
        return json.dumps({"error": "Post not found"}), 404

    comment = comments[post_id]["data"].get(comment_id)

    if not comment:
        return json.dumps({"error": "Comment not found"}), 404

    comment["text"] = text  # pass by reference
    return json.dumps(comment), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
