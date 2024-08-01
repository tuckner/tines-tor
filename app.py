from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

@app.route('/fetch', methods=['POST'])
def proxy():
    # Get the request body
    body = request.json
    
    # Extract full URL and data from the request body
    url = body.get('url')
    data = body.get('data', {})
    method = body.get('method', 'GET').upper()

    if not url:
        return jsonify({"error": "url is required"}), 400

    # Forward the request
    try:
        proxies = dict(
            http='socks5h://host:port',
            https='socks5h://host:port'
        )
        resp = requests.request(
            method=method,
            url=url,
            headers={key: value for (key, value) in request.headers if key.lower() not in ['host', 'content-length']},
            json=data if method in ['POST', 'PUT', 'PATCH'] else None,
            params=data if method == 'GET' else None,
            cookies=request.cookies,
            allow_redirects=False,
            proxies=proxies
        )

        # Create the response object
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)
    
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)