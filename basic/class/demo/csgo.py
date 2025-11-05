# 定义一个类（类名首字母大写，遵循驼峰命名法，如 CSGOPlayer）
class CSGOPlayer:
    # 1. 初始化方法（构造函数）：创建实例时自动执行，用于初始化属性
    def __init__(self, nickname, rank, win_rate):
        # self 代表「当前实例本身」，必须作为第一个参数
        self.nickname = nickname  # 实例属性：昵称
        self.rank = rank  # 实例属性：段位
        self.win_rate = win_rate  # 实例属性：胜率

    # 2. 实例方法：需要 self 参数，操作当前实例的属性
    def shoot(self, target):
        # 方法中通过 self 访问实例属性
        return f"{self.nickname}（{self.rank}）向 {target} 开火！"

    # 3. 实例方法：修改实例属性
    def update_win_rate(self, new_rate):
        self.win_rate = new_rate
        return f"{self.nickname} 的胜率更新为 {self.win_rate}%"


# 4. 类属性：属于类本身，所有实例共享（不在 __init__ 中，直接定义在类里）
CSGOPlayer.game = "Counter-Strike 2"  # 所有 CSGOPlayer 实例的游戏名都是 CS2

# 格式：实例名 = 类名(参数1, 参数2, ...)（参数对应 __init__ 除了 self 之外的参数）
player1 = CSGOPlayer(nickname="小帅", rank="全球精英", win_rate=78.5)
player2 = CSGOPlayer(nickname="小美", rank="大师级守卫", win_rate=62.3)


print(player1.nickname)  # 输出：小帅
print(player2.rank)      # 输出：大师级守卫
print(player1.win_rate)  # 输出：78.5