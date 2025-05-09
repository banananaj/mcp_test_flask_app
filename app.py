import logging
import random
import time
from flask import Flask, render_template_string, request

# ✅ OpenTelemetry 관련 import
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# ✅ 로깅 (OpenTelemetry 내부 디버깅용, 선택)
logging.basicConfig(level=logging.INFO)

# Flask 앱 정의
app = Flask(__name__)

# ✅ TracerProvider → OTLP Exporter 연결
provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "flask-apm"})
)
trace.set_tracer_provider(provider)

# 👇 OTLP Exporter 설정 (Jaeger OTLP HTTP 수신 포트 사용)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://43.202.49.44:4318/v1/traces",  # ← EC2 A (Jaeger 서버) IP
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

# ✅ Flask 자동 계측
FlaskInstrumentor().instrument_app(app)

# ✅ 로깅 설정
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

# ✅ HTML 템플릿
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

# ✅ 라우트 정의
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/trigger-log', methods=['POST'])
def trigger_log():
    tracer = trace.get_tracer(__name__)
    level = request.form.get('level', 'info')

    # ✅ 명시적 span 생성
    with tracer.start_as_current_span("trigger-log-span"):
        if level == 'error':
            app.logger.error("❌ ERROR 로그가 발생했습니다.")
            return "ERROR"
        else:
            delay_ms = random.randint(0, 1000)
            time.sleep(delay_ms / 1000.0)
            app.logger.info(f"✅ 거래 발생 (응답시간: {delay_ms}ms)")
            return f"거래 발생 (응답시간 : {delay_ms}ms)"

# ✅ 서버 실행
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
