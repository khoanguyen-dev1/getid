import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
port = int(os.getenv('PORT', 8080))


# Cấu hình logging
logger = logging.getLogger('api_usage')
logger.setLevel(logging.INFO)

# Sử dụng thư mục tạm cho logs
log_file_path = '/tmp/api_usage.log'  # Đường dẫn lưu log cho Vercel
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_client_ip():
    """Hàm để lấy địa chỉ IP của client, xem xét cả trường hợp đằng sau proxy."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/user', methods=['GET'])
def get_user_id():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Please Enter Username'}), 400

    try:
        response = requests.post(
            'https://users.roblox.com/v1/usernames/users',
            json={"usernames": [username]}
        )
        response_data = response.json()

        if 'data' not in response_data or len(response_data['data']) == 0:
            return jsonify({'error': 'User Not Found In Database!'}), 400

        user_id = response_data['data'][0]['id']
        return jsonify({'id': user_id , 'credit' : 'UwU'})
    except requests.RequestException as req_err:
        logger.error(f"Request error: {req_err}")
        return jsonify({'error': 'Request failed, please try again later'}), 500
    except ValueError as json_err:
        logger.error(f"JSON parsing error: {json_err}")
        return jsonify({'error': 'Failed to parse response from the server'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Đảm bảo rằng debug=False trong môi trường sản xuất
    )
