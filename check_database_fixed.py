# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

# 强制使用UTF-8编码
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def check_database_fixed():
    """检查数据库内容（修复编码版本）"""
    db_path = 'novels/metadata.db'
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在!")
        return False
    
    print(f"✅ 数据库文件存在: {db_path}")
    print(f"文件大小: {os.path.getsize(db_path)} 字节")
    
    # 连接数据库并检查表内容
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='novels'")
    table_exists = c.fetchone()
    
    if table_exists:
        print("✅ novels表存在")
        
        # 统计记录数
        c.execute("SELECT COUNT(*) FROM novels")
        count = c.fetchone()[0]
        print(f"📚 小说记录数: {count}")
        
        # 显示所有小说
        c.execute("SELECT id, title, author, filename, file_size FROM novels ORDER BY id")
        novels = c.fetchall()
        
        print("\n📖 小说列表:")
        print("-" * 70)
        print(f"{'ID':<3} {'书名':<15} {'作者':<10} {'文件名':<20} {'大小':<10}")
        print("-" * 70)
        
        for novel in novels:
            novel_id, title, author, filename, file_size = novel
            size_mb = f"{file_size / 1024 / 1024:.2f} MB"
            print(f'{novel_id:<3} {title:<15} {author:<10} {filename:<20} {size_mb:<10}')
        
        print("\n✅ 数据库构建成功！所有小说数据已正确导入。")
    else:
        print("❌ novels表不存在")
        return False
    
    conn.close()
    return True

if __name__ == '__main__':
    check_database_fixed()