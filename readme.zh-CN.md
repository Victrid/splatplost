# Splatplost

[English](readme.md)

Splatplost是一个基于[libnxctrl](https://github.com/Victrid/libnxctrl)的斯普拉遁投稿绘图器，与以前常用的需要Teensy或基于AVR的微控制器的USB绘图器不同，你只需要一台有蓝牙连接的电脑。通过优化的打印算法，这可以为你节省1/3的打印时间。

## 基本用法

### 安装

建议使用一台物理的linux机器。如果你没有，你可以从[Ubuntu](https://www.ubuntu.com/download/desktop)下载一个Live-CD，然后继续。不支持Windows或MacOS，因为libnxctrl是基于bluez的，即Linux的蓝牙协议栈。

你需要使用`sudo`，或root用户，因为改变蓝牙是一个特权操作。

```bash
sudo pip install splatplost
```

这将自动安装所需的依赖项。

如果你需要更新库，你可以使用`pip install --upgrade splatplost`。

### 使用

生成一个绘图计划：

```bash
sudo splatplan -i <你的图像> -o <输出文件名>
```

启动绘图器：

```bash
sudo splatplot --order <输出文件名>
```

你可以检查绘图器的选项（例如稳定模式，自定义延迟和按键时间，等等），使用：

```bash
sudo splatplot --help
```

当屏幕上显示 "Open the pairing menu on switch. " 时，进入配对菜单，Switch将被配对。

然后你可以进入游戏，用你自己的手柄进入斯普拉遁投稿界面。记得把刷子设置为最小的一个。

当一切准备就绪后，断开你自己的手柄，（例如，按下手柄顶部的小配对按钮），你将进入 "连接到手柄" 菜单。

按照指示按回车键或 "A" 键，绘图将开始。你可以看到打印时的进度和预计完成的时间。

## 需要帮助/我发现了一个错误/功能请求

点击上面的"Issue"链接，在资源库上打开一个Issue。

如果你发现连接上的错误，请在[libnxctrl](https://github.com/Victrid/libnxctrl)上打开一个Issue。
## 贡献



## 许可证

这个项目是基于libnxctrl的，所以它在GPLv3下发布。
