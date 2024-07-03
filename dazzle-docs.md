# Dazzle library

Dazzle is a helper library for Snazzle that helps get things from ScratchDB and the Scratch API.

## Functions

### fmt_time(timestamp)
Formats a timestamp to a human-readable format.

- `timestamp` (str): The timestamp to format.

### set_server_host(host)
Sets the server host for the application.

- `host` (str): The host to set.

### use_scratchdb(value)
Force ScratchDB usage.

- `value` (bool): True to force ScratchDB usage, False otherwise.

### replit_mode(value)
Enable Replit mode for Snazzle usage on Replit.

- `value` (bool): True to enable Replit mode, False otherwise.

### use_proxy(value)
Force proxy usage for Snazzle.

- `value` (bool): True to force proxy usage, False otherwise.

### remove_duplicates(input_list)
Removes duplicates from a list.

- `input_list` (list): The list to remove duplicates from.

Returns:
- list: A list that is a copy of `input_list`, but with duplicates removed.

### get_topics(category, page)
Gets topics in a subforum from ScratchDB.

- `category` (str): The category to retrieve topics from.
- `page` (int): The page number of topics to retrieve.

Returns:
- dict: A dictionary containing the error status and topics.

### get_post_info(post_id)
Gets information about a forum post from ScratchDB.

- `post_id` (str): The ID of the post to retrieve information for.

Returns:
- dict: Information about the forum post.

### get_author_of(post_id)
Gets the author of a forum topic.

- `post_id` (str): The ID of the post to retrieve the author for.

Returns:
- str: The author of the forum topic.

### get_project_info(project_id)
Gets information about a project from ScratchDB.

- `project_id` (str): The ID of the project to retrieve information for.

Returns:
- dict: Information about the project.

### get_comments(project_id)
Gets comments for a project.

- `project_id` (str): The ID of the project to retrieve comments for.

Returns:
- dict: Comments for the project.

### get_ocular(username)
Gets a user's status from Ocular.

- `username` (str): The username of the user.

Returns:
- dict: User's status information.

### get_aviate(username)
Gets a user's status from Aviate.

- `username` (str): The username of the user.

Returns:
- str: User's status.

### init_db()
Initializes the database.

### get_featured_projects()
Retrieves the featured projects from the Scratch API.

Returns:
- dict: Featured projects.

### get_topic_data(topic_id)
Gets data about a topic from ScratchDB.

- `topic_id` (str): The ID of the topic to retrieve data for.

Returns:
- dict: Topic data.

### get_trending_projects()
Gets trending projects from the Scratch API.

Returns:
- dict: Trending projects.

### get_topic_posts(topic_id, page=0, order="oldest")
Gets posts for a topic.

- `topic_id` (str): The ID of the topic to retrieve posts for.
- `page` (int): The page number of posts.
- `order` (str): The order of posts (oldest or newest).

Returns:
- dict: Topic posts.

### get_pfp_url(username, size=90)
Gets the profile picture URL for a user.

- `username` (str): The username of the user.
- `size` (int): The size of the profile picture.

Returns:
- str: Profile picture URL.

### get_redirect_url()
Gets the redirect URL for Scratch Auth.

Returns:
- str: Redirect URL.

### login(code)
Logs in a user with the provided code.

- `code` (str): The authentication code.

Returns:
- str: Session ID.

### token_matches_user(token)
Checks if the token matches the user.

- `token` (str): The token to check.

Returns:
- list: List of matching users.

### search_for_projects(q)
Searches for projects.

- `q` (str): The query string.

Returns:
- dict: Search results.

### get_studio_data(id)
Gets data about a studio.

- `id` (str): The ID of the studio.

Returns:
- dict: Studio data.

### get_studio_comments(id)
Gets comments for a studio.

- `id` (str): The ID of the studio.

Returns:
- None
