#!/bin/bash

# 定义变量
LOCAL_DIR="/Users/mac/SillyTavern/data"
VPS_USER="root"
VPS_IP="154.217.241.20"
REMOTE_DIR="/root/SillyTavern/data"
LOG_FILE="/tmp/rsync_sync.log" #定义日志文件的位置
TEMP_FILE="rsync_temp.log" # 定义临时文件，使用相对路径
SSH_KEY="$HOME/.ssh/id_rsa" # 指定SSH密钥位置
SSH_PORT="22" # 指定SSH端口，默认为22

# 检查目录是否存在
if [ ! -d "$LOCAL_DIR" ]; then
  echo "错误：本地目录 $LOCAL_DIR 不存在"
  exit 1
fi

# 检查SSH密钥是否存在
if [ ! -f "$SSH_KEY" ]; then
  echo "错误：SSH密钥 $SSH_KEY 不存在"
  exit 1
fi

echo "===== 测试SSH连接 ====="
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 "$VPS_USER@$VPS_IP" "echo 连接成功" > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "SSH连接测试失败! 尝试检查以下几点:"
  echo "1. 确保.ssh目录权限正确: chmod 700 ~/.ssh"
  echo "2. 确保密钥文件权限正确: chmod 600 $SSH_KEY"
  echo "3. 确保密钥已添加到远程服务器的authorized_keys中"
  echo "4. 尝试手动测试连接: ssh -i $SSH_KEY $VPS_USER@$VPS_IP"
  echo ""
  echo "是否尝试使用密码登录? (y/n)"
  read -r use_password
  
  if [[ "$use_password" == "y" ]]; then
    echo "请输入远程服务器的密码: "
    read -rs password
    export SSHPASS="$password"
    USE_SSHPASS=true
  else
    echo "退出同步脚本"
    exit 1
  fi
else
  echo "SSH连接测试成功!"
  USE_SSHPASS=false
fi

# 记录开始时间
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "开始同步: $START_TIME" >> "$LOG_FILE"

# 执行 rsync 命令，并将输出保存到临时文件
echo "开始同步 $LOCAL_DIR 到 $VPS_USER@$VPS_IP:$REMOTE_DIR"

# 根据认证方式选择rsync命令
if [ "$USE_SSHPASS" = true ]; then
  # 检查sshpass是否安装
  if ! command -v sshpass &> /dev/null; then
    echo "错误: 需要安装sshpass才能使用密码认证"
    echo "可以运行 'brew install sshpass' 安装"
    exit 1
  fi
  
  sshpass -e rsync -avzu --delete -e "ssh -o StrictHostKeyChecking=no" "$LOCAL_DIR/" "$VPS_USER@$VPS_IP:$REMOTE_DIR" > "$TEMP_FILE" 2>&1
else
  rsync -avzu --delete -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o BatchMode=yes -p $SSH_PORT" "$LOCAL_DIR/" "$VPS_USER@$VPS_IP:$REMOTE_DIR" > "$TEMP_FILE" 2>&1
fi

# 检查 rsync 命令的退出代码
RSYNC_EXIT=$?
if [ $RSYNC_EXIT -eq 0 ]; then
  echo "同步成功"
  echo "同步成功" >> "$LOG_FILE"
elif [ $RSYNC_EXIT -eq 23 ]; then
  echo "部分文件同步成功，但有些文件无法传输 (可能是权限问题)"
  echo "部分文件同步成功，但有些文件无法传输" >> "$LOG_FILE"
elif [ $RSYNC_EXIT -eq 255 ]; then
  echo "SSH连接失败，请检查SSH密钥及权限设置"
  echo "SSH连接失败，请检查SSH密钥及权限设置" >> "$LOG_FILE"
else
  echo "同步失败，错误代码: $RSYNC_EXIT"
  echo "同步失败，错误代码: $RSYNC_EXIT" >> "$LOG_FILE"
fi

# 将临时文件的所有内容添加到日志
cat "$TEMP_FILE" >> "$LOG_FILE"

# 分析临时文件的内容
cat "$TEMP_FILE" | while read line; do
  if [[ "$line" == *".d..t......"* ]]; then
    echo "同步了文件: ${line//.d..t....... /}"
    echo "同步了文件: ${line//.d..t....... /}" >> "$LOG_FILE"
  elif [[ "$line" == *"<f++++++++++"* ]]; then
    echo "新增了文件: ${line//<f++++++++++ /}"
    echo "新增了文件: ${line//<f++++++++++ /}" >> "$LOG_FILE"
  elif [[ "$line" == *">f++++++++++"* ]]; then
     echo "修改了文件: ${line//>f++++++++++ /}"
     echo "修改了文件: ${line//>f++++++++++ /}" >> "$LOG_FILE"
  elif [[ "$line" == *"deleting"* ]]; then
    echo "删除了文件: ${line//deleting /}"
    echo "删除了文件: ${line//deleting /}" >> "$LOG_FILE"
  elif [[ "$line" == *"rsync: connection unexpectedly closed"* ]]; then
    echo "rsync: 连接意外关闭"
    echo "rsync: 连接意外关闭" >> "$LOG_FILE"
  elif [[ "$line" == *"rsync error:"* ]]; then
    echo "rsync error: $line"
    echo "rsync error: $line" >> "$LOG_FILE"
  elif [[ "$line" == *"Permission denied"* ]]; then
    echo "权限被拒绝: $line"
    echo "权限被拒绝: $line" >> "$LOG_FILE"
  fi
done

# 清理临时文件
rm -f "$TEMP_FILE"

# 记录结束时间
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "结束同步: $END_TIME" >> "$LOG_FILE"

# 输出日志文件位置
echo "日志文件: $LOG_FILE"
