# 項目概覽 (Project Overview)

## 📁 項目結構

```
student_management/
├── 📁 app/                          # 主應用目錄
│   ├── 📄 __init__.py              # Flask 應用初始化
│   ├── 📁 auth/                    # 認證模組
│   │   ├── __init__.py
│   │   ├── forms.py                # 登入/註冊表單
│   │   └── routes.py               # 認證路由
│   ├── 📁 classes/                 # 班級管理模組
│   │   ├── __init__.py
│   │   ├── decorators.py           # 權限裝飾器
│   │   ├── forms.py                # 班級表單
│   │   └── routes.py               # 班級路由
│   ├── 📁 models/                  # 數據模型
│   │   └── __init__.py             # SQLAlchemy 模型定義
│   ├── 📁 search/                  # 搜尋功能模組
│   │   ├── __init__.py
│   │   └── routes.py               # 搜尋 API 和路由
│   ├── 📁 static/                  # 靜態資源
│   │   └── css/
│   │       └── dashboard.css       # 自定義樣式
│   ├── 📁 student/                 # 學生管理模組
│   │   ├── __init__.py
│   │   ├── decorators.py           # 權限控制
│   │   ├── forms.py                # 學生表單
│   │   └── routes.py               # 學生路由
│   ├── 📁 teacher/                 # 教師管理模組
│   │   ├── __init__.py
│   │   ├── decorators.py           # 權限控制
│   │   ├── forms.py                # 教師表單
│   │   └── routes.py               # 教師路由
│   ├── 📁 templates/               # HTML 模板
│   │   ├── 📁 auth/                # 認證相關模板
│   │   ├── 📁 classes/             # 班級相關模板
│   │   ├── 📁 search/              # 搜尋相關模板
│   │   ├── 📁 student/             # 學生相關模板
│   │   ├── 📁 teacher/             # 教師相關模板
│   │   ├── 📁 user_management/     # 用戶管理模板
│   │   ├── base.html               # 基礎模板
│   │   └── index.html              # 首頁模板
│   └── 📁 user_management/         # 用戶管理模組
│       ├── __init__.py
│       ├── decorators.py           # 管理員權限
│       ├── forms.py                # 用戶管理表單
│       └── routes.py               # 用戶管理路由
├── 📄 config.py                    # 應用配置
├── 📄 manage.py                    # 數據庫管理腳本
├── 📄 requirements.txt             # Python 依賴
├── 📄 reset_admin.py               # 管理員重置腳本
├── 📄 run.py                       # 應用啟動文件
├── 📄 .gitignore                   # Git 忽略文件
├── 📄 README.md                    # 項目說明
├── 📄 LICENSE                      # 授權協議
├── 📄 DEPLOYMENT.md                # 部署指南
└── 📄 setup_github.sh              # GitHub 設置腳本
```

## 🎯 核心功能模組

### 1. 認證系統 (`app/auth/`)
- **用途**: 用戶登入、登出、註冊
- **主要文件**:
  - `forms.py`: 登入和註冊表單驗證
  - `routes.py`: 認證相關路由處理
- **功能**: Flask-Login 集成、密碼加密、會話管理

### 2. 學生管理 (`app/student/`)
- **用途**: 學生資料的 CRUD 操作
- **主要文件**:
  - `forms.py`: 學生資料表單和驗證
  - `routes.py`: 學生管理路由
  - `decorators.py`: 權限控制裝飾器
- **功能**: 新增、編輯、刪除、查看學生、分頁顯示

### 3. 教師管理 (`app/teacher/`)
- **用途**: 教師資料的 CRUD 操作
- **主要文件**:
  - `forms.py`: 教師資料表單和驗證
  - `routes.py`: 教師管理路由
  - `decorators.py`: 權限控制裝飾器
- **功能**: 教師資料管理、薪資管理、部門分配

### 4. 班級管理 (`app/classes/`)
- **用途**: 班級資料和學生分配管理
- **主要文件**:
  - `forms.py`: 班級表單
  - `routes.py`: 班級管理路由
  - `decorators.py`: 權限控制
- **功能**: 班級創建、學生分配、班導師指派

### 5. 搜尋系統 (`app/search/`)
- **用途**: 全局搜尋功能
- **主要文件**:
  - `routes.py`: 搜尋 API 和頁面路由
- **功能**: 跨模組搜尋、即時建議、權限過濾

### 6. 用戶管理 (`app/user_management/`)
- **用途**: 系統用戶管理 (管理員功能)
- **主要文件**:
  - `forms.py`: 用戶管理表單
  - `routes.py`: 用戶管理路由
  - `decorators.py`: 管理員權限控制
- **功能**: 用戶創建、角色分配、密碼重置

## 🗄️ 數據模型 (`app/models/__init__.py`)

### 主要實體
1. **User**: 系統用戶 (管理員、教師、學生、職員)
2. **Student**: 學生資料
3. **Teacher**: 教師資料
4. **Class**: 班級資料
5. **Department**: 部門資料

### 關聯關係
- User ↔ Student/Teacher (一對一)
- Teacher ↔ Class (一對多，班導師)
- Student ↔ Class (多對一，班級歸屬)
- Teacher ↔ Department (多對一，部門歸屬)
- Class ↔ Department (多對一，班級所屬部門)

## 🎨 前端架構

### 模板系統
- **基礎模板**: `base.html` - 包含導航欄、搜尋欄、頁腳
- **模組模板**: 各模組專用模板，繼承基礎模板
- **響應式設計**: Bootstrap 5 框架

### 靜態資源
- **CSS**: Bootstrap 5 + 自定義樣式
- **JavaScript**: 原生 JS + AJAX
- **圖標**: Font Awesome 6

### 用戶界面特色
- 響應式設計，支援各種設備
- 即時搜尋和自動完成
- 分頁和篩選功能
- 友善的錯誤提示
- 多語言支援 (繁體中文)

## 🔐 權限系統

### 角色定義
1. **admin**: 系統管理員 - 完整權限
2. **teacher**: 教師 - 管理自己的班級和學生
3. **student**: 學生 - 查看自己的資料
4. **staff**: 職員 - 協助管理功能

### 權限控制
- 裝飾器模式實現權限檢查
- 基於角色的訪問控制 (RBAC)
- 數據級權限過濾
- 路由級權限保護

## 🔧 配置和部署

### 配置文件
- `config.py`: 主要配置 (資料庫、密鑰等)
- `requirements.txt`: Python 依賴套件
- `.gitignore`: Git 版本控制忽略規則

### 部署腳本
- `run.py`: 開發環境啟動
- `manage.py`: 資料庫初始化和管理
- `reset_admin.py`: 管理員帳戶重置
- `setup_github.sh`: GitHub 倉庫設置

## 📊 開發統計

- **總文件數**: 64 個文件
- **代碼行數**: 8,657+ 行
- **模組數**: 6 個主要功能模組
- **模板數**: 25+ 個 HTML 模板
- **路由數**: 50+ 個路由端點
- **數據模型**: 5 個主要實體模型

## 🚀 快速開始

1. **克隆項目**: `git clone <repository-url>`
2. **安裝依賴**: `pip install -r requirements.txt`
3. **配置資料庫**: 修改 `config.py`
4. **初始化**: `python manage.py`
5. **創建管理員**: `python reset_admin.py`
6. **啟動應用**: `python run.py`

## 🤝 貢獻指南

- 遵循 PEP 8 代碼風格
- 為新功能添加測試
- 更新相關文檔
- 提交前運行測試
- 使用有意義的提交訊息

## 📞 技術支援

如有技術問題，請查看：
1. `README.md` - 基本使用說明
2. `DEPLOYMENT.md` - 部署指南
3. GitHub Issues - 問題追蹤
4. 代碼註釋 - 詳細實現說明
