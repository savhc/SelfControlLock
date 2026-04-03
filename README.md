## 中文版文档

### SelfControlLock

一个 Python 脚本，在指定时间段内锁定计算机，需通过可配置次数的紧急点击解锁。锁定时禁用任务管理器并阻止键盘输入。

### 功能

- 设定锁机起止时间（格式：月.日.时:分）
- 通过重复点击按钮紧急解锁（默认 3000 次）
- 状态自动持久化，重启后恢复锁机状态
- 可选开机自启动
- 禁用任务管理器（`DisableTaskMgr` 注册表项）
- 使用 `pynput` 阻止键盘输入

### 环境要求

- Python 3.6+
- Windows 操作系统（注册表与全屏锁定依赖 Windows API）
- 依赖库：
  - `pynput`
  - `tkinter`（Python 标准库）

安装依赖：
```bash
pip install pynput
```

### 使用方法

运行脚本：
```bash
python lock.py
```

1. 输入开始与结束时间，格式 `月.日.时:分`（例如 `12.31.23:59`）
2. 设置紧急退出所需点击次数（最低 100）
3. 可选开启“开机自启动”
4. 点击“开始锁机”

锁机状态下：
- 窗口全屏并置顶
- 键盘输入被屏蔽
- 反复点击“紧急退出”直到点击次数达到阈值
- 到达结束时间后自动解锁

### 状态文件

`lock_state.json` 存储锁机计划、点击次数与锁机状态。若在锁机状态下重启程序，将自动恢复锁机界面。

### 已知限制

- 不屏蔽鼠标输入
- 全屏锁机可通过终止进程绕过（任务管理器已被禁用，但其他进程终止工具仍可能生效）
- 时间解析基于当前年份，跨年需手动调整

### 许可证

Unlicense – 无任何使用限制
# SelfControlLock

A Python script that locks the computer during a specified time window and requires a configurable number of emergency clicks to unlock. Disables Task Manager and blocks keyboard input while locked.

## Features

- Schedule lock start and end times (month.day.hour:minute)
- Emergency unlock via repeated button clicks (default 3000 clicks)
- Automatic state persistence across reboots
- Optional startup registration
- Disables Task Manager (`DisableTaskMgr` registry key)
- Blocks keyboard input using `pynput`

## Requirements

- Python 3.6+
- Windows OS (registry and full‑screen lock rely on Windows APIs)
- Dependencies:
  - `pynput`
  - `tkinter` (included with standard Python)

Install dependencies:
```bash
pip install pynput
```

## Usage

Run the script:
```bash
python lock.py
```

1. Enter start and end time in format `month.day.hour:minute` (e.g., `12.31.23:59`).
2. Set the required number of emergency clicks (minimum 100).
3. Optionally enable “开机自启动” (run on Windows login).
4. Click “开始锁机”.

While locked:
- The screen is full‑window and always on top.
- Keyboard input is blocked.
- Click “紧急退出” repeatedly until the click counter reaches the threshold.
- The lock automatically ends when the scheduled end time is reached.

## State File

`lock_state.json` stores the lock schedule, click count, and lock status. The script restores the lock state if restarted while locked.

## Limitations

- Does not block mouse input (only keyboard).
- Full‑screen lock can be bypassed by terminating the process (Task Manager is disabled, but other process killers may work).
- Time parsing is year‑sensitive: assumes the current year; crossing a year boundary requires manual adjustment.

## License

Unlicense – free for any use.
