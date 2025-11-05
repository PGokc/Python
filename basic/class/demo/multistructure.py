# --------------------------------- 1.给 init 加默认参数（最简单，推荐）---------------------------------
class CSGOPlayer:
    # win_rate 设为默认值 None，支持两种实例化方式
    def __init__(self, nickname, rank, win_rate=None):
        self.nickname = nickname
        self.rank = rank
        # 可选参数的逻辑处理
        if win_rate is not None:
            self.win_rate = win_rate
        else:
            self.win_rate = 50.0  # 默认胜率

# 方式 1：只传必填参数（nickname + rank）
player1 = CSGOPlayer("小帅", "全球精英")
print(player1.win_rate)  # 输出：50.0（使用默认值）

# 方式 2：传所有参数（nickname + rank + win_rate）
player2 = CSGOPlayer("小美", "大师级守卫", 62.3)
print(player2.win_rate)  # 输出：62.3（使用传入值）

# --------------------------------- 2.用关键字参数（**kwargs）支持灵活传参 ---------------------------------
class CSGOPlayer:
    def __init__(self, **kwargs):
        # 必选参数（如果没传则报错）
        self.nickname = kwargs["nickname"]
        self.rank = kwargs["rank"]
        # 可选参数（有则用，无则默认）
        self.win_rate = kwargs.get("win_rate", 50.0)
        self.team = kwargs.get("team", "无战队")

# 方式 1：只传必填参数
player1 = CSGOPlayer(nickname="小帅", rank="全球精英")
print(player1.team)  # 输出：无战队

# 方式 2：传必填+部分可选参数
player2 = CSGOPlayer(nickname="小美", rank="大师级守卫", win_rate=62.3)
print(player2.win_rate)  # 输出：62.3

# 方式 3：传所有参数
player3 = CSGOPlayer(nickname="s1mple", rank="全球精英", win_rate=89.5, team="NA'VI")
print(player3.team)  # 输出：NA'VI

# --------------------------------- 3. 用类方法（@classmethod）定义「备选构造函数」（最灵活） ---------------------------------
class CSGOPlayer:
    # 核心构造函数（处理所有属性的初始化）
    def __init__(self, nickname, rank, win_rate, team):
        self.nickname = nickname
        self.rank = rank
        self.win_rate = win_rate
        self.team = team

    # 备选构造函数 1：普通玩家（无战队，默认胜率 50.0）
    @classmethod
    def normal_player(cls, nickname, rank):
        return cls(nickname=nickname, rank=rank, win_rate=50.0, team="无战队")

    # 备选构造函数 2：职业玩家（有战队，需传胜率）
    @classmethod
    def pro_player(cls, nickname, rank, team, win_rate):
        return cls(nickname=nickname, rank=rank, win_rate=win_rate, team=team)

    # 备选构造函数 3：新手玩家（固定段位+胜率，只需传昵称）
    @classmethod
    def new_player(cls, nickname):
        return cls(nickname=nickname, rank="新手", win_rate=40.0, team="无战队")


# 方式 1：创建普通玩家
player1 = CSGOPlayer.normal_player("小帅", "全球精英")
print(player1.team, player1.win_rate)  # 输出：无战队 50.0

# 方式 2：创建职业玩家
player2 = CSGOPlayer.pro_player("s1mple", "全球精英", "NA'VI", 89.5)
print(player2.team, player2.win_rate)  # 输出：NA'VI 89.5

# 方式 3：创建新手玩家
player3 = CSGOPlayer.new_player("小白")
print(player3.rank, player3.win_rate)  # 输出：新手 40.0