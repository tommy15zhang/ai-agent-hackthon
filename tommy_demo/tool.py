import os
import shutil

def flatten_directory(root_dir):
    """
    将目标目录下所有子目录中的文件移动到根目录，并保留文件名冲突的文件
    """
    # 获取所有需要移动的文件路径（排除根目录自身文件）
    file_paths = []
    for foldername, _, filenames in os.walk(root_dir):
        if foldername == root_dir:
            continue  # 跳过根目录
        for filename in filenames:
            file_paths.append(os.path.join(foldername, filename))

    # 移动文件并处理重名
    for src_path in file_paths:
        # 提取基础文件名
        base_name = os.path.basename(src_path)
        
        # 构造目标路径
        dest_path = os.path.join(root_dir, base_name)
        
        # 处理文件名冲突
        counter = 1
        name, ext = os.path.splitext(base_name)
        while os.path.exists(dest_path):
            new_name = f"{name} ({counter}){ext}"
            dest_path = os.path.join(root_dir, new_name)
            counter += 1
        
        # 移动文件
        shutil.move(src_path, dest_path)
        print(f"Moved: {src_path} -> {dest_path}")

    # 删除空目录（自底向上删除）
    for foldername, _, _ in os.walk(root_dir, topdown=False):
        if foldername != root_dir:
            try:
                os.rmdir(foldername)
                print(f"Removed empty directory: {foldername}")
            except OSError:
                pass  # 目录不为空时会跳过

if __name__ == "__main__":
    target_dir = "C:/Users/jacky/Desktop/Test files"
    if os.path.isdir(target_dir):
        flatten_directory(os.path.abspath(target_dir))
        print("操作完成！")
    else:
        print("错误：输入的路径不是有效的目录")