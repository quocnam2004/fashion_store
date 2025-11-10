from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .utils import load_products, load_users, load_history
from app.account_module import append_purchase
import csv, os

app_routes = Blueprint(
    'app_routes',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# ---------------- LOAD DATA ----------------
PRODUCTS = load_products()
USERS = load_users()
HISTORY = load_history()


def find_user(username):
    return next((u for u in USERS if str(u.get('username')) == str(username)), None)


def get_product_by_id(pid):
    return next((p for p in PRODUCTS if str(p.get('id')) == str(pid)), None)


# ---------------- HOME PAGE ----------------
@app_routes.route('/')
def index():
    # reload products mỗi lần truy cập (không cần restart khi thay CSV)
    products_all = load_products()

    # phân trang
    per_page = 8
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except Exception:
        page = 1

    total = len(products_all)
    start = (page - 1) * per_page
    end = start + per_page
    products = products_all[start:end]

    total_pages = (total + per_page - 1) // per_page

    # featured có thể là top N từ products_all
    featured = products_all[:8]

    return render_template(
        'index.html',
        products=products,
        featured=featured,
        page=page,
        total_pages=total_pages
    )



# ---------------- CATEGORY PAGE ----------------
@app_routes.route('/category/<cat>')
def category(cat):
    # Dùng gender thay vì category
    prods = [
        p for p in PRODUCTS
        if (p.get('gender', '').lower() == cat.lower() or cat == 'all')
    ]

    # Lọc thêm
    size = request.args.get('size', '').strip()
    color = request.args.get('color', '').strip()
    if size:
        prods = [p for p in prods if size.lower() in str(p.get('size', '')).lower()]
    if color:
        prods = [p for p in prods if color.lower() in str(p.get('color', '')).lower()]

    # Sắp xếp
    sort = request.args.get('sort', 'new')
    if sort == 'price_asc':
        prods = sorted(prods, key=lambda x: float(x.get('price') or 0))
    elif sort == 'price_desc':
        prods = sorted(prods, key=lambda x: -float(x.get('price') or 0))

    # Phân trang
    per_page = 8
    page = int(request.args.get('page', 1))
    total = len(prods)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = prods[start:end]
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'category.html',
        cat=cat,
        products=paginated,
        page=page,
        total_pages=total_pages
    )





# ---------------- PRODUCT DETAIL ----------------
@app_routes.route('/product/<int:pid>')
def product_detail(pid):
    p = get_product_by_id(pid)
    if not p:
        return "Sản phẩm không tồn tại", 404
    similar = [x for x in PRODUCTS if x.get('category') == p.get('category') and x.get('id') != p.get('id')][:4]
    return render_template('product_detail.html', product=p, similar=similar)


# ---------------- CART ----------------
@app_routes.route('/cart')
def cart():
    cart = session.get('cart', {})
    items, total = [], 0
    for pid, qty in cart.items():
        prod = get_product_by_id(pid)
        if prod:
            subtotal = int(float(prod.get('price') or 0)) * int(qty)
            total += subtotal
            items.append({'product': prod, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total=total)


@app_routes.route('/cart/add/<pid>', methods=['POST', 'GET'])
def cart_add(pid):
    qty = int(request.form.get('qty', 1)) if request.method == 'POST' else 1
    cart = session.get('cart', {})
    cart[str(pid)] = cart.get(str(pid), 0) + qty
    session['cart'] = cart
    flash('Đã thêm vào giỏ hàng', 'success')
    return redirect(url_for('app_routes.cart'))


@app_routes.route('/cart/remove/<pid>')
def cart_remove(pid):
    cart = session.get('cart', {})
    if pid in cart:
        cart.pop(pid)
        session['cart'] = cart
    return redirect(url_for('app_routes.cart'))


# ---------------- CHECKOUT ----------------
@app_routes.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # ... phần code hiện tại bạn đang có (tính tổng tiền, xử lý form, v.v.)

    if request.method == 'POST':
        # Ví dụ bạn có giỏ hàng dạng list trong session
        cart = session.get('cart', [])
        total_price = 0

        for item in cart:
            total_price += float(item['price']) * int(item['quantity'])

        # Kiểm tra người dùng đã đăng nhập chưa
        user = session.get('user')
        if not user:
            flash('Vui lòng đăng nhập để hoàn tất thanh toán', 'danger')
            return redirect(url_for('account.login'))

        # Lưu từng sản phẩm vào lịch sử
        for item in cart:
            append_purchase(
                user_id=user['id'],
                product_id=item['id'],
                quantity=item['quantity'],
                total_spent=float(item['price']) * int(item['quantity'])
            )

        # Sau khi lưu, xóa giỏ hàng
        session['cart'] = []
        flash('Thanh toán thành công! Đơn hàng đã được lưu vào lịch sử mua hàng.', 'success')
        return redirect(url_for('account.account_history'))

    return render_template('checkout.html')


# ---------------- AUTH ----------------
@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = find_user(username)
        if user and str(user.get('password', '')) == password:
            session['user'] = user.get('username')
            session['role'] = user.get('role', 'user')
            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('app_routes.index'))
        flash('Sai username hoặc password', 'danger')
    return render_template('login.html')


@app_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        fullname = request.form.get('fullname', '').strip()
        if find_user(username):
            flash('Tài khoản đã tồn tại', 'warning')
            return redirect(url_for('app_routes.register'))

        # Ghi vào CSV
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        users_csv = os.path.join(base, 'users.csv')
        with open(users_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([username, password, 'user', fullname, ''])
        global USERS
        USERS = load_users()
        flash('Đăng ký thành công. Hãy đăng nhập.', 'success')
        return redirect(url_for('app_routes.login'))
    return render_template('register.html')


@app_routes.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('app_routes.index'))


# ---------------- ACCOUNT ----------------
@app_routes.route('/account')
def account():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để xem thông tin cá nhân', 'warning')
        return redirect(url_for('app_routes.login'))
    user = find_user(session.get('user'))
    return render_template('account.html', user=user)


# ---------------- ADMIN ----------------
@app_routes.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Bạn cần quyền admin để truy cập', 'warning')
        return redirect(url_for('app_routes.login'))
    return render_template('admin_dashboard.html', products=PRODUCTS)


# ---------------- ABOUT ----------------
@app_routes.route('/about')
def about():
    return render_template('about.html')


# ---------------- CONTACT ----------------
@app_routes.route('/contact')
def contact():
    return render_template('contact.html')
