from flask import Flask, request, Response, jsonify
import requests
import stem.process
import stem.util.log
import time

stem.util.log.get_logger().setLevel(stem.util.log.DEBUG)

app = Flask(__name__)

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print(line)

def start_tor():
    start = stem.process.launch_tor_with_config(
        config = {
            'SocksPort': '6000',
            'ExitNodes': '{US}',
        },
        init_msg_handler = print_bootstrap_lines,
    )
    return start

tor_process = start_tor()

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
            http=f'socks5h://127.0.0.1:6000',
            https=f'socks5h://127.0.0.1:6000'
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
    try:
        app.run(debug=True)
    finally:
        tor_process.kill()  # stops tor when the app is terminated