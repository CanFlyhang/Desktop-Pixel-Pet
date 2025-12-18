import argparse
import sys
import os

# 将项目根目录添加到路径以便导入 core 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.license_manager import LicenseManager

def main():
    parser = argparse.ArgumentParser(description="生成桌宠激活密钥 (License Key Generator)")
    parser.add_argument("username", nargs="?", help="目标用户的用户名")
    parser.add_argument("pet_name", nargs="?", help="要解锁的宠物名称 (例如: 黄金像素龙)")
    
    args = parser.parse_args()
    
    # 如果未提供命令行参数，则进入交互模式
    if not args.username:
        print("进入交互模式 (Ctrl+C 退出)")
        args.username = input("请输入用户名: ").strip()
        
    if not args.username:
        print("错误: 用户名不能为空")
        return

    if not args.pet_name:
        args.pet_name = input("请输入宠物名称 (例如: 黄金像素龙): ").strip()
        
    if not args.pet_name:
        print("错误: 宠物名称不能为空")
        return
    
    key = LicenseManager.generate_key(args.username, args.pet_name)
    print("\n" + "="*40)
    print(f" 用户: {args.username}")
    print(f" 宠物: {args.pet_name}")
    print("-" * 40)
    print(f" 激活密钥: {key}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
