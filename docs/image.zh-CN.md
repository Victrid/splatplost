# 使用预配置镜像

如果你遇到了以下问题：
- 报错 Type is not subscriptable（Python 3.9 左右改变的类型标记语法导致）
- 关于 "dbus-python" 和蓝牙的任何问题
- 不能发现 Switch，卡在 "Open pair menu"（可能是虚拟机软件的蓝牙问题）
- 没有 Linux 物理机，也不准备使用虚拟机

可以下载预配置镜像，并使用 [Balena Etcher](https://www.balena.io/etcher/) 将其烧录到U盘上。（U 盘随后可通过重新格式化的方法恢复正常使用）

下载链接 (约 1.8GB)：
> mega 网盘: https://mega.nz/file/CSBgnZpT#Us49WL1WAp0S_qww1qobISAWMDZ-COvCAOq14NHej3k
> 
> 天翼云盘: https://cloud.189.cn/web/share?code=NNviyqZjuUZn （访问码: sfo9）
> 
> 百度盘:  https://pan.baidu.com/s/1182YwpjhaqwoLjEvUeM_9g?pwd=jxdb (提取码: jxdb)

（如果你有更好的文件分享方法，欢迎提交 Issue！）

重新启动你的电脑，并进入启动项菜单（根据电脑厂商不同，一般是按 F12、F2、F10 或 F8 等，具体情况可通过说明书或搜索引擎了解），在菜单中选择 U 盘。

如果你的电脑是近几年购买的，并预装了 Windows，则可能会遇到 "Secure Boot 禁止从 USB 启动" 的问题。这需要在 BIOS 中禁用 Secure Boot（在完成全部操作后可能需要重新启用，否则 windows 可能无法启动）相关操作方法可以查看说明书或使用搜索引擎查找。

启动后，系统会进入桌面环境，点击桌面上的图标 "Konsole" 来打开一个终端。（需要将系统先连接至互联网）

在终端中运行 `install_splatplost`，即可正常使用 Splatplost。后续操作可见 readme.md 的 "使用" 部分。

需要注意的是，通过此方法启动的系统无法读取电脑中的硬盘，所有更改也不会保存，因此每次启动都需要重新运行`install_splatplost`。想要读取电脑硬盘中的文件需要对 Linux 的一些基础操作有所了解，如果你不会操作，可以将需要打印的图片存在网盘里，随后通过系统中的 FireFox 浏览器下载。此外，还可以事先将图片保存到另一 U 盘中，在系统启动后插入这一 U 盘，即可读取 U 盘中的文件。

## 在本地创建镜像（高阶操作）

使用装有 Arch Linux 的设备上（虚拟机和实体机都可以），安装`archiso`， 在`imagebuilder`文件夹中运行：
```bash
make build_packages
make build
```

执行`make clean_all`以清除生成物。
