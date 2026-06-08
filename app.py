import os
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
# استيراد النماذج والبيانات
from models import db, User, Property, PropertyImage, SavedSearch, SearchAlert
from data import MOCK_PROPERTIES

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GENAI_MODEL = os.getenv('GENAI_MODEL', 'gemini-1.5-flash')  # ✅ تم تصحيح اسم الموديل

try:
    if GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        genai = None
except Exception as e:
    print(f"Gemini integration disabled: {e}")
    genai = None

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///realestate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ─── HOME ────────────────────────────────────────────────────────────────────
@app.route('/')
def home_view():
    db_properties = Property.query.filter_by(status='approved').all()
    if not db_properties:
        properties = MOCK_PROPERTIES
        cities = list(set(p['city'] for p in MOCK_PROPERTIES if 'city' in p))
    else:
        properties = [p.to_dict() for p in db_properties]
        cities = [r[0] for r in db.session.query(Property.city).filter_by(status='approved').distinct().all()]

    city_branding = {
        'New Cairo': {'icon': 'building-2', 'color': 'blue'},
        '6th of October': {'icon': 'warehouse', 'color': 'indigo'},
        'New Administrative Capital': {'icon': 'landmark', 'color': 'cyan'},
        'Mostakbal City': {'icon': 'city', 'color': 'emerald'},
        'Ain Sokhna': {'icon': 'waves', 'color': 'yellow'},
        'North Coast': {'icon': 'umbrella', 'color': 'blue'},
        'El Gouna': {'icon': 'home', 'color': 'rose'},
        'New Heliopolis': {'icon': 'layout', 'color': 'purple'},
        'Nasr City': {'icon': 'building', 'color': 'slate'},
        'El Shorouk': {'icon': 'tree-pine', 'color': 'green'},
        'Badr': {'icon': 'factory', 'color': 'orange'},
    }

    saved_ids = {p.id for p in current_user.saved_list} if current_user.is_authenticated else set()
    for p in properties:
        p['is_saved'] = p.get('id') in saved_ids

    return render_template('home.html', properties=properties, cities=cities, city_branding=city_branding)

# ─── MAP ─────────────────────────────────────────────────────────────────────
@app.route('/map')
def map_view():
    db_properties = Property.query.filter_by(status='approved').all()
    properties = [p.to_dict() for p in db_properties] if db_properties else MOCK_PROPERTIES
    cities = list(set(p['city'] for p in properties))

    saved_ids = {p.id for p in current_user.saved_list} if current_user.is_authenticated else set()
    for p in properties:
        p['is_saved'] = p.get('id') in saved_ids

    return render_template('map.html', properties=properties, cities=cities)

# ─── ABOUT ───────────────────────────────────────────────────────────────────
@app.route('/about')
def about():
    return render_template('about.html')

# ─── CHATBOT ─────────────────────────────────────────────────────────────────

def detect_language(text):
    if not text:
        return 'en'
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    return 'en'


def summarize_properties(properties, max_items=6):
    summary = []
    for p in (properties or [])[:max_items]:
        title = p.get('title') or 'Property'
        city = p.get('city') or 'Unknown'
        listing_type = p.get('listing_type') or 'buy'
        price = p.get('price') or 'Price unavailable'
        beds = p.get('bedrooms') if p.get('bedrooms') is not None else 'N/A'
        summary.append(f"- {title} | {city} | {listing_type} | {price} | {beds} beds")
    return "\n".join(summary)


def build_gemini_prompt(user_message, history, properties_data, language):
    summaries = summarize_properties(properties_data, max_items=6)
    lang_instruction = (
        "إذا كتب المستخدم باللغة العربية، أجب بالعربية. "
        "إذا كتب المستخدم باللغة الإنجليزية، أجب بالإنجليزية."
        if language == 'ar' else
        "If the user writes in Arabic, answer in Arabic. If the user writes in English, answer in English."
    )
    instructions = (
        "أنت مساعد عقاري ودود لـ Dalilak. قدم اقتراحات واضحة ومفيدة حول العقارات المتاحة، "
        "وإلا اطلب مزيداً من المعلومات إذا كان الطلب غير مكتمل."
        if language == 'ar' else
        "You are a friendly real estate assistant for Dalilak. Offer clear, helpful suggestions about available properties, "
        "or ask for more details if the user's request is incomplete."
    )
    history_text = "\n".join([
        f"{item.get('role', 'user')}: {item.get('content', '')}"
        for item in (history or [])
    ])

    prompt = (
        f"{lang_instruction}\n"
        f"{instructions}\n"
        "استخدم دائماً نفس اللغة التي يكتب بها المستخدم.\n"
        "Only answer based on the available property list below and general real estate guidance.\n\n"
        "Available approved properties:\n"
        f"{summaries}\n\n"
        "Conversation history:\n"
        f"{history_text}\n\n"
        f"User query: {user_message}\n"
        "Answer concisely and naturally."
    )
    return prompt


def get_gemini_response(user_message, history, properties_data, language):
    """✅ تم تصحيح استخدام Gemini API - GenerativeModel بدل generate_text القديمة"""
    if genai is None:
        raise RuntimeError('Gemini API not available')
    prompt = build_gemini_prompt(user_message, history, properties_data, language)
    model = genai.GenerativeModel(GENAI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({'response': "عذراً، لم أستلم أي بيانات."}), 400

    user_message = data.get('message')
    chat_history = data.get('history', [])
    preferred_language = detect_language(user_message) or data.get('language') or 'en'

    if not user_message:
        return jsonify({'response': 'من فضلك اكتب رسالة أولاً.'}), 400

    try:
        db_properties = Property.query.filter_by(status='approved').all()
        properties_data = [p.to_dict() for p in db_properties] if db_properties else MOCK_PROPERTIES

        try:
            response = get_gemini_response(user_message, chat_history, properties_data, preferred_language)
        except Exception as e:
            print(f"Gemini fallback: {e}")
            from chatbot import RealEstateChatbot
            bot = RealEstateChatbot(properties_data)
            response = bot.get_response(chat_history, user_message, preferred_language)

        return jsonify({'response': response})

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'response': 'عذراً، أواجه مشكلة في الاتصال حالياً. سأكون معك فور إصلاح العطل.'})

# ─── AUTH ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_view'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('home_view'))
        flash('البريد الإلكتروني أو كلمة المرور غير صحيحة | Invalid email or password')
    return render_template('auth.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home_view'))
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not full_name or not email or not password:
            flash('جميع الحقول مطلوبة | All fields are required')
            return render_template('auth.html', signup=True)
        if User.query.filter_by(email=email).first():
            flash('هذا البريد الإلكتروني مسجل بالفعل | Email already registered')
            return render_template('auth.html', signup=True)
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل | Password must be at least 6 characters')
            return render_template('auth.html', signup=True)
        user = User(full_name=full_name, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('أهلاً بك! تم إنشاء حسابك بنجاح | Welcome! Account created successfully')
        return redirect(url_for('home_view'))
    return render_template('auth.html', signup=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_view'))

# ─── PROFILE ─────────────────────────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    saved_properties = current_user.saved_list
    user_listings = Property.query.filter_by(owner_id=current_user.id).all()
    saved_searches = SavedSearch.query.filter_by(user_id=current_user.id).all()
    alerts = SearchAlert.query.filter_by(user_id=current_user.id).all()

    for s in saved_searches:
        if not hasattr(s, "filters") or not isinstance(s.filters, dict):
            s.filters = {}
    for a in alerts:
        if not hasattr(a, "criteria_dict") or not isinstance(a.criteria_dict, dict):
            a.criteria_dict = {}

    stats = {
        "saved_count": len(saved_properties),
        "searches_count": len(saved_searches),
        "listings_count": len(user_listings),
        "alerts_count": len(alerts),
    }
    return render_template("profile.html", stats=stats, saved_searches=saved_searches, alerts=alerts)

# ─── MY LISTINGS ─────────────────────────────────────────────────────────────
@app.route('/my-listings')
@login_required
def my_listings():
    user_properties = Property.query.filter_by(owner_id=current_user.id).all()
    stats = {
        "approved_count": len([p for p in user_properties if p.status == 'approved']),
        "pending_count":  len([p for p in user_properties if p.status == 'pending']),
        "rejected_count": len([p for p in user_properties if p.status == 'rejected']),
    }
    return render_template('my_listings.html', listings=user_properties, stats=stats)

@app.route('/approved-listings')
@login_required
def approved_listings():
    listings = Property.query.filter_by(owner_id=current_user.id, status='approved').all()
    return render_template('approved_listings.html', approved_listings=listings)

# ─── PROPERTY DETAIL ─────────────────────────────────────────────────────────
@app.route('/property/<int:prop_id>')
def property_detail(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        mock_prop = next((p for p in MOCK_PROPERTIES if p['id'] == prop_id), None)
        if not mock_prop:
            abort(404)
        return render_template('property.html', property=mock_prop)
    return render_template('property.html', property=prop.to_dict())

# ─── SUBMIT PROPERTY ─────────────────────────────────────────────────────────
@app.route('/submit-property', methods=['GET', 'POST'])
@login_required
def submit_property():
    if request.method == 'POST':
        try:
            title        = request.form.get('title', '').strip()
            price        = request.form.get('price', '').strip()
            listing_type = request.form.get('listing_type', 'buy')
            city         = request.form.get('city', 'Cairo').strip()
            area         = request.form.get('area', '').strip()
            bedrooms     = request.form.get('bedrooms', 0)
            description  = request.form.get('description', '').strip()
            lat          = float(request.form.get('lat', 30.0444))
            lng          = float(request.form.get('lng', 31.2357))

            if not title or not price:
                flash('عنوان العقار والسعر مطلوبان | Title and price are required')
                return redirect(url_for('submit_property'))

            prop = Property(
                title=title, price=price, listing_type=listing_type,
                city=city, area=area, bedrooms=int(bedrooms) if bedrooms else 0,
                description=description, lat=lat, lng=lng,
                owner_id=current_user.id, status='pending',
            )
            db.session.add(prop)
            db.session.flush()

            upload_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            import time
            for img in request.files.getlist('images')[:10]:
                if img and allowed_file(img.filename):
                    fname = f"{int(time.time())}_{secure_filename(img.filename)}"
                    img.save(os.path.join(upload_folder, fname))
                    # ✅ تم تصحيح: image_url بدل filename لأن ده اسم الـ column في الـ model
                    db.session.add(PropertyImage(property_id=prop.id, image_url=fname))

            db.session.commit()
            flash('تم إرسال العقار بنجاح وهو قيد المراجعة | Property submitted and pending review')
            return redirect(url_for('my_listings'))
        except Exception as e:
            db.session.rollback()
            print(f"Submit property error: {e}")
            flash('حدث خطأ أثناء إرسال العقار | An error occurred while submitting')

    db_properties = Property.query.filter_by(status='approved').all()
    cities = list(set(p.city for p in db_properties)) if db_properties else [
        'New Cairo', 'El Shorouk', '6th of October', 'New Administrative Capital',
        'Mostakbal City', 'Ain Sokhna', 'North Coast', 'Nasr City', 'Badr',
    ]
    return render_template('submit_property.html', cities=cities)

# ─── TOGGLE SAVE ─────────────────────────────────────────────────────────────
@app.route('/toggle_save/<int:prop_id>', methods=['POST'])
@login_required
def toggle_save(prop_id):
    prop = db.session.get(Property, prop_id)
    if not prop:
        return jsonify({'status': 'error', 'message': 'Property not found'}), 404
    if prop in current_user.saved_list:
        current_user.saved_list.remove(prop)
        action = 'removed'
    else:
        current_user.saved_list.append(prop)
        action = 'added'
    db.session.commit()
    return jsonify({'status': 'success', 'action': action})

# ─── VERIFICATION ────────────────────────────────────────────────────────────
@app.route('/verify')
@login_required
def verify():
    return render_template('verify.html')

@app.route('/submit-verification', methods=['POST'])
@login_required
def submit_verification():
    try:
        id_type   = request.form.get('id_type', 'National ID')
        id_number = request.form.get('id_number', '').strip()

        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        import time
        for side in ['id_front', 'id_back']:
            f = request.files.get(side)
            if f and allowed_file(f.filename):
                fname = f"{side}_{int(time.time())}_{secure_filename(f.filename)}"
                f.save(os.path.join(upload_folder, fname))

        if hasattr(current_user, 'id_type'):
            current_user.id_type = id_type
            current_user.id_number = id_number
            current_user.verification_status = 'pending'
            db.session.commit()

        flash('تم إرسال وثائق التحقق بنجاح | Verification documents submitted')
        return redirect(url_for('profile'))
    except Exception as e:
        print(f"Verification error: {e}")
        flash('حدث خطأ أثناء رفع الوثائق | Error uploading documents')
        return redirect(url_for('verify'))

# ─── ADMIN ───────────────────────────────────────────────────────────────────
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/admin')
@admin_required
def admin_dashboard():
    all_users      = User.query.all()
    pending_props  = Property.query.filter_by(status='pending').all()
    approved_props = Property.query.filter_by(status='approved').all()
    rejected_props = Property.query.filter_by(status='rejected').all()
    pending_verifications = [u for u in all_users if getattr(u, 'verification_status', None) == 'pending']

    return render_template(
        'admin.html',
        user=current_user,
        all_users=all_users,
        pending_props=pending_props,
        approved_props=approved_props,
        rejected_props=rejected_props,
        pending_verifications=pending_verifications,
        active_tab='admin-dashboard'
    )

@app.route('/admin/approve-property/<int:prop_id>', methods=['POST'])
@admin_required
def admin_approve_property(prop_id):
    prop = db.session.get(Property, prop_id)
    if prop:
        prop.status = 'approved'
        db.session.commit()
        flash(f'تمت الموافقة على العقار | Property approved: {prop.title}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-property/<int:prop_id>', methods=['POST'])
@admin_required
def admin_reject_property(prop_id):
    prop = db.session.get(Property, prop_id)
    if prop:
        prop.status = 'rejected'
        db.session.commit()
        flash(f'تم رفض العقار | Property rejected: {prop.title}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/verify-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_verify_user(user_id):
    user = db.session.get(User, user_id)
    if user and hasattr(user, 'verification_status'):
        user.verification_status = 'verified'
        db.session.commit()
        flash(f'تم التحقق من المستخدم | User verified: {user.full_name}')
    return redirect(url_for('admin_dashboard'))

# ─── ERROR HANDLERS ──────────────────────────────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    flash('غير مصرح بالوصول | Access denied')
    return redirect(url_for('home_view'))

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return redirect(url_for('home_view'))

# ─── INIT & RUN ───────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(full_name='Admin User', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001, host='0.0.0.0')