import sqlite3
import os
import glob

def init_database():
    """初始化数据库和表结构"""
    conn = sqlite3.connect('novels/metadata.db')
    c = conn.cursor()
    
    # 创建小说表
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
    print("数据库表创建完成")

def get_file_size(filepath):
    """获取文件大小（字节）"""
    return os.path.getsize(filepath)

def import_novels():
    """导入小说数据"""
    # 小说信息映射表
    novel_info = {
        '红楼梦.txt': {
            'title': '红楼梦',
            'author': '曹雪芹',
            'description': '中国古典四大名著之一，清代长篇小说，又名《石头记》',
            'tags': '古典文学,爱情,家族,清代小说'
        },
        '三国演义.txt': {
            'title': '三国演义',
            'author': '罗贯中',
            'description': '中国古典四大名著之一，描写东汉末年至西晋初年的历史风云',
            'tags': '古典文学,历史,战争,权谋'
        },
        '水浒传.txt': {
            'title': '水浒传',
            'author': '施耐庵',
            'description': '中国古典四大名著之一，描写北宋末年梁山好汉起义的故事',
            'tags': '古典文学,英雄,起义,江湖'
        },
        '西游记.txt': {
            'title': '西游记',
            'author': '吴承恩',
            'description': '中国古典四大名著之一，描写唐僧师徒西天取经的神话故事',
            'tags': '古典文学,神话,冒险,佛教'
        },
        '四大名著简介.txt': {
            'title': '四大名著简介',
            'author': '整理',
            'description': '中国古典四大名著的综合介绍和赏析',
            'tags': '简介,赏析,文学评论'
        }
    }
    
    conn = sqlite3.connect('novels/metadata.db')
    c = conn.cursor()
    
    imported_count = 0
    skipped_count = 0
    
    # 遍历novels目录下的所有txt文件
    for filename in os.listdir('novels'):
        if filename.endswith('.txt'):
            filepath = os.path.join('novels', filename)
            
            # 检查是否已存在
            c.execute('SELECT id FROM novels WHERE filename = ?', (filename,))
            if c.fetchone():
                print(f'跳过已存在的文件: {filename}')
                skipped_count += 1
                continue
            
            # 获取文件信息
            if filename in novel_info:
                info = novel_info[filename]
                title = info['title']
                author = info['author']
                description = info['description']
                tags = info['tags']
            else:
                # 对于不在映射表中的文件，使用文件名作为标题
                title = os.path.splitext(filename)[0]
                author = '未知作者'
                description = ''
                tags = ''
            
            file_size = get_file_size(filepath)
            
            # 插入数据库
            c.execute('''INSERT INTO novels 
                        (title, author, filename, description, tags, file_size)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (title, author, filename, description, tags, file_size))
            
            print(f'导入成功: {title} - {author} ({file_size} 字节)')
            imported_count += 1
    
    conn.commit()
    conn.close()
    
    print(f'\n导入完成! 成功导入: {imported_count} 本, 跳过: {skipped_count} 本')

def display_novels():
    """显示数据库中的小说列表"""
    conn = sqlite3.connect('novels/metadata.db')
    c = conn.cursor()
    
    c.execute('SELECT id, title, author, filename, file_size FROM novels ORDER BY id')
    novels = c.fetchall()
    
    print('\n当前数据库中的小说:')
    print('-' * 80)
    print(f'{"ID":<3} {"书名":<15} {"作者":<10} {"文件名":<20} {"大小":<10}')
    print('-' * 80)
    
    for novel in novels:
        novel_id, title, author, filename, file_size = novel
        size_mb = f"{file_size / 1024 / 1024:.2f} MB"
        print(f'{novel_id:<3} {title:<15} {author:<10} {filename:<20} {size_mb:<10}')
    
    conn.close()

if __name__ == '__main__':
    print("开始构建小说数据库...")
    
    # 确保novels目录存在
    if not os.path.exists('novels'):
        print("错误: novels目录不存在!")
        exit(1)
    
    # 初始化数据库
    init_database()
    
    # 导入小说
    import_novels()
    
    # 显示结果
    display_novels()
    
    print("\n数据库构建完成! 现在你可以运行主程序了。")