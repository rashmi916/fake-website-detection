from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from models import CheckResult
from app import db
from utils.features import extract_features
from utils.model_service import load_model, predict

checker_bp = Blueprint('checker', __name__, template_folder='../templates')

@checker_bp.route('/', methods=['GET'])
def home():
    return redirect(url_for('checker.check_form'))

@checker_bp.route('/check', methods=['GET','POST'])
def check_form():
    if request.method == 'POST':
        url = request.form.get('url')
        return redirect(url_for('checker.result', url=url))
    return render_template('check.html')

@checker_bp.route('/result')
def result():
    url = request.args.get('url')
    features = extract_features(url)
    model = load_model()
    score, verdict = predict(model, features)  # predict returns probability & verdict
    # Save result
    rec = CheckResult(user_id=current_user.id if current_user.is_authenticated else None,
                      url=url, verdict=verdict, score=float(score), features=str(features))
    db.session.add(rec)
    db.session.commit()
    return render_template('result.html', url=url, score=score, verdict=verdict, features=features)

# API endpoint for async calls
@checker_bp.route('/api/check', methods=['POST'])
def api_check():
    data = request.get_json() or {}
    url = data.get('url')
    features = extract_features(url)
    model = load_model()
    score, verdict = predict(model, features)
    return jsonify({'url': url, 'score': score, 'verdict': verdict})
