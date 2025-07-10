"""
全局搜尋模組
提供跨模組的統一搜尋功能
"""

from flask import Blueprint

bp = Blueprint('search', __name__, url_prefix='/search')

from app.search import routes
