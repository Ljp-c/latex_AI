#!/bin/bash

# 增强版编译脚本
# 支持：自动检测编译器、错误重试、PDF预览

set -e  # 遇到错误立即退出

TEX_FILE=${1:-main.tex}
BASE_NAME="${TEX_FILE%.*}"

# 检测编译器
detect_compiler() {
    if grep -q "documentclass.*{ctex" "$TEX_FILE" || \
       grep -q "usepackage.*{xeCJK" "$TEX_FILE" || \
       grep -q "usepackage.*{fontspec" "$TEX_FILE"; then
        COMPILER="xelatex"
    elif grep -q "usepackage.*{luatex" "$TEX_FILE"; then
        COMPILER="lualatex"
    else
        COMPILER="pdflatex"
    fi
    echo "检测到使用 $COMPILER 编译器"
}

# 编译函数
compile_tex() {
    local attempt=1
    local max_attempts=3
    
    while [ $attempt -le $max_attempts ]; do
        echo "编译尝试 $attempt/$max_attempts ..."
        $COMPILER -synctex=1 -interaction=nonstopmode -file-line-error "$TEX_FILE"
        
        if [ $? -eq 0 ]; then
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    return 1
}

# 主流程
main() {
    echo "📄 编译文档: $TEX_FILE"
    
    detect_compiler
    
    # 第一次编译
    echo "🔄 第一次编译..."
    if ! compile_tex; then
        echo "❌ 编译失败，请检查错误信息"
        exit 1
    fi
    
    # 处理参考文献
    if [ -f "$BASE_NAME.bcf" ] || [ -f "$BASE_NAME.aux" ]; then
        if command -v biber &> /dev/null; then
            echo "📚 处理参考文献 (Biber)..."
            biber "$BASE_NAME" || true
        elif command -v bibtex &> /dev/null; then
            echo "📚 处理参考文献 (BibTeX)..."
            bibtex "$BASE_NAME" || true
        fi
        
        # 后续编译
        echo "🔄 第二次编译..."
        compile_tex
        
        echo "🔄 第三次编译..."
        compile_tex
    fi
    
    # 清理文件
    echo "🧹 清理中间文件..."
    cleanup
    
    echo "✅ 编译成功: $BASE_NAME.pdf"
    
    # 自动打开PDF
    if [ "$2" == "--view" ] || [ "$2" == "-v" ]; then
        open_pdf
    fi
}

# 清理函数
cleanup() {
    rm -f "$BASE_NAME".{aux,log,bbl,bcf,blg,run.xml,toc,out,lof,lot,nav,snm,vrb} 2>/dev/null || true
    rm -f _minted-* 2>/dev/null || true
}

# 打开PDF
open_pdf() {
    if [ -f "$BASE_NAME.pdf" ]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "$BASE_NAME.pdf" &
        elif command -v open &> /dev/null; then
            open "$BASE_NAME.pdf" &
        else
            echo "⚠️  无法自动打开PDF，请手动查看"
        fi
    fi
}

# 运行主函数
main "$@"