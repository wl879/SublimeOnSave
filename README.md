# OnSave plugin for Sublime Text 3

Which executes given commands on file save. output results can be displayed in an edit view



在你保存文件时，预设一些执行指令，如 Coffeescript、Teajs、Css、Jade 的预编译。

特点:
    OnSave plugin 可将输出内容显示到 Sublime Text 的编辑窗口中，更优雅的调试你的代码。


## 安装 Install

Execute **"Package Control: Install Package"** in the Command Pallette to retrieve a list of available packages. Search in the list and install package `On Save`.



现在已经成功上传到 Sublime Text Package Control, 可以在 Install package 里搜索 `On Save`


### Git installation

```
    Clone the repository in your Sublime Text "Packages" directory:
    
        git clone https://github.com/wl879/SublimeOnSave.git OnSave
        
    
    The "Packages" directory is located at:
    
    * OS X:
    
            ~/Library/Application Support/Sublime Text 3/Packages/
    
```



## 使用 Usage



Create a ".onsave" file in you project dir.  The contents as follows



### 配置文件


* 新建在你的项目目录下 ".onsave" 文件，使用 yaml 语法配置
* 也可以在项目文件夹上 [右键] > [On Save] 创建，模板如下：


```yaml

# 预设变量
VAR:
    #name: --test

# 全局设置

# 预设环境变量
ENV:
    #path: /usr/bin

# 开启输出显示的功能
OUT : right
# false 不显示
# 定义一个输出窗口的 name，输出到一个标准文本编辑窗口中
# name left 在左边打开一个输出窗口
# name right 在右边打开一个输出窗口
# name bottom 在下边打开一个输出窗口
            
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
        OUT : right
        
        # 需要检测的文件, 除普通的通配符外, 使用正则表达式用 [( ... )] 标注
        WATCH : "*.js"
   
        # 设置超时 5s
        TIMEOUT : 5000
```



## 截图 Screenshots


![OnSave plugin](https://raw.githubusercontent.com/wl879/screenshots/master/pics/onsaveplugin.png)

![OnSave plugin](https://raw.githubusercontent.com/wl879/screenshots/master/pics/onsaveplugin.gif)