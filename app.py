import logging
from flask import Flask, render_template_string, request

app = Flask(__name__)

# 로깅 설정
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('flask_app.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

setup_logging()

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Logging Buttons</title>
    <script>
        async function triggerLog(level) {
            const res = await fetch('/trigger-log', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'level=' + level
            });
            const text = await res.text();
            document.getElementById('log-result').innerText = text;
        }
    </script>
</head>
<body>
    <h2>로그 발생 버튼</h2>
    <button onclick="triggerLog('info')">INFO 로그 발생</button>
    <button onclick="triggerLog('error')">ERROR 로그 발생</button>
    <p id="log-result" style="margin-top:10px; color:green;"></p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/trigger-log', methods=['POST'])
def trigger_log():
    level = request.form.get('level', 'info')
    if level == 'error':
        app.logger.error("❌ ERROR 로그가 발생했습니다.")
        return "ERROR 로그 발생 완료!"
    else:
        app.logger.info("✅ INFO 로그가 발생했습니다.")
        return "INFO 로그 발생 완료!"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
