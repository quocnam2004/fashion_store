# app/account_module.py
# Flask module quản lý người dùng (đăng ký, đăng nhập, lưu lịch sử mua hàng)
# Dữ liệu được lưu trong CSV (users.csv, history.csv)
# ======================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os, json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Blueprint Flask
account_bp = Blueprint('account', __name__, template_folder='templates')

# --- Đường dẫn file CSV ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
HISTORY_CSV = os.path.join(DATA_DIR, 'history.csv')


# --- Hàm tiện ích ---
def ensure_files():
    """Tạo file CSV mẫu nếu chưa tồn tại"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_CSV):
        users_df = pd.DataFrame(columns=[
            'id', 'username', 'email', 'password_hash', 'role',
            'gender', 'age', 'location', 'preferred_color',
            'preferred_brand', 'favorite_category', 'last_login'
        ])
        users_df.to_csv(USERS_CSV, index=False, encoding='utf-8-sig')

    if not os.path.exists(HISTORY_CSV):
        history_df = pd.DataFrame(columns=['user_id', 'purchases'])
        history_df.to_csv(HISTORY_CSV, index=False, encoding='utf-8-sig')


def load_users():
    ensure_files()
    return pd.read_csv(USERS_CSV, dtype=str).fillna('')


def save_users(df):
    df.to_csv(USERS_CSV, index=False, encoding='utf-8-sig')


def load_history():
    ensure_files()
    return pd.read_csv(HISTORY_CSV, dtype=str).fillna('')


def save_history(df):
    df.to_csv(HISTORY_CSV, index=False, encoding='utf-8-sig')


# --- User ---
def find_user_by_email(email):
    df = load_users()
    rows = df[df['email'].str.lower() == str(email).lower()]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def find_user_by_id(uid):
    df = load_users()
    rows = df[df['id'] == str(uid)]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def create_user(username, email, raw_password, gender='', age='', location='', preferred_color='', preferred_brand='', favorite_category=''):
    df = load_users()
    if not df.empty and (df['email'].str.lower() == email.lower()).any():
        return None, "Email đã tồn tại!"

    new_id = 1
    if not df.empty:
        try:
            new_id = int(df['id'].astype(int).max()) + 1
        except Exception:
            new_id = len(df) + 1

    hashed = generate_password_hash(raw_password)
    new_user = {
        'id': str(new_id),
        'username': username,
        'email': email,
        'password_hash': hashed,
        'role': 'user',
        'gender': gender,
        'age': age,
        'location': location,
        'preferred_color': preferred_color,
        'preferred_brand': preferred_brand,
        'favorite_category': favorite_category,
        'created_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'last_login': ''
    }

    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    save_users(df)
    return new_user, None



# --- History ---
def get_user_history(user_id):
    df = load_history()
    rows = df[df['user_id'] == str(user_id)]
    if rows.empty:
        return []
    try:
        return json.loads(rows.iloc[0]['purchases']) if rows.iloc[0]['purchases'] else []
    except Exception:
        return []


def append_purchase(user_id, product_id, quantity, total_spent):
    df = load_history()
    rows = df[df['user_id'] == str(user_id)]
    new_purchase = {
        'product_id': int(product_id),
        'quantity': int(quantity),
        'total_spent': float(total_spent),
        'purchased_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    if rows.empty:
        new_row = {'user_id': str(user_id), 'purchases': json.dumps([new_purchase])}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        idx = rows.index[0]
        existing = []
        try:
            existing = json.loads(df.at[idx, 'purchases']) if df.at[idx, 'purchases'] else []
        except Exception:
            pass
        existing.append(new_purchase)
        df.at[idx, 'purchases'] = json.dumps(existing)
    save_history(df)


# --- ROUTES ---
@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        gender = request.form.get('gender', '')
        age = request.form.get('age', '')
        location = request.form.get('location', '')
        preferred_color = request.form.get('preferred_color', '')
        preferred_brand = request.form.get('preferred_brand', '')
        favorite_category = request.form.get('favorite_category', '')

        if not username or not email or not password:
            flash('Vui lòng nhập đầy đủ thông tin', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Mật khẩu nhập lại không khớp', 'danger')
            return render_template('register.html')

        user, err = create_user(
            username=username,
            email=email,
            raw_password=password,
            gender=gender,
            age=age,
            location=location,
            preferred_color=preferred_color,
            preferred_brand=preferred_brand,
            favorite_category=favorite_category
        )

        if err:
            flash(err, 'danger')
            return render_template('register.html')

        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('account.login'))

    return render_template('register.html')




@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('email').strip()  # có thể là username hoặc email
        password = request.form.get('password')

        users = load_users()
        # tìm user theo email hoặc username
        user_row = users[
            (users['email'].str.lower() == identifier.lower()) |
            (users['username'].str.lower() == identifier.lower())
        ]

        # nếu không tìm thấy
        if user_row.empty:
            flash('Sai tên người dùng hoặc mật khẩu', 'danger')
            return render_template('login.html')

        user = user_row.iloc[0].to_dict()

        # kiểm tra mật khẩu
        if not check_password_hash(user['password_hash'], password):
            flash('Sai tên người dùng hoặc mật khẩu', 'danger')
            return render_template('login.html')

        # đăng nhập thành công
        session['user'] = user
        flash(f"Xin chào {user['username']}!", 'success')
        return redirect(url_for('account.account'))

    return render_template('login.html')



@account_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Bạn đã đăng xuất', 'info')
    return redirect(url_for('account.login'))


@account_bp.route('/account')
def account():
    user = session.get('user')
    if not user:
        return redirect(url_for('account.login'))
    user_info = find_user_by_id(user['id'])
    return render_template('account.html', user=user_info)


@account_bp.route('/account/history')
def account_history():
    user = session.get('user')
    if not user:
        return redirect(url_for('account.login'))
    purchases = get_user_history(user['id'])
    return render_template('account_history.html', purchases=purchases)
