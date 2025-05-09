import logging
import random
import time
from flask import Flask, render_template_string, request

# ✅ OpenTelemetry 관련 import
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME

# Flask + APM 설정
app = Flask(__name__)

# ✅ OpenTelemetry 초기화
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "flask-apm"})  # 서비스명 지정
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name="43.202.49.44",  # ← 여기에 Jaeger 서버 IP (예: 3.34.123.45)
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
FlaskInstrumentor().instrument_app(app)

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
    <button onclick="triggerLog('info')">거래 발생</button>
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
        return "ERROR"
    else:
        delay_ms = random.randint(0, 1000)
        time.sleep(delay_ms / 1000.0)
        app.logger.info(f"✅ 거래 발생 (응답시간: {delay_ms}ms)")
        return f"거래 발생 (응답시간 : {delay_ms}ms)"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
