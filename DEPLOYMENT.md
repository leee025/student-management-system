# 部署指南 (Deployment Guide)

本文檔提供學生管理系統的詳細部署說明，包括開發環境和生產環境的配置。

## 📋 系統要求

### 最低要求
- **操作系統**: Linux (Ubuntu 18.04+), macOS, Windows 10+
- **Python**: 3.8 或更高版本
- **資料庫**: MySQL 5.7+ 或 MariaDB 10.3+
- **記憶體**: 最少 1GB RAM
- **硬碟空間**: 最少 2GB 可用空間

### 推薦配置
- **CPU**: 2 核心或更多
- **記憶體**: 4GB RAM 或更多
- **資料庫**: MySQL 8.0+
- **Web 伺服器**: Nginx + Gunicorn (生產環境)

## 🛠️ 開發環境部署

### 1. 環境準備

```bash
# 更新系統套件
sudo apt update && sudo apt upgrade -y

# 安裝 Python 和相關工具
sudo apt install python3 python3-pip python3-venv git -y

# 安裝 MySQL
sudo apt install mysql-server mysql-client -y
```

### 2. 資料庫設定

```bash
# 啟動 MySQL 服務
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全設定
sudo mysql_secure_installation

# 登入 MySQL
mysql -u root -p

# 創建資料庫和用戶
CREATE DATABASE student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON student_management.* TO 'sms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 應用部署

```bash
# 克隆項目
git clone https://github.com/your-username/student-management-system.git
cd student-management-system

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 配置環境變數
cp config.py config_local.py
# 編輯 config_local.py 設定資料庫連接

# 初始化資料庫
python manage.py

# 創建管理員帳戶
python reset_admin.py

# 啟動開發伺服器
python run.py
```

## 🚀 生產環境部署

### 1. 使用 Gunicorn + Nginx

#### 安裝 Gunicorn
```bash
pip install gunicorn
```

#### 創建 Gunicorn 配置文件
```bash
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 創建 systemd 服務文件
```bash
# /etc/systemd/system/student-management.service
[Unit]
Description=Student Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/student-management-system
Environment="PATH=/path/to/student-management-system/venv/bin"
ExecStart=/path/to/student-management-system/venv/bin/gunicorn --config gunicorn.conf.py run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 配置 Nginx
```nginx
# /etc/nginx/sites-available/student-management
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/student-management-system/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 啟動服務
```bash
# 啟用服務
sudo systemctl enable student-management
sudo systemctl start student-management

# 啟用 Nginx 配置
sudo ln -s /etc/nginx/sites-available/student-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. 使用 Docker 部署

#### 創建 Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

#### 創建 docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql://sms_user:password@db:3306/student_management
    depends_on:
      - db
    volumes:
      - ./app/static:/app/app/static

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: student_management
      MYSQL_USER: sms_user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

#### 部署命令
```bash
# 構建和啟動
docker-compose up -d

# 初始化資料庫
docker-compose exec web python manage.py

# 創建管理員
docker-compose exec web python reset_admin.py
```

## 🔧 配置說明

### 環境變數
```bash
# .env 文件
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://username:password@localhost/database_name
FLASK_ENV=production
FLASK_DEBUG=False
```

### 安全設定
- 使用強密碼
- 定期更新依賴套件
- 配置防火牆
- 啟用 HTTPS
- 定期備份資料庫

## 📊 監控和維護

### 日誌管理
```bash
# 查看應用日誌
sudo journalctl -u student-management -f

# 查看 Nginx 日誌
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 資料庫備份
```bash
# 創建備份腳本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u sms_user -p student_management > backup_$DATE.sql
```

### 性能優化
- 配置資料庫索引
- 啟用 Gzip 壓縮
- 使用 CDN 加速靜態資源
- 配置快取機制

## 🚨 故障排除

### 常見問題

1. **資料庫連接失敗**
   - 檢查資料庫服務狀態
   - 驗證連接參數
   - 確認用戶權限

2. **靜態文件無法載入**
   - 檢查 Nginx 配置
   - 驗證文件路徑
   - 確認文件權限

3. **應用無法啟動**
   - 檢查依賴套件
   - 查看錯誤日誌
   - 驗證配置文件

### 聯繫支援
如遇到部署問題，請提交 Issue 或聯繫技術支援團隊。
