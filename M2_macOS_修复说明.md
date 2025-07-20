# AugmentCode-Free M2 macOS GUI 修复说明

## 问题描述

在 M2 芯片的 macOS 系统上运行 AugmentCode-Free 时，可能会遇到以下 GUI 显示问题：

- ✅ GUI 窗口能正常启动
- ❌ 窗口内的 UI 元素（按钮、文本等）不可见
- ✅ 虽然看不到按钮，但点击空白区域仍能触发功能
- ❌ 界面元素在视觉上没有正确渲染

## 问题原因

经过分析，问题主要由以下因素导致：

1. **tkinter 版本兼容性**: macOS 自带的 tkinter 8.5 在 M2 芯片上存在渲染问题
2. **字体兼容性**: 使用了 'Microsoft YaHei' 等在 macOS 上不存在的字体
3. **颜色方案**: 某些颜色组合在 M2 macOS 上可能不可见
4. **Canvas 渲染**: 复杂的 Canvas 操作在 tkinter 8.5 上可能失效

## 修复方案

### 方案一：使用修复后的标准版本

已对原始 `gui.py` 进行了以下修复：

1. **字体修复**:
   - 替换 'Microsoft YaHei' 为 macOS 系统字体 'SF Pro Display'
   - 添加跨平台字体检测机制

2. **颜色方案优化**:
   - 使用 macOS 系统颜色方案
   - 主色调：`#007AFF` (系统蓝色)
   - 背景色：`#F2F2F7` (系统背景色)
   - 文字色：`#1C1C1E` (系统文字色)

3. **渲染优化**:
   - 简化 Canvas 操作
   - 优化按钮绘制逻辑

### 方案二：使用 M2 兼容版本

创建了专门的 `gui_m2_compatible.py`，特点：

1. **简化设计**: 避免复杂的 Canvas 操作
2. **标准组件**: 使用标准 tkinter 组件而非自定义组件
3. **兼容字体**: 使用 Helvetica 等标准字体
4. **稳定渲染**: 确保在 tkinter 8.5 上正常显示

## 使用方法

### 方法一：自动启动脚本（推荐）

```bash
./start_m2.sh
```

此脚本会：
- 自动检测系统环境
- 选择最适合的版本
- 应用必要的环境变量修复

### 方法二：手动选择版本

#### 启动修复后的标准版本：
```bash
TK_SILENCE_DEPRECATION=1 python3 main.py
```

#### 启动 M2 兼容版本：
```bash
TK_SILENCE_DEPRECATION=1 python3 gui_m2_compatible.py
```

#### 使用图形化启动器：
```bash
python3 start_m2_macos.py
```

### 方法三：测试修复效果

运行测试脚本验证 GUI 元素是否正确显示：
```bash
python3 test_gui_fix.py
```

## 环境变量说明

- `TK_SILENCE_DEPRECATION=1`: 静默 tkinter 弃用警告
- `PYTHONPATH`: 确保模块路径正确

## 修复详情

### 已修复的文件

1. **gui.py**: 原始 GUI 文件的修复版本
   - 字体替换为系统字体
   - 颜色方案优化
   - Canvas 渲染改进

2. **gui_m2_compatible.py**: M2 专用兼容版本
   - 简化的按钮组件
   - 标准 tkinter 组件
   - 兼容性优先设计

3. **test_gui_fix.py**: GUI 测试脚本
   - 验证各种 UI 元素显示
   - 系统信息检测

4. **start_m2_macos.py**: 图形化启动器
   - 自动检测系统环境
   - 智能版本选择

5. **start_m2.sh**: 命令行启动脚本
   - 自动环境配置
   - 版本自动选择

### 修复的具体问题

1. **字体问题**:
   ```python
   # 修复前
   font=('Microsoft YaHei', 12)
   
   # 修复后
   font=('SF Pro Display', 12)  # macOS
   font=('Helvetica', 12)       # 兼容版本
   ```

2. **颜色问题**:
   ```python
   # 修复前
   bg='#4f46e5'  # 可能不可见的颜色
   
   # 修复后
   bg='#007AFF'  # macOS 系统蓝色
   ```

3. **背景色问题**:
   ```python
   # 修复前
   bg='#f5f5f5'
   
   # 修复后
   bg='#F2F2F7'  # macOS 系统背景色
   ```

## 验证修复效果

修复成功后，您应该能看到：

- ✅ 清晰可见的按钮和文字
- ✅ 正确的颜色显示
- ✅ 流畅的界面交互
- ✅ 正常的功能操作

## 故障排除

如果仍有问题，请尝试：

1. **重启终端**: 确保环境变量生效
2. **检查 Python 版本**: 建议使用 Python 3.9+
3. **更新 tkinter**: 如果可能，升级到 tkinter 8.6+
4. **使用兼容版本**: 强制使用 `gui_m2_compatible.py`

## 技术细节

### 系统检测逻辑

```python
def check_system():
    system = platform.system()
    processor = platform.processor()
    is_apple_silicon = "Apple" in subprocess.run(
        ['sysctl', '-n', 'machdep.cpu.brand_string'], 
        capture_output=True, text=True
    ).stdout
    return is_apple_silicon
```

### 字体选择逻辑

```python
def get_system_font():
    if platform.system() == "Darwin":
        return "SF Pro Display"  # macOS 系统字体
    elif platform.system() == "Windows":
        return "Segoe UI"
    else:
        return "DejaVu Sans"  # Linux
```

## 总结

通过以上修复，AugmentCode-Free 现在能够在 M2 macOS 系统上正常显示和运行。修复方案考虑了：

- M2 芯片的特殊性
- tkinter 8.5 的兼容性问题
- macOS 系统的设计规范
- 用户体验的一致性

建议优先使用自动启动脚本 `./start_m2.sh`，它会自动选择最适合您系统的版本。
