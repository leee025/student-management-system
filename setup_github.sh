#!/bin/bash

# 學生管理系統 GitHub 設置腳本
# 此腳本幫助您將項目推送到 GitHub

echo "🚀 學生管理系統 GitHub 設置"
echo "================================"

# 檢查是否已經設置了遠程倉庫
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ 遠程倉庫已設置："
    git remote get-url origin
else
    echo "📝 請按照以下步驟設置 GitHub 倉庫："
    echo ""
    echo "1. 前往 https://github.com 並登入您的帳戶"
    echo "2. 點擊右上角的 '+' 按鈕，選擇 'New repository'"
    echo "3. 填寫倉庫資訊："
    echo "   - Repository name: student-management-system"
    echo "   - Description: 基於 Flask 的現代化學生管理系統"
    echo "   - 選擇 Public 或 Private"
    echo "   - 不要勾選 'Initialize this repository with a README'"
    echo "4. 點擊 'Create repository'"
    echo ""
    echo "5. 複製倉庫的 HTTPS 或 SSH URL"
    echo ""
    read -p "請輸入您的 GitHub 倉庫 URL: " repo_url
    
    if [ -n "$repo_url" ]; then
        echo "🔗 添加遠程倉庫..."
        git remote add origin "$repo_url"
        echo "✅ 遠程倉庫已添加: $repo_url"
    else
        echo "❌ 未提供倉庫 URL，請手動設置"
        exit 1
    fi
fi

echo ""
echo "📊 當前 Git 狀態："
git status --short

echo ""
echo "📝 最近的提交："
git log --oneline -5

echo ""
echo "🚀 準備推送到 GitHub..."
read -p "是否要推送到 GitHub? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "📤 推送到 GitHub..."
    
    # 推送主分支
    if git push -u origin main; then
        echo ""
        echo "🎉 成功推送到 GitHub！"
        echo ""
        echo "📋 項目資訊："
        echo "   - 倉庫 URL: $(git remote get-url origin)"
        echo "   - 分支: main"
        echo "   - 提交數: $(git rev-list --count HEAD)"
        echo "   - 文件數: $(git ls-files | wc -l)"
        echo ""
        echo "🌐 您可以在以下位置查看您的項目："
        repo_url=$(git remote get-url origin)
        if [[ $repo_url == *"github.com"* ]]; then
            # 轉換 SSH URL 為 HTTPS URL
            if [[ $repo_url == git@github.com:* ]]; then
                web_url="https://github.com/${repo_url#git@github.com:}"
                web_url="${web_url%.git}"
            else
                web_url="${repo_url%.git}"
            fi
            echo "   $web_url"
        fi
        echo ""
        echo "📚 接下來您可以："
        echo "   1. 在 GitHub 上編輯 README.md 添加更多詳細資訊"
        echo "   2. 設置 GitHub Pages (如果需要)"
        echo "   3. 配置 Issues 和 Projects"
        echo "   4. 邀請協作者"
        echo "   5. 設置 CI/CD 流程"
        
    else
        echo "❌ 推送失敗，請檢查："
        echo "   1. 網路連接"
        echo "   2. GitHub 認證 (用戶名/密碼 或 SSH 金鑰)"
        echo "   3. 倉庫權限"
        echo ""
        echo "💡 如果使用 HTTPS，您可能需要使用 Personal Access Token"
        echo "   前往: https://github.com/settings/tokens"
    fi
else
    echo "⏸️  推送已取消"
    echo ""
    echo "💡 您可以稍後手動推送："
    echo "   git push -u origin main"
fi

echo ""
echo "📋 有用的 Git 命令："
echo "   git status          - 查看狀態"
echo "   git add .           - 添加所有更改"
echo "   git commit -m \"...\" - 提交更改"
echo "   git push            - 推送到遠程倉庫"
echo "   git pull            - 從遠程倉庫拉取"
echo "   git log --oneline   - 查看提交歷史"
