# MusicEmotionAnalysis
简单readme 操作步骤：
1. 将repo pull 到本地， 建议使用pycharm打开
2. 设立虚拟环境，可使用pyenv virtualenv
3. 用 ‘pip install -r requirements.txt’指令安装所需requirements.txt
4. 当前项目有两个环境，在本地使用时只需用到dev环境（在root/app.py中将ENV设为dev）
5. 你需要在本地设立一个数据库，并把它的路径替换 `app.config['SQLALCHEMY_DATABASE_URI']`后的`YOUR DB`
6. 你可以通过一次性调用helpers文件中的read_musics()方法来传入音乐。项目内提供了两个在线音乐库，Musicdata和Musicdata1分别存于在亚马逊和阿里云，目前只有亚马逊可用。
7. 在完成以上步骤后你可以通过运行local_run文件在本地运行代码。 如果你在`http://127.0.0.1:5000/`看见success！则表示后端运行成功。
