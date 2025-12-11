import re
import logging
from flask import Flask, request, jsonify, render_template, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from datetime import datetime, timedelta
from collections import defaultdict
import ipaddress

# ----------------------------
# 配置与初始化
# ----------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///xss_defense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------------------
# 数据模型
# ----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # 实际项目中应哈希存储

class AttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    blocked = db.Column(db.Boolean, default=True)

class BannedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False)
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)
    permanent = db.Column(db.Boolean, default=False)

# ----------------------------
# XSS 检测器
# ----------------------------
class XSSDetector:
    # 常见 XSS 特征正则（可扩展）
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript\s*:.*',
        r'on\w+\s*=\s*["\'][^"\']*["\']',
        r'<.*?(alert|eval|execScript)\s*\(.*?\)',
        r'expression\s*\(',
        r'vbscript\s*:',
    ]

    @staticmethod
    def detect(content: str) -> bool:
        if not content:
            return False
        content_lower = content.lower()
        for pattern in XSSDetector.XSS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                return True
        return False

    @staticmethod
    def sanitize(content: str) -> str:
        # 简单净化：移除危险标签（实际项目建议用 html-sanitizer 库）
        dangerous = ['<script>', '</script>', 'javascript:', 'vbscript:']
        for tag in dangerous:
            content = content.replace(tag, '')
        return content

# ----------------------------
# WSGI 中间件：XSS 防御核心
# ----------------------------
class XSSMiddleware:
    def __init__(self, flask_app, app_wsgi):
        self.flask_app = flask_app
        self.app_wsgi = app_wsgi
        self.detector = XSSDetector()
        self.ip_attack_count = defaultdict(int)  # 内存缓存，生产环境用 Redis

    def __call__(self, environ, start_response):
        # 获取 IP
        ip = environ.get('HTTP_X_FORWARDED_FOR', environ.get('REMOTE_ADDR', '127.0.0.1')).split(',')[0].strip()
        
        # 在访问数据库前确保有应用上下文
        with self.flask_app.app_context():
            # 检查 IP 是否被封禁
            if BannedIP.query.filter_by(ip=ip).first():
                self._log_attack(ip, "Blocked by IP ban", blocked=True)
                start_response('403 Forbidden', [('Content-Type', 'application/json')])
                return [b'{"error": "IP blocked"}']

        # 检查请求体（仅处理 POST JSON）
        if environ.get('REQUEST_METHOD') == 'POST' and environ.get('CONTENT_TYPE', '').startswith('application/json'):
            try:
                request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
                environ['wsgi.input'] = BytesIO(request_body)  # 重置流供 Flask 读取
                content = request_body.decode('utf-8', errors='ignore')
                
                if self.detector.detect(content):
                    # 记录攻击需要应用上下文
                    with self.flask_app.app_context():
                        self._log_attack(ip, content, blocked=True)
                    # 触发防御：返回拦截响应
                    response_body = b'{"error": "XSS attack detected and blocked"}'
                    start_response('400 Bad Request', [
                        ('Content-Type', 'application/json; charset=utf-8'),
                        ('Content-Length', str(len(response_body)))
                    ])
                    return [response_body]
            except Exception as e:
                logging.error(f"XSS Middleware error: {e}")

        # 正常请求
        return self.app_wsgi(environ, start_response)

    def _log_attack(self, ip: str, payload: str, blocked: bool = True):
        # 确保在调用处已进入 app_context，或者在此处再入一次以保险
        with self.flask_app.app_context():
            log = AttackLog(ip=ip, payload=payload[:500], blocked=blocked)
            db.session.add(log)
            db.session.commit()

# ----------------------------
# Flask 路由
# ----------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return "XSS 防御系统运行中！访问 /test_xss 进行测试"

@app.route('/test_xss', methods=['GET'])
def test_xss_page():
    return render_template('test_xss.html')

@app.route('/test_xss', methods=['POST'])
def test_xss_api():
    # 此路由会被中间件提前拦截（如果含 XSS）
    data = request.get_json()
    clean_input = XSSDetector.sanitize(data.get('input', ''))
    return jsonify({"message": f"安全输入: {clean_input}"})

@app.route('/ban_ip/<ip>')
@login_required
def ban_ip(ip):
    try:
        ipaddress.ip_address(ip)  # 验证 IP 格式
        if not BannedIP.query.filter_by(ip=ip).first():
            ban = BannedIP(ip=ip, permanent=True)
            db.session.add(ban)
            db.session.commit()
        return jsonify({"status": "IP 已封禁"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logs')
@login_required
def get_logs():
    logs = AttackLog.query.order_by(AttackLog.timestamp.desc()).limit(20).all()
    return jsonify([{
        'ip': log.ip,
        'payload': log.payload,
        'time': log.timestamp.isoformat(),
        'blocked': log.blocked
    } for log in logs])

# ----------------------------
# 初始化数据库 & 启动
# ----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建测试用户（用户名: admin, 密码: admin）
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin')  # 注意：实际项目必须哈希密码！
            db.session.add(admin)
            db.session.commit()
    
    # 应用中间件
    from io import BytesIO
    app.wsgi_app = XSSMiddleware(app, app.wsgi_app)
    
    app.run(debug=True, host='0.0.0.0', port=5000)