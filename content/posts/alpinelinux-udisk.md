Title: alpinelinux的启动盘定制
Author: jyf
Date: 2025-01-21 13:00:00
Tags: alpinelinux,启动盘,syslinux,uefi
Slug: alpinelinux-udisk

# 缘由

我一直比较喜欢迷你发行版,但是作为一个懒人，自己却不太
爱每次都去定制 *initramfs* 这类东西，所以我发现 *alpinelinux*
可以极大满足我的这个癖好，因为他提供了一些特性让你可以把
定制外部化，形成一个tarball，然后在他的 *initramfs* 的启动
阶段加载你的这些定制。


另外一个问题是：我以前玩的板子，如果跑一般的系统，由于文件
系统频繁读写，会非常损u盘或者tf卡，而 *alpinelinux* 的 *diskless*
模式是系统加载到内存，除非你有意定制自己的一些服务读写盘，
否则没这个问题，这点非常适合我这种日常不审计日志的人


基于以上两点，我打算动手来做个定制包，目标为

+ 可以headless运行,也就是插上主机，加电即可最后引导至期望的系统
+ 自动修改hostname以及自动连网，我这里的case是wifi
+ 自动配置好sshd服务尤其是认证的公钥

以下截图是本次的目标机

![目标机](images/alpinelinux/host.jpeg)

# 实现步骤

## headless上电启动支持

这一步主要是要手动做个启动盘 同时由于我的目标机是现代机，支持uefi,
所以目标进一步细分为制作一个uefi支持的启动盘

uefi的规范比较复杂，网上的中文资料也很垃圾，同时他支持特性很多，网上
很多资料都是泛泛而谈，一般都涉及 `efibootmgr` 但我们是 `headless` 安装
所以实际不可能看到bios输出而去选择，因此我选择了一个最简单的玩法就是

+ 将启动盘按照uefi规范分区
+ 为启动盘安装适合的引导器，这里选择 **syslinux**

### 分区

uefi的默认启动分区叫 **esp** 要求是 **gpt**分区表的**vfat** 格式 实践
中一般不安排在第一个分区，防止跟mbr那类冲突，但是我这是uefi only的板
子,所以无所谓 就安排在了第一分区 以下是我网上抄来的脚本用于快速分区

```bash
#!/bin/bash

disk=/dev/sdb

wipefs -a $disk 

# Not sure if this is required but can't hurt
dd if=/dev/zero of=$disk bs=1M count=100

# 设置磁盘分区格式为gpt
parted -s $disk mklabel gpt

# 开个ESP分区
# 1MiB 是 start位置，2GiB 是分区大小
parted -s --align=optimal $disk mkpart ESP fat32 1MiB 2GiB 
parted -s $disk set 1 esp on

# 2GiB 是 start位置，100% 是分区大小 意思使用剩下容量的百分百
# 要注意 这里的 start位置跟前面分区大小有关系 一定要计算好
# 切勿产生overlap
parted -s --align=optimal $disk mkpart ext4 2GiB 100%

sleep 10
 
mkfs.vfat -n EFI $disk'1' 
mkfs.ext4 -L ROOT $disk'2'
```

注意以上的 `disk=/dev/sdb` 这部分 请务必按照自己
设备实际情况修改，一定要仔细对照清楚，否则容易丢失数据

以上脚本我们把我的/dev/sdb设备(上图tf卡) 转成了gpt分区表
同时新建了俩分区，第一个是esp也就是启动用的，第二个是
预备将来用作数据区的

### 安装与配置引导器

这里选择的是 syslinux 同时目标机是x86_64架构，按uefi规范
系统会自动加载 `esp分区/efi/boot/bootx64.efi` 这个文件
这里我们可以去 syslinux官网下载对应的 x86_64 架构的 syslinux.efi
文件放到前述位置，同时在相同目录下提供一个配置文件 `syslinux.cfg`

对于debian系用户，可直接安装包 `syslinux-efi` 安装完以后 可以
在目录 `/usr/lib/SYSLINUX.EFI/efi64/` 下找到引导器 `syslinux.efi`

同时在 `/usr/lib/syslinux/modules/` 有所有依赖的功能项，可以按需
或者全部复制到 `esp分区/efi/boot/` 目录下,我选择的就是后者

最后我的配置文件如下

```cfg
ui menu.c32
timeout 30
prompt 0

menu title boot menu

default lts

label lts
        linux /boot/vmlinuz-lts
        initrd /boot/initramfs-lts
        append modules=loop,squashfs,sd-mod,usb-storage,iwlmvm debug
```

最后，将官网下载下来的 `alpinelinux` 的iso文件里面的内容复制到esp分区里

至此，如果你讲目标机上电他就会启动到默认的alpinelinux的官方默认状态

## alpinelinux定制

### 原理

alpinelinux有个机制，他会在启动阶段去initramfs所在的分区根目录里搜索任意名字
的 `.apkovl.tar.gz` 文件并作为overlay挂载到系统分区上，利用这个特性
可以实现不重新打包官方的initramfs文件而定制系统的目的

由于后续的lbu工具有bug 无法从环境里找到当前使用apkovl文件的名字，所以
我们只好将定制文件命名为 **lark.apkovl.tar.gz** 这里的 lark 是我准备
给目标机定制的 `hostname` 如果你不打算定制这个，就使用 `localhost.apkovl.tar.gz`
这个名字 

同时如果我们想要给alpinelinux预装一些软件，我们需要

+ 将相关的apk文件放到esp分区下的 **apks** 目录下
+ 将待安装的程序名增加到apkovl定制包的 `etc/apk/world` 里

如果我们预装的是服务，除了安装以外，我们还需要将相关的服务启动文件
加入到启动目录下启动目录一般有

+ `etc/runlevels/sysinit`
+ `etc/runlevels/boot`
+ `etc/runlevels/default`

应该在定制包里建立这些目录，并且做一些软连接，连接到相关的服务文件

我建议一般人可以把目标机接上屏幕和键盘，然后上电启动到alpinlinux登陆

使用root无密码登陆系统以后，直接执行 `lbu ci sdb1` 来生成一个初始化的

定制包，当然我本人的是自己定制一部分以后再生成的 这里的 sdb1是我目标

机上的媒体设备名，大家应该执行下 `mount` 命令，看看启动分区被挂载到了

哪里，一般是 `/media/xxx` 这里的xxx在我本机就是 sdb1 如果在你机器上是

`/media/usb` 则你应该执行的命令为 `lbu ci usb`

以下的具体的定制过程

注意我说的修改定制包是指

+ 先解开 apkovl.tar.gz 文件到一个指定目录
+ 在此目录基础上做相关修改
+ 将此目录重新打包成 apkovl.tar.gz 文件

### hostname

修改定制包 

+ 增加文件 `etc/hostname` 里面内容为 `lark` 也就是我要的hostname
+ 增加软连接 `etc/runlevels/default/hostname` 链接到 `../../init.d/hostname` 

至此，目标机上电并启动后，hostname会自动调整为 lark

### 无线网络

修改定制包

+ 修改文件 `etc/apk/world` 增加wpa_supplicant
+ 增加文件 `etc/wpa_supplicant/wpa_supplicant.conf` 上网查下怎么根据wifi ap名
  和密码来生成此文件 提示是用 `wpa_passphare`
+ 增加文件 `etc/conf.d/wpa_cli.sh` 里面的内容为 `WPACLI_OPTS="-a /etc/wpa_supplicant/wpa_cli.sh"`
+ 增加软连接 `etc/runlevels/boot/networking` 链接到 `../../init.d/networking` 
+ 增加软连接 `etc/runlevels/boot/wpa_cli` 链接到 `../../init.d/wpa_cli` 
+ 增加软连接 `etc/runlevels/boot/wpa_supplicant` 链接到 `../../init.d/wpa_supplicant` 
+ 增加软连接 `etc/runlevels/boot/hwclock` 链接到 `../../init.d/hwclock` 

至此，目标机上电并启动后，会自动使用给出的密码链接配置的无线网络ap名并获得ip

并且在局域网里广播mdns名 lark

### ssh

修改定制包

+ 修改文件 `etc/apk/world` 增加openssh-server
+ 增加软连接 `etc/runlevels/default/sshd` 链接到 `../../init.d/sshd` 
+ 增加文件 `etc/apk/protected_paths.d/lbu.list` 内容为 
```
+add
+root/.ssh/authorized_keys
  ```
+ 增加文件 `/root/.ssh/authorized_keys` 并注意对整个`/root/.ssh/` 目录
  分配权限为600

至此，目标机上电并启动后，会自动使用给出的密码链接配置的无线网络ap名并获得ip

并且在局域网里广播mdns名 lark, 同时局域网同志们都可以用 `指定的公钥免密码登陆```
