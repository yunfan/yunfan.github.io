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

!(目标机)[images/alpinelinux/host.jpeg]
