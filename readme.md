## 棋类对战平台

#### 设计思路

+ 采用服务器端和客户端分离的设计：
+ 服务器端：
  + 维护棋盘的状态和所有游戏规则，接受客户端反馈的用户操作，反馈新的棋盘状态
  + 主要分为server、rule、proxy三大模块：
    + server：包含GameServer类，用于管理游戏对局流程
    + rule：包含抽象规则BaseRule及相应的五子棋规则GobangRule、围棋规则GoRule，使用工厂模式进行创建。同时包含备忘录模式的MementoBox类维护历史游戏状态实现悔棋。
    + proxy：代理模式，在ServerProxy中封装了一切跟客户端交互的通信接口。
+ 客户端：
  + 提供GUI界面（pyqt5），上报用户操作到服务器端，并展示当前棋盘状态
  + 与server类似，主要分为client、gui、proxy三大模块：
    + client：包含GameClient类，用于管理游戏对局流程。而由于客户端流程其实很简单，发送开始信号后不断展示服务器端发来的信号即可，因此实际上只充当了proxy和gui直接对接的接口层。
    + gui：使用pyqt实现了所有图形界面，主要包含侧边菜单栏和棋盘两大模块。
    + proxy：代理模式，在ClientProxy中封装了一切跟服务端交互的通信接口。