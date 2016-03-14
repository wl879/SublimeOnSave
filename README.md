# OnSave plugin for Sublime Text 3



可以在你保存文件时，预设一些执行指令，如 Coffeescript、Teajs、Css、Jade 的预编译。

特点:
    OnSave plugin 可将输出内容显示到 Sublime Text 的编辑窗口中，更优雅的调试你的代码。

技巧:
    在输出的内容中可以双击文件目录格式的文本（例：~/Sites/index.html），将会跳转到目标文件



## 安装

目前只测式过在 Mac OS 下的 Sublime Text 3 版本


### Git installation

```
    Clone the repository in your Sublime Text "Packages" directory:
    
        git clone https://github.com/wl879/SublimeOnSave.git OnSave
        
    
    The "Packages" directory is located at:
    
    * OS X:
    
            ~/Library/Application Support/Sublime Text 3/Packages/
    
    * Linux:
    
            ~/.config/sublime-text-3/Packages/
    
    * Windows:
    
            %APPDATA%/Sublime Text 3/Packages/

```

## 使用


### 配置文件


* 新建在你的项目目录下 ".onsave" 文件，使用 yaml 语法配置
* 也可以在项目文件夹上 [右键] > [New OnSave config] 创建，模板如下：


```yaml

# 预设变量
VAR:
    #name: --test

# 全局设置

# 预设环境变量
ENV:
    #path: /usr/bin

# 开启输出显示的功能
DEBUG : refresh
        # false 不显示
        # true 显示在快捷的窗口中
        # 定义一个输出窗口的 ID，输出到一个标准文本编辑窗口中
            # ID + refresh 重新执行时清除上次输出的内容
            
# 设置执行的命令, 可设置多个
LISTENER:
    -
        # 需执行的命令
        CMD : echo "Hello world"
            
            # 内部变量
                # $ROOT     = 配置文件所在的目录
                # $FILE     = 当前文件路径
                # $FILENAME = 当前文件名
                # $FILEDIR  = 当前文件所在的文件夹
                # $name     = 引用在 VAR 中预设的变量
                
        # 开启输出显示的功能
        DEBUG : refresh
        
        # 需要检测的文件, 除普通的通配符外, 使用正则表达式用 [( ... )] 标注
        WATCH : "*.js"
        
        # 设置超时 5s
        TIMEOUT : 5000
```

## 截图


![OnSave plugin](https://raw.githubusercontent.com/wl879/screenshots/master/pics/onsaveplugin.png)