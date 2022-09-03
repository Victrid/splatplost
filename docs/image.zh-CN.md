# 使用预配置镜像

如果你遇到了这样的问题：
- 报错 Type is not subscriptable（这是在python 3.9左右改变的类型标记语法导致的一个问题）
- 关于 "dbus-python" 和蓝牙的任何问题
- 不能发现Switch，卡在 "Open pair menu"（这可能是你的虚拟机软件的蓝牙问题）。
- 没有linux机器，也没有用过虚拟机

你可以下载可刷写的镜像，并使用[Balena Etcher](https://www.balena.io/etcher/)将其烧录到U盘上。（此后可以用同样的方法恢复正常，不会影响您的U盘）

下载链接 (约1.8GB)：
> mega网盘: https://mega.nz/file/CSBgnZpT#Us49WL1WAp0S_qww1qobISAWMDZ-COvCAOq14NHej3k
> 
> 天翼云盘: https://cloud.189.cn/web/share?code=NNviyqZjuUZn （访问码: sfo9）
> 
> 百度盘:  https://pan.baidu.com/s/1182YwpjhaqwoLjEvUeM_9g?pwd=jxdb (提取码: jxdb)

（如果你有更好的文件分享方法，欢迎开Issue！）

重新启动你的电脑，并进入启动菜单。这通常是通过按F12、F2、F10或F8，或其他键来完成的，取决于你的电脑。你可能需要查看你的电脑手册。选择你的U盘来继续。

如果你的电脑是最近买的，预先安装了Windows，你可能会遇到诸如 "Secure Boot禁止你从USB启动" 的问题。你可能需要在你的BIOS中禁用Secure Boot。(你可以在使用镜像后重新启用它，否则你的Windows可能无法启动）你可能需要查看你的计算机手册。

启动后，你应该看到一个桌面环境，上面有一个图标 "Konsole"。连接到互联网（在底部系统托盘上），并点击它来打开一个终端。

在终端中运行 `install_splatplost`，之后一切都应该准备好了。继续阅读readme.md的 "使用" 部分。

需要注意的是，该镜像不会访问您电脑本机中的硬盘，因此每次启动都需要重新运行 `install_splatplost`。访问您电脑上的文件需要一些Linux的使用技巧，如果您不具备的话，可以将您的大作存在网盘里，在镜像的Firefox浏览器中下载。

## 在本地创建镜像（高阶操作）

使用装有Arch Linux的设备上（虚拟机和实体机都可以），安装`archiso`， 在`imagebuilder`文件夹中运行：
```bash
make build_packages
make build
```

执行`make clean_all`以清除生成物。