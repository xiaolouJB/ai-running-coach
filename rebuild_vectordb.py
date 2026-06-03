import os
import sys

def check_dependencies():
    try:
        import chromadb
        from langchain.text_splitter import MarkdownTextSplitter
        # 假设这里有更多导入
    except ImportError:
        print("❌ 缺少依赖包。运行前请先安装：")
        print("pip install chromadb langchain")
        sys.exit(1)

def print_instructions():
    print("""
======================================================================
🏃 AI Running Coach v2.0 - 高级本地知识库重建脚本
======================================================================

【声明】
受限于版权要求，公开的 GitHub 仓库不包含原版跑步书籍的内容以及 ChromaDB 向量库。
该脚本仅供『自备合法版权书籍』的本地高级用户使用。

【使用说明】
1. 准备您的合法 EPUB 或 PDF 书籍文件。
2. 将书籍放入对应的目录中：
   - 理论/跑步理论库/
   - 理论/伤病康复库/
   - 理论/力量体能库/
   - 理论/运动营养库/
3. 取消注释本脚本下方的执行逻辑。
4. 运行此脚本，它会自动切割文本并构建本地的 ChromaDB 向量库。

注意：一旦运行此脚本，生成的 `理论/processed_chunks/` 和 `理论/vector_db/`
将被 `.gitignore` 忽略，请勿强制上传至公开代码库！

======================================================================
""")

if __name__ == "__main__":
    print_instructions()
    # 如果用户自行下载了书籍并配置好了依赖，可以在这里写重建向量库的逻辑。
    # 示例代码（未激活）：
    # check_dependencies()
    # print("开始读取理论库文件...")
    # ...
    # print("重建向量库完毕，保存在 理论/vector_db/")
