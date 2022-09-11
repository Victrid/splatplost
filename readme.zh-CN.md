# Splatplost

[English](readme.md)

Splatplost 是一个基于 [libnxctrl](https://github.com/Victrid/libnxctrl) 的斯普拉遁投稿绘图器，与以往的需要 Teensy 或基于 AVR 的微控制器的 USB 绘图方案不同，你只需要一台拥有蓝牙适配器的电脑，并且通过优化打印算法，可以节省 1/3 的打印时间。

## 基本用法

### 安装

建议使用 Linux 物理机。如果没有现成机器，可以使用 [预配置镜像](docs/image.zh-CN.md) 中的方法进行配置。由于 libnxctrl 是基于 bluez 这一 Linux 蓝牙协议栈的，本项目不支持 Windows 或 MacOS。

由于操作蓝牙适配器需要 root 权限，你需要使用`sudo`或 root 用户运行相关命令。

```bash
sudo pip install splatplost
```

这将自动安装所需的依赖。

如果你需要更新软件，可以使用`pip install --upgrade splatplost`。

### 使用

启动 GUI 界面：

```bash
sudo splatplost
```

## 需要帮助/遇到问题/功能请求

点击上方的 “Issue” 按钮，并提交一个 Issue。

碰到手柄连接和配对问题时，请在 [libnxctrl](https://github.com/Victrid/libnxctrl) 提交 Issue。

## 贡献

- **程序的国际化**: 不需要编程基础，详见[翻译](docs/translation.zh-CN.md)。
- **程序的文档**: 不需要编程基础。
- 帮助解决Issue
- 程序的重构与Bug清理
- 算法的优化

## 许可证

本项目基于 libnxctrl ，故采用 GPLv3 发布。
