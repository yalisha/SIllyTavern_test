# -*- coding: utf-8 -*-
import os
import sys

# 尝试确保控制台能正确输出UTF-8字符 (特别是Windows)
if sys.stdout.encoding != 'utf-8':
    try:
        # 适用于 Python 3.7+
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # 备用方法 (可能效果有限)
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except Exception as e_io:
            print(f"警告: 无法将控制台输出设置为UTF-8: {e_io}", file=sys.stderr)
            print("某些特殊字符的文件名可能无法正确显示。", file=sys.stderr)
    except Exception as e:
        print(f"警告: 设置控制台编码时出错: {e}", file=sys.stderr)

def summarize_files_in_folders(folder_paths):
    """
    总结指定文件夹（包括子文件夹）中的所有文件名，忽略以 '!' 结尾的文件。

    Args:
        folder_paths (list): 需要扫描的文件夹路径列表。

    Returns:
        list: 一个包含所有有效文件名的列表（已去重并排序）。
              如果找不到有效文件或文件夹不存在/无法访问，则返回空列表。
    """
    all_valid_filenames = set() # 使用集合来自动处理重复的文件名

    print("\n开始扫描指定的文件夹...")
    print("-" * 30)

    for folder_path in folder_paths:
        # 规范化路径表示 (例如，处理 './' 或 '../')
        folder_path = os.path.normpath(folder_path)

        # 检查路径是否存在且是否为目录
        if not os.path.isdir(folder_path):
            print(f"警告：跳过无效路径 '{folder_path}' (不存在或不是文件夹)")
            continue

        print(f"正在扫描: {folder_path}")

        try:
            # os.walk 会递归遍历目录树
            # dirpath: 当前正在遍历的目录路径
            # dirnames: dirpath 下子目录的名字列表 (不含路径)
            # filenames: dirpath 下非目录文件的名字列表 (不含路径)
            for dirpath, dirnames, filenames in os.walk(folder_path):
                print(f"  检查目录: {dirpath}")
                count_in_dir = 0
                for filename in filenames:
                    # 检查文件名是否不以 '!' 结尾
                    if not filename.endswith('!'):
                        all_valid_filenames.add(filename)
                        count_in_dir += 1
                    else:
                        # (可选) 打印被忽略的文件信息
                        # print(f"    忽略文件: {os.path.join(dirpath, filename)}")
                        pass
                if count_in_dir > 0:
                    print(f"    在此目录找到 {count_in_dir} 个有效文件。")

        except OSError as e:
            print(f"错误：访问 '{folder_path}' 或其子文件夹时出错: {e}")
        except Exception as e:
            print(f"发生意外错误: {e}")

        print("-" * 30)

    # 将集合转换为列表，并按字母顺序排序
    return sorted(list(all_valid_filenames))

# --- 主程序执行部分 ---
if __name__ == "__main__":
    # --- !!! 用户配置区域 !!! ---
    # 请在这里修改或添加您要扫描的文件夹路径列表
    # 您可以使用绝对路径 (如 "C:/Users/YourUser/Documents" 或 "/home/youruser/data")
    # 也可以使用相对路径 (如 "my_folder" 或 "../project_files")
    # 相对路径是相对于您运行此脚本的位置
    folders_to_scan = [
        # === 在下面添加您要扫描的文件夹路径 ===
          # "." 代表当前运行脚本所在的目录
        "/Users/mac/Documents/SIllyTavern_test/角色卡/我的老婆们ver2/world/FATE系列人物",
        "/Users/mac/Documents/SIllyTavern_test/角色卡/我的老婆们ver2/world/同人人物-无超能力",
        "/Users/mac/Documents/SIllyTavern_test/角色卡/我的老婆们ver2/world/米家系列人物",
        "/Users/mac/Documents/SIllyTavern_test/角色卡/我的老婆们ver2/world/同人人物-超能力",
        "/Users/mac/Documents/SIllyTavern_test/角色卡/我的老婆们ver2/world/原创人物"
        # "C:/Users/Public/Documents", # Windows 示例路径
        # "/Users/your_username/Desktop", # macOS 示例路径
        # "path/to/your/folder1",
        # "path/to/your/folder2",
        # === 添加结束 ===
    ]
    # --- !!! 配置结束 !!! ---

    # --- (可选) 创建一些测试文件和目录用于演示 ---
    def setup_test_environment(base_dir="."):
        test_root = os.path.join(base_dir, "test_summary_folder")
        sub_folder = os.path.join(test_root, "sub_dir")
        os.makedirs(sub_folder, exist_ok=True)
        files_to_create = [
            os.path.join(test_root, "report.txt"),
            os.path.join(test_root, "image.jpg"),
            os.path.join(test_root, "temp_notes!"),       # 应被忽略
            os.path.join(test_root, "archive.zip"),
            os.path.join(sub_folder, "data.csv"),
            os.path.join(sub_folder, "config.ini!"),     # 应被忽略
            os.path.join(sub_folder, "script.py"),
            os.path.join(base_dir, "root_file.md"),       # 在根目录 (如果 '.' 在列表里)
            os.path.join(base_dir, "ignore_this_one!"), # 在根目录，应被忽略
        ]
        print("\n--- 创建测试文件和目录 (仅用于演示) ---")
        for f_path in files_to_create:
            try:
                # 确保使用utf-8编码写入文件，避免潜在问题
                with open(f_path, 'w', encoding='utf-8') as f:
                    f.write(f"这是文件: {os.path.basename(f_path)}")
                print(f"  已创建: {f_path}")
            except Exception as e:
                print(f"  创建失败: {f_path} ({e})")
        # 添加一个测试文件夹到扫描列表 (如果它还没在)
        if test_root not in folders_to_scan:
            folders_to_scan.append(test_root)
        print("--- 测试环境设置完毕 ---\n")

    # 如果你想运行测试设置，取消下面这行的注释
    # setup_test_environment()
    # ----------------------------------------------

    if not folders_to_scan or all(p == "." or not p for p in folders_to_scan):
         # 如果列表为空，或者只包含空字符串或 "." (当前目录的默认值)，提示用户
         if folders_to_scan == ["."]:
             print("提示: 当前只扫描脚本所在的目录 ('.')。")
             print("请编辑脚本中的 'folders_to_scan' 列表以添加其他文件夹。")
         else:
            print("错误：请在脚本的 'folders_to_scan' 列表中指定至少一个有效的文件夹路径。")
            sys.exit(1) # 退出程序

    # 调用函数执行扫描和总结
    valid_filenames = summarize_files_in_folders(folders_to_scan)

    # 打印最终结果
    print("\n" + "="*60)
    print("          文 件 名 总 结 结 果")
    print(f"  (已扫描文件夹: {', '.join(folders_to_scan)})")
    print("  (已忽略所有以 '!' 结尾的文件)")
    print("="*60)

    if valid_filenames:
        print("\n找到以下有效文件 (按字母顺序排列):")
        for i, filename in enumerate(valid_filenames, 1):
            # 尝试正确打印文件名，即使包含特殊字符
            try:
                print(f"{i}. {filename}")
            except UnicodeEncodeError:
                # 如果直接打印失败，尝试用替换模式编码再解码来显示
                safe_filename = filename.encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8', 'replace')
                print(f"{i}. {safe_filename} (部分字符可能无法正确显示)")

        print(f"\n在指定的文件夹及其子文件夹中，共找到 {len(valid_filenames)} 个有效文件。")
    else:
        print("\n在指定的文件夹中没有找到符合条件的文件（或者文件夹为空、无法访问）。")

    print("\n扫描完成。")

