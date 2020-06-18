# 多关键词相关性排序可搜索加密app

本项目是毕业设计***基于数据加密的端云访问控制方法***的演示app。

前端通过@vue/cli搭建脚手架并通过hbuilder打包成安卓app

服务器通过linux + apache + mysql + django的模式实现后端api

## 文件说明

```
searchable_encryption
│   readme.md
│   manage.py
|
└───searchable_encryption -- django初始配置目录
|   |   ...
│
└───backend -- 后端api应用
│   │   ...
|
└───secure_encrypt_server -- 安全服务器模拟应用
│   │   ...
│   
└───cloud_client -- 前端app代码，即@vue/cli脚手架目录
|   |   ...
|   └───dist -- 根据配置文件，打包后的文件必须直接放在这个目录下
|
└───config -- 所有配置文件
|   |   config.py
|   |   logger.py -- 日志类
|   |   ...
|
└───logs -- 日志目录
|   |   ...
|
└───media -- 媒体文件目录
    └───encrypt_file -- 加密文件
    |   |   ...
    |
    └───secure_file -- 安全服务器文件
        |   ...
```

## 部署时遇到的问题

服务器环境如下：

操作系统centos7

> Linux version 3.10.0-1062.9.1.el7.x86_64 (mockbuild@kbuilder.bsys.centos.org) (gcc version 4.8.5 20150623 (Red Hat 4.8.5-39) (GCC) ) #1 SMP Fri Dec 6 15:49:49 UTC 2019`

数据库mysql
> mysql  Ver 15.1 Distrib 5.5.64-MariaDB, for Linux (x86_64) using readline 5.1`

web服务器apache
> Server version: Apache/2.4.6 (CentOS)
> Server built:   Aug  8 2019 11:41:18

后端框架django

> Python 3.7.6
>
> django3.0.2


### 1. RuntimeError: populate() isn't reentrant

一开始500错误，查看服务器日志，发现**RuntimeError: populate() isn't reentrant**这个错误，然后根据：

https://stackoverflow.com/questions/27093746/django-stops-working-with-runtimeerror-populate-isnt-reentrant

所说的改了django/apps/registry.py的内容，就可以看到具体的错误了。

### 2.路径问题

在python app的\__init\__.py中，引入logging库，需要创建文件，但是创建文件的路径和用python的测试服务器不同，最后的解决方法是把\__init__.py中的路径改为绝对路径，代码如下：

```python
import logging
from config.logger import logger_backend
import os
import datetime
from django.conf import settings
from django.conf import settings

# 初始化日志对象
def initialLogger():
  # 如果不存在logs文件夹则创建
  if not os.path.exists(os.path.join(settings.BASE_DIR,"logs/")):
    os.mkdir(os.path.join(settings.BASE_DIR,"logs/"))
  handler1 = logging.FileHandler(os.path.join(settings.BASE_DIR,"logs/backend." + str(datetime.date.today()) + ".log"),"a",encoding="utf8")
  handler2 = logging.StreamHandler()
  formatter1 = logging.Formatter(fmt="%(asctime)s [%(levelname)s] [%(lineno)d] >> %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
  formatter2 = logging.Formatter(fmt = "[%(levelname)s] >> %(message)s")
  handler1.setFormatter(formatter1)
  handler2.setFormatter(formatter2)
  handler1.setLevel(logging.DEBUG)
  handler2.setLevel(logging.INFO)
  logger_backend.setLevel(logging.DEBUG)
  logger_backend.addHandler(handler1)
  logger_backend.addHandler(handler2)

initialLogger()
```

这样就解决了python临时服务器和httpd执行代码时相对路径不一致的问题。

### 3.权限问题

1. apache用户需要python可执行文件以及python用到的所有包的读取执行权限，这里我给的是755
2. 所有代码文件都需要执行权限，这里我也给了755，但是apache显然还需要对`logs`文件夹进行创建文件和修改操作，因此对于`logs`目录给了777，同理`media`文件夹下存放上传的文件因此也需要777权限。

### 4.加载问题

在解决了一些问题之后，发现服务器日志报错：**timeout when reading response headers from daemon process**

>  这里我们参照：https://stackoverflow.com/questions/40413171/django-webfaction-timeout-when-reading-response-headers-from-daemon-process解决了这个问题

解决方法：在apache配置文件中加入：

```conf
WSGIApplicationGroup %{GLOBAL}
```

> 原因应该是项目中用了numpy库

### 5.注意的点

对于新安装的python包要确保权限正确

对于项目的所有代码都需要确保权限正确

### 下面是完整的apache虚拟机代码

```conf
<VirtualHost *:80>
    ServerName www.bingo.cn
    ServerAdmin 416778940@qq.com

    WSGIProcessGroup searchable_encryption
    WSGIDaemonProcess searchable_encryption python-path=/django_server/searchable_encryption python-home=/usr/local/python3.7
    WSGIScriptAlias /searchable_encryption /django_server/searchable_encryption/searchable_encryption/wsgi.py process-group=searchable_encryption
    <Directory "/django_server/searchable_encryption/searchable_encryption">
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    Alias /searchable_encryption_static /django_server/searchable_encryption/static
    Alias /searchable_encryption_media /django_server/searchable_encryption/media
    <Directory /django_server/searchable_encryption/static>
        Require all granted
    </Directory>
    <Directory /django_server/searchable_encryption/media>
        Require all granted
    </Directory>

    # 因为用了numpy库，所以要加这一行
    # https://stackoverflow.com/questions/40413171/django-webfaction-timeout-when-reading-response-headers-from-daemon-process
    WSGIApplicationGroup %{GLOBAL}
</VirtualHost>
```

## 几张截图

