# API Reference

## Tool: inject_urls_into_prompt

**Endpoint:**
```
POST /mcp/tool/inject_urls_into_prompt
```

**Input:**
- `user_prompt` (string): The original prompt provided by the user.

**Output:**
- (string) The original prompt, augmented with up to 10 relevant URLs as a Markdown list.

**Example:**
```
{
  "user_prompt": "How do I implement a REST API in Python using Flask?"
}
```

**Response:**
```
How do I implement a REST API in Python using Flask?

Here are some relevant resources:
- https://realpython.com/flask-rest-api/
- https://flask.palletsprojects.com/en/2.0.x/tutorial/
- https://stackoverflow.com/questions/12364942/developing-restful-apis-with-python-and-flask
```

---

## Health Check

**Endpoint:**
```
GET /health
```
**Response:**
- `200 OK` with body `OK`

---

## Metrics (Prometheus)

**Endpoint:**
```
GET /metrics
```
**Response:**
- Prometheus-formatted metrics for requests and latency.

**How to use:**
- Add your server to your Prometheus config:
  ```yaml
  scrape_configs:
    - job_name: 'url-injector-mcp'
      static_configs:
        - targets: ['yourdomain.example.com:8000']
  ``` 