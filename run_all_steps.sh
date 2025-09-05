#!/bin/bash
echo "🔧 Anki 插件修复 - 快速执行"
echo "================================"

echo
echo "📋 第一步：修复导入路径"
python3 fix_anki_imports.py
if [ $? -ne 0 ]; then
    echo "❌ 第一步失败"
    exit 1
fi

echo
echo "📋 第二步：验证修复"
python3 test_import_fix.py
if [ $? -ne 0 ]; then
    echo "❌ 第二步失败"
    exit 1
fi

echo
echo "📋 第三步：重新打包"
python3 build_addon.py
if [ $? -ne 0 ]; then
    echo "❌ 第三步失败"
    exit 1
fi

echo
echo "📋 第四步：检查结果"
python3 check_execution.py

echo
echo "🎉 修复完成！请在 Anki 中安装新的插件包"
