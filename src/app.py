import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
posts = {
    1: {
        "id": 1,
        "upvotes": 1,
        "title": "My cat is the cutest!",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98",
    },
    2: {
        "id": 2,
        "upvotes": 3,
        "title": "Check out my new puppy!",
        "link": "https://i.imgur.com/puppy.jpg",
        "username": "doglover42",
    },
}
comments = {
    1: {
        "id": 1,
        "upvotes": 12,
        "text": "wow my first reddit gold!",
        "username": "alicia98",
    }
}
post_id_counter = 3  # one more than the current tasks for create


# get all posts, without returning their comments
@app.route("/posts/")
def get_posts():
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200


# create a post it starts with no comments by default
@app.route("/posts/", methods=["POST"])
def create_post():
    """
    {
        "title": "hello post",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "randy1234"
    }
    """
    global post_id_counter
    body = json.loads(request.data)
    title = body["title"]
    link = body["link"]
    username = body["username"]

    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username,
    }
    posts[post_id_counter] = post
    post_id_counter += 1
    return json.dumps(post), 201


# get a specific post by its "id" not including any of its comments
@app.route("/posts/<int:post_id>/")
def get_post_by_id(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found:"}), 404
    return json.dumps(post), 200


# delete a specific post by its id. this action also deletes that post's comments if it had any.
@app.route("/posts/<int:post_id>/", methods=["DELETE"])
def remove_post_by_id(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200


# get comments for a specific post
@app.route("/posts/<int:post_id>/comments/")
def get_comments_by_id(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404


# post a comment for a specific post

# edit a comment for a specific post


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
