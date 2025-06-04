from flask import Blueprint, send_from_directory, current_app, url_for, redirect
from flask_login import login_required
from app.decorators import permission_required

main_bp = Blueprint('main_bp', __name__)

# Shared route to download uploaded files
@main_bp.route('/uploads/<filename>')
@login_required
@permission_required("view_dashboard")
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route("/", endpoint="index")
def index():
    return redirect(url_for("auth.login"))