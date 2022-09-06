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

生成一个绘图计划：

```bash
sudo splatplan -i <你的图像> -o <输出文件名>
```

启动绘图器：

```bash
sudo splatplot --order <输出文件名>
```

查看绘图器的选项（例如稳定模式，自定义延迟和按键时间，等等）：

```bash
sudo splatplot --help
```

当屏幕上显示 "Open the pairing menu on switch. " 时，进入 NS 的配对菜单，虚拟手柄将自动与 NS 配对。

然后用自己的手柄进入斯普拉遁投稿界面，并将笔刷设为最小。

准备完成后，断开自己的手柄，（可以按下手柄顶部的小配对按钮），NS 将提示 “请在需要使用的手柄上按下 L + R 键”。

按照指示按回车键或 "A" 键，绘图将开始，程序将会显示打印进度和预计完成时间。

## 需要帮助/遇到问题/功能请求

点击上方的 “Issue” 按钮，并提交一个 Issue。

碰到手柄连接和配对问题时，请在 [libnxctrl](https://github.com/Victrid/libnxctrl) 提交 Issue。

## 贡献



## 许可证

本项目基于 libnxctrl ，故采用 GPLv3 发布。
