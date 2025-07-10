#!/bin/bash
# 激活虛擬環境的腳本
# 使用方法: source activate_venv.sh

echo "正在激活虛擬環境..."
source venv_new/bin/activate

echo "虛擬環境已激活！"
echo "Python 版本: $(python --version)"
echo "虛擬環境路徑: $VIRTUAL_ENV"

# 顯示已安裝的主要套件
echo ""
echo "主要已安裝套件："
pip list | grep -E "(Flask|SQLAlchemy|WTF)"
