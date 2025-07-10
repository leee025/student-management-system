"""
全局搜尋路由
處理跨模組的搜尋請求
"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.search import bp
from app.models import Student, Teacher, Class, Department
from app.student.decorators import can_view_student_list
from app.teacher.decorators import can_view_teacher_list


@bp.route('/')
@login_required
def global_search():
    """全局搜尋頁面"""
    # 從URL參數獲取初始搜尋查詢
    initial_query = request.args.get('q', '')
    return render_template('search/global_search.html',
                         title='全局搜尋',
                         initial_query=initial_query)


@bp.route('/api')
@login_required
def search_api():
    """全局搜尋 API"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, student, teacher, class
    
    if not query:
        return jsonify({
            'students': [],
            'teachers': [],
            'classes': [],
            'total': 0
        })
    
    results = {
        'students': [],
        'teachers': [],
        'classes': [],
        'total': 0
    }
    
    # 搜尋學生
    if search_type in ['all', 'student'] and can_view_student_list():
        try:
            student_query = Student.query.options(joinedload(Student.class_info))
            
            # 根據用戶權限過濾
            if current_user.role == 'teacher':
                # 教師只能看到自己班級的學生
                student_query = student_query.join(Class).filter(
                    Class.teacher_id == current_user.related_id
                )
            
            students = student_query.filter(
                Student.name.contains(query) |
                Student.student_id.contains(query) |
                Student.email.contains(query) |
                Student.phone.contains(query)
            ).limit(10).all()
            
            results['students'] = [
                {
                    'student_id': s.student_id,
                    'name': s.name,
                    'class_name': s.class_info.class_name if s.class_info else '未分配',
                    'status': s.status,
                    'email': s.email,
                    'phone': s.phone
                }
                for s in students
            ]
        except Exception as e:
            print(f"搜尋學生時發生錯誤: {e}")
    
    # 搜尋教師
    if search_type in ['all', 'teacher'] and can_view_teacher_list():
        try:
            teacher_query = Teacher.query.options(joinedload(Teacher.department))
            
            # 根據用戶權限過濾
            if current_user.role == 'teacher':
                # 教師只能看到自己
                teacher_query = teacher_query.filter(
                    Teacher.teacher_id == current_user.related_id
                )
            
            teachers = teacher_query.filter(
                Teacher.name.contains(query) |
                Teacher.teacher_id.contains(query) |
                Teacher.email.contains(query) |
                Teacher.phone.contains(query) |
                Teacher.position.contains(query)
            ).limit(10).all()
            
            results['teachers'] = [
                {
                    'teacher_id': t.teacher_id,
                    'name': t.name,
                    'department_name': t.department.department_name if t.department else '未分配',
                    'position': t.position,
                    'email': t.email,
                    'phone': t.phone
                }
                for t in teachers
            ]
        except Exception as e:
            print(f"搜尋教師時發生錯誤: {e}")
    
    # 搜尋班級
    if search_type in ['all', 'class']:
        try:
            class_query = Class.query.options(
                joinedload(Class.department),
                joinedload(Class.teacher)
            )
            
            # 根據用戶權限過濾
            if current_user.role == 'teacher':
                # 教師只能看到自己負責的班級
                class_query = class_query.filter(
                    Class.teacher_id == current_user.related_id
                )
            
            classes = class_query.filter(
                Class.class_name.contains(query)
            ).limit(10).all()
            
            results['classes'] = [
                {
                    'class_id': c.class_id,
                    'class_name': c.class_name,
                    'grade': c.grade,
                    'department_name': c.department.department_name if c.department else '未分配',
                    'teacher_name': c.teacher.name if c.teacher else '未分配',
                    'student_count': len(c.students) if c.students else 0
                }
                for c in classes
            ]
        except Exception as e:
            print(f"搜尋班級時發生錯誤: {e}")
    
    # 計算總結果數
    results['total'] = len(results['students']) + len(results['teachers']) + len(results['classes'])
    
    return jsonify(results)


@bp.route('/suggestions')
@login_required
def search_suggestions():
    """搜尋建議 API - 用於自動完成"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    # 學生建議
    if can_view_student_list():
        try:
            student_query = Student.query
            if current_user.role == 'teacher':
                student_query = student_query.join(Class).filter(
                    Class.teacher_id == current_user.related_id
                )
            
            students = student_query.filter(
                Student.name.contains(query) |
                Student.student_id.contains(query)
            ).limit(5).all()
            
            for s in students:
                suggestions.append({
                    'type': 'student',
                    'id': s.student_id,
                    'text': f"{s.name} ({s.student_id})",
                    'category': '學生'
                })
        except Exception:
            pass
    
    # 教師建議
    if can_view_teacher_list():
        try:
            teacher_query = Teacher.query
            if current_user.role == 'teacher':
                teacher_query = teacher_query.filter(
                    Teacher.teacher_id == current_user.related_id
                )
            
            teachers = teacher_query.filter(
                Teacher.name.contains(query) |
                Teacher.teacher_id.contains(query)
            ).limit(5).all()
            
            for t in teachers:
                suggestions.append({
                    'type': 'teacher',
                    'id': t.teacher_id,
                    'text': f"{t.name} ({t.teacher_id})",
                    'category': '教師'
                })
        except Exception:
            pass
    
    return jsonify(suggestions[:10])  # 最多返回10個建議
