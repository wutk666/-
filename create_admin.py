from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("当前用户：", [(u.id, u.username, u.password[:30] + ('...' if len(u.password)>30 else '')) for u in users])

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("已创建 admin / admin")
    else:
        admin.set_password('admin')
        db.session.commit()
        print("已重置 admin 密码为 admin")