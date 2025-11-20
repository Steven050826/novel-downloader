from flask import Flask, request, jsonify, send_file
from flask_restful import Api, Resource
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)  # 允许跨域访问
api = Api(app)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('novels/metadata.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS novels
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT,
                  filename TEXT NOT NULL,
                  description TEXT,
                  tags TEXT,
                  file_size INTEGER,
                  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# 搜索小说
def search_novels(keyword, page=1, per_page=20):
    conn = sqlite3.connect('novels/metadata.db')
    c = conn.cursor()
    
    offset = (page - 1) * per_page
    
    if keyword:
        c.execute('''SELECT * FROM novels 
                    WHERE title LIKE ? OR author LIKE ? OR tags LIKE ?
                    LIMIT ? OFFSET ?''',
                 (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', per_page, offset))
    else:
        c.execute('''SELECT * FROM novels 
                    ORDER BY id DESC 
                    LIMIT ? OFFSET ?''', 
                 (per_page, offset))
    
    results = c.fetchall()
    
    # 获取总数
    if keyword:
        c.execute('''SELECT COUNT(*) FROM novels 
                    WHERE title LIKE ? OR author LIKE ? OR tags LIKE ?''',
                 (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    else:
        c.execute('''SELECT COUNT(*) FROM novels''')
    
    total = c.fetchone()[0]
    conn.close()
    
    # 格式化结果
    novels_list = []
    for row in results:
        novel = {
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'filename': row[3],
            'description': row[4],
            'tags': row[5],
            'file_size': row[6],
            'created_date': row[7]
        }
        novels_list.append(novel)
    
    return {
        'data': novels_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }

# API资源类
class NovelList(Resource):
    def get(self):
        """获取小说列表"""
        keyword = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)  # 限制每页最大50条
        
        result = search_novels(keyword, page, per_page)
        return jsonify({
            'success': True,
            'data': result['data'],
            'pagination': result['pagination']
        })

class NovelDetail(Resource):
    def get(self, novel_id):
        """获取小说详情"""
        conn = sqlite3.connect('novels/metadata.db')
        c = conn.cursor()
        c.execute('SELECT * FROM novels WHERE id = ?', (novel_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {'success': False, 'error': '小说不存在'}, 404
        
        novel = {
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'filename': row[3],
            'description': row[4],
            'tags': row[5],
            'file_size': row[6],
            'created_date': row[7]
        }
        
        return jsonify({
            'success': True,
            'data': novel
        })

class NovelDownload(Resource):
    def get(self, novel_id):
        """下载小说文件"""
        conn = sqlite3.connect('novels/metadata.db')
        c = conn.cursor()
        c.execute('SELECT filename, title FROM novels WHERE id = ?', (novel_id,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            return {'success': False, 'error': '文件不存在'}, 404
        
        filename, title = result
        filepath = f'novels/{filename}'
        
        if not os.path.exists(filepath):
            return {'success': False, 'error': '文件不存在'}, 404
        
        # 返回文件下载
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"{title}.txt",
            mimetype='text/plain'
        )

class NovelStats(Resource):
    def get(self):
        """获取统计信息"""
        conn = sqlite3.connect('novels/metadata.db')
        c = conn.cursor()
        
        # 小说总数
        c.execute('SELECT COUNT(*) FROM novels')
        total_novels = c.fetchone()[0]
        
        # 作者数量
        c.execute('SELECT COUNT(DISTINCT author) FROM novels')
        total_authors = c.fetchone()[0]
        
        # 文件总大小
        c.execute('SELECT SUM(file_size) FROM novels')
        total_size = c.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_novels': total_novels,
                'total_authors': total_authors,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        })

# 注册API路由
api.add_resource(NovelList, '/api/novels')
api.add_resource(NovelDetail, '/api/novels/<int:novel_id>')
api.add_resource(NovelDownload, '/api/novels/<int:novel_id>/download')
api.add_resource(NovelStats, '/api/stats')

@app.route('/')
def index():
    """API首页信息"""
    return jsonify({
        'success': True,
        'message': '小说API服务运行中',
        'endpoints': {
            '获取小说列表': '/api/novels?q=关键词&page=1&per_page=20',
            '获取小说详情': '/api/novels/<id>',
            '下载小说文件': '/api/novels/<id>/download',
            '获取统计信息': '/api/stats'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 初始化数据库
    if not os.path.exists('novels'):
        os.makedirs('novels')
    init_db()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)