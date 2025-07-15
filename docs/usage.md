# Usage Guide

## Tool: `inject_urls_into_prompt`

This tool takes a user prompt and returns the same prompt augmented with up to 10 relevant URLs as a Markdown list.

### Example Request

**Endpoint:**
```
POST /mcp/tool/inject_urls_into_prompt
```

**Headers:**
```
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

**Body:**
```
{
  "user_prompt": "How do I implement a REST API in Python using Flask?"
}
```

### Example Response
```
How do I implement a REST API in Python using Flask?

Here are some relevant resources:
- https://realpython.com/flask-rest-api/
- https://flask.palletsprojects.com/en/2.0.x/tutorial/
- https://stackoverflow.com/questions/12364942/developing-restful-apis-with-python-and-flask
```

## Health Check

```
GET /health
```
Returns `200 OK` with body `OK`.

## Error Responses
- `401 Unauthorized`: Missing or invalid API key.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Unexpected error (see logs for details).

## Performance

- The server caches web search results for 10 minutes to improve speed and reduce duplicate requests. 