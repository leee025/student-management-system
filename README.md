# 學生管理系統 (Student Management System)

一個基於 Flask 的現代化學生管理系統，提供完整的學生、教師、班級管理功能，以及強大的搜尋和權限控制系統。

## 🌟 主要功能

### 👥 用戶管理
- **多角色權限系統**: 管理員、教師、學生、職員
- **安全登入**: Flask-Login 身份驗證
- **權限控制**: 基於角色的訪問控制 (RBAC)

### 🎓 學生管理
- **學生資料管理**: 新增、編輯、刪除、查看學生資訊
- **班級分配**: 學生與班級的關聯管理
- **狀態追蹤**: 在學、休學、畢業狀態管理
- **分頁顯示**: 高效的數據分頁展示

### 👨‍🏫 教師管理
- **教師資料管理**: 完整的教師資訊管理
- **部門分配**: 教師與部門的關聯
- **薪資管理**: 教師薪資資訊管理
- **職位管理**: 教授、副教授、講師等職位分類

### 🏫 班級管理
- **班級資料管理**: 班級基本資訊管理
- **班導師分配**: 教師與班級的關聯
- **學生名單**: 班級學生列表管理

### 🔍 強大搜尋功能
- **全局搜尋**: 跨模組統一搜尋界面
- **即時搜尋**: 輸入時自動搜尋建議
- **多字段搜尋**: 支援姓名、編號、郵箱等多字段
- **權限過濾**: 根據用戶角色過濾搜尋結果
- **分類顯示**: 學生、教師、班級分類展示

## 🛠️ 技術架構

### 後端技術
- **Flask**: Python Web 框架
- **SQLAlchemy**: ORM 數據庫操作
- **Flask-Login**: 用戶認證管理
- **Flask-WTF**: 表單處理和驗證
- **MySQL**: 關聯式資料庫

### 前端技術
- **Bootstrap 5**: 響應式 UI 框架
- **Font Awesome**: 圖標庫
- **JavaScript**: 前端互動邏輯
- **AJAX**: 異步數據請求
- **Jinja2**: 模板引擎

### 項目結構
```
student_management/
├── app/                    # 應用主目錄
│   ├── __init__.py        # 應用初始化
│   ├── models/            # 數據模型
│   ├── auth/              # 認證模組
│   ├── student/           # 學生管理模組
│   ├── teacher/           # 教師管理模組
│   ├── classes/           # 班級管理模組
│   ├── search/            # 搜尋功能模組
│   ├── user_management/   # 用戶管理模組
│   ├── templates/         # HTML 模板
│   └── static/            # 靜態資源
├── config.py              # 配置文件
├── requirements.txt       # 依賴套件
├── run.py                # 應用啟動文件
└── README.md             # 項目說明
```

## 🚀 快速開始

### 環境要求
- Python 3.8+
- MySQL 5.7+
- pip

### 安裝步驟

1. **克隆項目**
```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

2. **創建虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **配置資料庫**
```bash
# 修改 config.py 中的資料庫連接設定
# 創建資料庫
mysql -u root -p
CREATE DATABASE student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **初始化資料庫**
```bash
python manage.py
```

6. **創建管理員帳戶**
```bash
python reset_admin.py
```

7. **啟動應用**
```bash
python run.py
```

8. **訪問系統**
打開瀏覽器訪問 `http://localhost:5000`

## 📱 功能截圖

### 登入頁面
- 安全的用戶認證
- 角色選擇登入

### 儀表板
- 系統統計數據
- 快速操作入口

### 學生管理
- 學生列表展示
- 詳細資料查看
- 搜尋和篩選

### 教師管理
- 教師資訊管理
- 部門分配
- 薪資管理

### 全局搜尋
- 統一搜尋界面
- 即時搜尋建議
- 分類結果顯示

## 🔐 權限說明

### 管理員 (Admin)
- 完整系統管理權限
- 用戶、學生、教師、班級管理
- 系統配置和維護

### 教師 (Teacher)
- 查看和管理自己負責的班級
- 查看班級學生資訊
- 更新自己的個人資料

### 學生 (Student)
- 查看自己的個人資料
- 查看所屬班級資訊
- 更新個人聯繫資訊

### 職員 (Staff)
- 查看學生和教師資訊
- 協助日常管理工作

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權協議

本項目採用 MIT 授權協議 - 查看 [LICENSE](LICENSE) 文件了解詳情

## 📞 聯繫方式

如有問題或建議，請通過以下方式聯繫：

- 提交 [Issue](https://github.com/your-username/student-management-system/issues)
- 發送郵件至：your-email@example.com

## 🙏 致謝

感謝所有為這個項目做出貢獻的開發者和用戶！

---

⭐ 如果這個項目對您有幫助，請給我們一個 Star！
