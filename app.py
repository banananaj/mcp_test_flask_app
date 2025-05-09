import logging
import random
import time
from flask import Flask, render_template_string, request

app = Flask(__name__)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('flask_app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

setup_logging()

# HTML 템플릿 (버튼 포함)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Logging Test</title></head>
<body>
    <h2>로그 발생 버튼</h2>
    <form method="POST" action="/trigger-log">
        <button type="submit">로그 발생시키기</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/trigger-log', methods=['POST'])
def trigger_log():
    delay_ms = random.randint(0, 1000)
    time.sleep(delay_ms / 1000.0)  # ms → sec
    app.logger.info(f"✅ 버튼 클릭됨. {delay_ms}ms 지연 후 로그 발생")
    return f"로그 발생 완료! ({delay_ms}ms 지연)"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
