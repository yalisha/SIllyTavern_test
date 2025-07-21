#!/usr/bin/env python3
"""
PDF转图片脚本
使用方法: python pdf_to_images.py <pdf文件路径> [输出目录]
"""

import sys
import os
from pathlib import Path 

try:
    import fitz  # PyMuPDF
except ImportError:
    print("请先安装PyMuPDF: pip install PyMuPDF")
    sys.exit(1)

def pdf_to_images(pdf_path, output_dir=None):
    """将PDF转换为图片"""
    
    # 检查PDF文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: PDF文件不存在: {pdf_path}")
        return False
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.splitext(pdf_path)[0] + "_images"
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)
        
        print(f"开始转换PDF: {pdf_path}")
        print(f"总页数: {len(pdf_document)}")
        print(f"输出目录: {output_dir}")
        
        # 遍历每一页
        for page_num in range(len(pdf_document)):
            # 获取页面
            page = pdf_document.load_page(page_num)
            
            # 设置缩放矩阵 (2.0表示2倍缩放，提高图片质量)
            mat = fitz.Matrix(2.0, 2.0)
            
            # 渲染页面为图片
            pix = page.get_pixmap(matrix=mat)
            
            # 保存图片
            output_filename = f"page_{page_num + 1:03d}.png"
            output_path = os.path.join(output_dir, output_filename)
            pix.save(output_path)
            
            print(f"已转换第 {page_num + 1} 页: {output_filename}")
        
        # 关闭PDF文档
        pdf_document.close()
        
        print(f"\n转换完成! 图片保存在: {output_dir}")
        return True
        
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python pdf_to_images.py <pdf文件路径> [输出目录]")
        print("示例: python pdf_to_images.py document.pdf")
        print("示例: python pdf_to_images.py document.pdf ./output_images/")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = pdf_to_images(pdf_path, output_dir)
    
    if success:
        print("\n✅ PDF转换完成!")
    else:
        print("\n❌ PDF转换失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()