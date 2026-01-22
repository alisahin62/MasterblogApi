from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts with optional sorting.

    Query parameters:
        sort: Field to sort by ('title' or 'content'). Optional.
        direction: Sort order ('asc' or 'desc'). Optional, defaults to 'asc'.

    Returns:
        JSON list of posts, optionally sorted.
        Returns status 400 if invalid sort field or direction is provided.
    """
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction')

    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({"error": f"Invalid sort field '{sort_field}'. Allowed values are: {', '.join(valid_sort_fields)}"}), 400

    if sort_direction and sort_direction not in valid_directions:
        return jsonify({"error": f"Invalid direction '{sort_direction}'. Allowed values are: {', '.join(valid_directions)}"}), 400

    posts = POSTS.copy()

    if sort_field:
        reverse = sort_direction == 'desc'
        posts = sorted(posts, key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new blog post.

    Expects JSON with 'title' and 'content' fields.
    Returns the created post with a unique ID and status 201.
    Returns status 400 if required fields are missing.
    """
    data = request.get_json()

    missing_fields = []
    if not data or 'title' not in data:
        missing_fields.append('title')
    if not data or 'content' not in data:
        missing_fields.append('content')

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400


    new_id = max((post['id'] for post in POSTS), default=0) + 1

    new_post = {
        "id": new_id,
        "title": data['title'],
        "content": data['content']
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by title and/or content.

    Accepts query parameters 'title' and 'content'.
    Returns a list of posts matching the search criteria.
    Returns an empty list if no posts match.
    """
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = []
    for post in POSTS:
        title_match = title_query in post['title'].lower() if title_query else True
        content_match = content_query in post['content'].lower() if content_query else True

        if title_query or content_query:
            if (title_query and title_match) or (content_query and content_match):
                results.append(post)

    return jsonify(results)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a blog post by its ID.

    Returns a success message with status 200 if the post was deleted.
    Returns status 404 if no post with the given ID exists.
    """
    for post in POSTS:
        if post['id'] == post_id:
            POSTS.remove(post)
            return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

    return jsonify({"error": f"Post with id {post_id} not found."}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
