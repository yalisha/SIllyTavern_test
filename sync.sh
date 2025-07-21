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

# 计算总文件数用于显示进度
echo "正在计算文件总数..."
TOTAL_FILES=$(find "$LOCAL_DIR" -type f | wc -l)
echo "共发现 $TOTAL_FILES 个文件"

# 记录开始时间
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "开始同步: $START_TIME" >> "$LOG_FILE"

# 创建命名管道用于实时读取rsync输出
FIFO_FILE="/tmp/rsync_fifo_$$"
mkfifo "$FIFO_FILE"

# 设置计数器
SYNCED_FILES=0
PERCENT=0

# 执行 rsync 命令，并将输出重定向到命名管道
echo "开始同步 $LOCAL_DIR 到 $VPS_USER@$VPS_IP:$REMOTE_DIR"

# 根据认证方式选择rsync命令
if [ "$USE_SSHPASS" = true ]; then
  # 检查sshpass是否安装
  if ! command -v sshpass &> /dev/null; then
    echo "错误: 需要安装sshpass才能使用密码认证"
    echo "可以运行 'brew install sshpass' 安装"
    rm -f "$FIFO_FILE"
    exit 1
  fi
  
  sshpass -e rsync -avzu --info=progress2 --stats --delete -e "ssh -o StrictHostKeyChecking=no" "$LOCAL_DIR/" "$VPS_USER@$VPS_IP:$REMOTE_DIR" > "$FIFO_FILE" 2>&1 &
else
  rsync -avzu --info=progress2 --stats --delete -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o BatchMode=yes -p $SSH_PORT" "$LOCAL_DIR/" "$VPS_USER@$VPS_IP:$REMOTE_DIR" > "$FIFO_FILE" 2>&1 &
fi

RSYNC_PID=$!

# 实时读取rsync输出并显示进度
cat "$FIFO_FILE" | tee "$TEMP_FILE" | while read -r line; do
  # 处理进度信息
  if [[ "$line" =~ ^[[:space:]]*([0-9]+)% ]]; then
    CURRENT_PERCENT="${BASH_REMATCH[1]}"
    if [ "$CURRENT_PERCENT" != "$PERCENT" ]; then
      PERCENT=$CURRENT_PERCENT
      echo -ne "\r同步进度: $PERCENT% "
    fi
  elif [[ "$line" == *"to-check="*"/"* ]]; then
    # 提取已检查的文件数和总文件数
    if [[ "$line" =~ to-check=([0-9]+)/([0-9]+) ]]; then
      REMAINING="${BASH_REMATCH[1]}"
      TOTAL="${BASH_REMATCH[2]}"
      DONE=$((TOTAL - REMAINING))
      PERCENT=$((DONE * 100 / TOTAL))
      echo -ne "\r同步进度: $PERCENT% ($DONE/$TOTAL) "
    fi
  fi
  
  # 输出正在同步的文件 - 修复正则表达式
  if [[ "$line" =~ ^[[:space:]]*[\<\>].+$ ]]; then
    FILENAME=$(echo "$line" | sed -E 's/^[[:space:]]*[\<\>][[:space:]]+(.*)/\1/')
    echo -e "\n正在同步: $FILENAME"
    SYNCED_FILES=$((SYNCED_FILES + 1))
  fi
done

# 等待rsync完成
wait $RSYNC_PID
RSYNC_EXIT=$?

# 删除FIFO文件
rm -f "$FIFO_FILE"

# 输出同步结果
echo -e "\n"
if [ $RSYNC_EXIT -eq 0 ]; then
  echo "同步成功，共同步 $SYNCED_FILES 个文件"
  echo "同步成功，共同步 $SYNCED_FILES 个文件" >> "$LOG_FILE"
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

# 计算并显示总耗时
START_SECONDS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$START_TIME" "+%s")
END_SECONDS=$(date -j -f "%Y-%m-%d %H:%M:%S" "$END_TIME" "+%s")
DURATION=$((END_SECONDS - START_SECONDS))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))
echo "总耗时: ${MINUTES}分${SECONDS}秒"

# 输出日志文件位置
echo "日志文件: $LOG_FILE"
