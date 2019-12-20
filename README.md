# 程序设计思想与方法 (Python) 大作业 /  CS902(Python) Final Project

### 概览 Overview

<img src="./imgs/overview.png" alt="Overview" style="zoom:50%;" />

**BugenPyQ SQL Client** 是一个基于 PyQt 的简易图形化 SQL 数据库前端, 允许连接多种文件或远程数据库, 支持数据表可视化编辑和 SQL 语句查询.

**BugenPyQ SQL Client** is a simple SQL client with GUI based on PyQt. It allows users to connect several kinds of SQL database and supports visual editing and SQL statement queries.

### 功能介绍 Introductions

#### 快速预览数据库中的全部表格, 进行可视化编辑 / Preview all tables in the database and perform visual editing

<img src="./imgs/edit.png" alt="edit" style="zoom:50%;" />

使用 **BugenPyQ SQL Client** 打开数据库后, 可利用左侧 Table 列表选取活动的数据表, 并直接在右侧预览窗口内修改表格. 修改完成后, 使用 **Submit** 提交对数据库的更改.

After open a database in **BugenPyQ SQL Client**, you can select the active table through the tables list and edit data in it directly at the preview window. Use **Submit** to submit the modification.

#### 支持打开本地 SQLite 文件、连接远程 PostgreSQL 和 MySQL 数据库 / Supports opening local SQLite file, remote PostgreSQL and MySQL database as well

<img src="./imgs/postgresql.png" alt="postgresql" style="zoom:50%;" />

**BugenPyQ SQL Client** 不仅可以打开本地的 SQLite 文件, 还可以连接远程 PostgreSQL 和 MySQL 数据库 (不同平台下可能需编译相应 Driver), 直接对远程数据库进行更删改查.

**BugenPyQ SQL Client** can not only open an SQLite file locally, but also support connecting to remote PostgreSQL or MySQL database (driver compilation is probably needed under different OS).

#### 多标签、多线程 SQL 请求, 可同时进行多个查询操作 / Multi-tabbed and multi-threaded SQL queries, executing several SQL operations simultaneously

<img src="./imgs/query.png" alt="query" style="zoom:50%;" />

在 **BugenPyQ SQL Client** 的第二个标签内可以进行 SQL 语句查询. **BugenPyQ SQL Client** 支持多标签, 可以使用快捷键 **⌘T / Ctrl+T** 或在 **文件** 菜单内新建查询标签. 此外, 查询系统支持多线程处理, 在处理繁忙查询时不影响应用其他功能的使用.

Users can perform SQL queries at the second tab of **BugenPyQ SQL Client **. **BugenPyQ SQL Client** is multi-tabbed. To add a query tab, please press **⌘T / Ctrl+T** or simply via **File** menu. Also, the query system supports multi-threading technology that no other operations will be interfered even when you are dealing with a busy query.

#### 将查询结果导出为 CSV 文件 / Export the results to a CSV file

<img src="./imgs/export.png" alt="export" style="zoom:50%;" />

在 **BugenPyQ SQL Client** 中进行查询时, 不仅可以利用 `SELECT INTO` 等语句保留查询结果, 还可将查询结果一键导出成标准 CSV (逗号分隔的值) 文件, 以便作进一步数据分析.

While querying in **BugenPyQ SQL Client**, you can not only save the results with statements like  `SELECT INTO` , but also export the query results to a CSV (comma-separated values) file for further data analysis.



### 构建和运行 Build and Run

1. 确保 Python 版本高于 3.7.

2. 安装 `PyQt5` 模块: `python3 -m pip install PyQt5 --user` .

3. 运行: `python3 ./main.py`.




1. Make sure the Python version is higher than 3.7. 
2. Install latest `PyQt5` module: `python3 -m pip install PyQt5 --user` . 
3. Run `python3 ./main.py`.

### 程序设计 Designing

```bash
.
├── connectionDialog.py # 连接对话框类
├── database.py # 数据库管理器类
├── databaseView.py # 表格预览类
├── example.py # 保存‘新建’数据库内容
├── exporter.py # 导出器类
├── main.py # 主窗口类
├── queriesContainer.py # 请求标签页容器类
├── queryView.py # 请求标签页类
└── sqlites # 示例 SQLite 数据库
    ├── product.sqlite
    ├── students.sqlite
    └── test.sqlite
```

**设计亮点:**

1. 各部件在单独的模块 (.py) 中实现, 与主窗口松耦合, 代码逻辑更清晰、复用性强、动态编译提升运行效率.

2. 使用独立的数据库管理器类 (database.py) 维护连接, 使 UI 代码与操作逻辑分离.

3. 利用多线程和 PyQt 的信号槽技术, 避免在 UI 线程中进行耗时操作, 保证程序 GUI 流畅性和稳定性.

4. 操作逻辑易于上手, 注重细节考量. 如: 

   - 全面采用 Layout 设计, 可任意缩放窗口

   - 允许用户多次建立和断开连接, 复用程序功能
   - 适时调整按钮和动作的可用状态,  程序鲁棒性强
   - 新建/打开/关闭/退出时均提示用户保存当前更改, 避免用户进行误操作,

   - 全程通过状态栏和标题栏指示当前连接信息和操作状态

   - 全平台下支持快捷键操作, 符合用户惯有操作逻辑



**Design highlights:**

1. All of the widgets are implemented in a separate module (.py), which is loosely coupled with the main window, resulting in clearer code logic, strong reusability and dynamic compilation with performance improvement.
2. Maintaining connections with a separate database manager class (database.py), separating the UI code from the logic code.
3. Make use of multi-threading and PyQt signal-slot technology to avoid time-consuming operation in the main UI thread and ensure the program GUI fluency and stability.
4. Easy operation logic and attention to details, such as:
   - Adopt Layout comprehensively, scaling the window arbitrarily is allowed.
	- Allows users to connect and disconnect multiple times and reuse program functions.
	- Adjust the enabled state of buttons and actions bringing to strong program robustness.
	- When new/open/close/exit, the user will be prompted to save the current changes to avoid misoperations.
	- Indicates current connection information and operation status through the status bar and title bar.
	- Keyboard shortcuts are supported on any platforms, which is in line with the user's usual operation logic.

### 视频演示 Video Demo

请见 `demos` 文件夹下的内容.

Please see the contents of the `demos` folder.

### 致谢 Acknowledgement

**感谢陆教授和助教老师的悉心教导!**

**Thanks to Professor Lu and the TAs for their guidance!**