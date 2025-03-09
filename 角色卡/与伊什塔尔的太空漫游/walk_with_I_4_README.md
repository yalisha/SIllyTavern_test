# Walk With I - 4 Setup UI

这是为《Walk With I - 4》游戏创建的角色设置用户界面，用于与SillyTavern集成。

## 功能概述

该UI允许玩家通过四个阶段设置他们的角色：

1. **基础信息**：选择性别、个人特质和所属势力
2. **势力信息**：选择契约从者、所在位置和战舰特质
3. **开局事件**：选择游戏的初始事件
4. **确认信息**：查看所有选择并确认创建角色

## 安装指南

1. 将以下文件复制到SillyTavern的`public`目录中：
   - `walk_with_I_4_setup.html`
   - `walk_with_I_4_setup.js`

2. 创建以下目录和资源：
   - `public/fonts/` - 放置字体文件（FZCuHeiSongGB.ttf）
   - `public/images/` - 放置背景和图标图像

3. 在SillyTavern的HTML中添加脚本引用：
   ```html
   <script src="walk_with_I_4_setup.js"></script>
   ```

## 使用方法

1. 在SillyTavern界面中，点击"Walk With I - 4 设置"按钮打开设置界面。
2. 按照提示完成四个设置阶段。
3. 点击"确认创建"按钮将角色设置发送给AI。

## 自定义选项

您可以通过编辑`walk_with_I_4_setup.html`文件来修改可用的选项：

- 性别选项
- 个人特质
- 势力选项
- 契约从者
- 位置选项
- 战舰特质
- 开局事件

## 注意事项

- 需要SillyTavern环境才能完全运行
- 推荐使用现代浏览器以获得最佳体验
- 字体和图像需要单独提供

## 设计风格

界面设计采用扁平化书籍风格，灵感来自战锤40K的美学：

- 深色背景与金色/红色强调
- 书籍式布局
- 帝国图标作为装饰元素
- 中文使用方正粗黑宋字体
- 英文使用Times New Roman字体

## 技术细节

- 纯HTML, CSS和JavaScript实现
- 无外部依赖
- 通过postMessage API与SillyTavern通信
- 响应式设计，适应不同屏幕尺寸 