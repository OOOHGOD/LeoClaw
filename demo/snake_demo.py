"""
贪吃蛇 - 终端自动演示版
使用简单的路径规划AI自动游玩并展示
"""
import random
import time
import os
import sys
import math

# ============ 游戏核心 ============
class SnakeGame:
    def __init__(self, width=30, height=18):
        self.W = width
        self.H = height
        # 蛇初始位置（居中，向右）
        mid_x, mid_y = width // 2, height // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = (1, 0)  # 向右
        self.food = None
        self.score = 0
        self.dead = False
        self.place_food()

    def place_food(self):
        occupied = set(self.snake)
        candidates = [(x, y) for x in range(self.W) for y in range(self.H)
                      if (x, y) not in occupied]
        self.food = random.choice(candidates) if candidates else None

    def step(self, direction):
        """执行一步。返回 (alive, ate_food)"""
        if self.dead:
            return False, False

        self.direction = direction
        head = self.snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])

        # 碰墙
        if not (0 <= new_head[0] < self.W and 0 <= new_head[1] < self.H):
            self.dead = True
            return False, False

        # 碰自己（排除尾巴，因为尾巴马上要缩掉）
        if new_head in self.snake[:-1]:
            self.dead = True
            return False, False

        self.snake.insert(0, new_head)

        ate = False
        if new_head == self.food:
            self.score += 10
            ate = True
            self.place_food()
            if self.food is None:
                # 胜利！蛇填满整个棋盘
                self.dead = True
                return False, True
        else:
            self.snake.pop()

        return True, ate

    def clone(self):
        g = SnakeGame.__new__(SnakeGame)
        g.W, g.H = self.W, self.H
        g.snake = list(self.snake)
        g.direction = self.direction
        g.food = self.food
        g.score = self.score
        g.dead = self.dead
        return g


# ============ AI 路径规划 ============
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # 上右下左
DIR_SYMBOLS = {(0, -1): '↑', (1, 0): '→', (0, 1): '↓', (-1, 0): '←'}


def opposite(d):
    return (-d[0], -d[1])


def bfs(start, goal, snake, width, height, direction):
    """BFS从start到goal，避开蛇身（但把蛇尾视为可走，因为会缩掉）"""
    # 蛇尾在一步后会消失
    obstacle = set(snake[:-1]) if len(snake) > 1 else set()

    queue = [(start, [])]
    visited = {start}

    while queue:
        pos, path = queue.pop(0)
        if pos == goal:
            return path

        for d in DIRS:
            # 不允许直接掉头
            if path:
                prev_d = path[-1] if path else direction
                if d == opposite(prev_d):
                    continue
            elif d == opposite(direction):
                continue

            np = (pos[0] + d[0], pos[1] + d[1])
            if np in visited:
                continue
            if not (0 <= np[0] < width and 0 <= np[1] < height):
                continue
            if np in obstacle:
                continue

            visited.add(np)
            queue.append((np, path + [d]))

    return None  # 无路可走


def safest_direction(game):
    """选择最安全的方向：优先吃食物，否则走最开阔的方向"""
    head = game.snake[0]
    d = game.direction

    # 尝试BFS找食物
    path = bfs(head, game.food, game.snake, game.W, game.H, d)
    if path:
        return path[0]  # 走BFS路径的第一步

    # 无法到达食物，选择最安全的方向（不撞墙、不撞自己）
    safe_dirs = []
    for nd in DIRS:
        if nd == opposite(d):
            continue
        nh = (head[0] + nd[0], head[1] + nd[1])
        if not (0 <= nh[0] < game.W and 0 <= nh[1] < game.H):
            continue
        if nh in game.snake[:-1]:
            continue
        # 评估该方向的"开阔度"
        flood_count = flood_fill(nh, game.snake, game.W, game.H)
        safe_dirs.append((nd, flood_count))

    if safe_dirs:
        # 选最开阔的
        safe_dirs.sort(key=lambda x: -x[1])
        return safe_dirs[0][0]

    # 没安全方向，只能往前
    nh = (head[0] + d[0], head[1] + d[1])
    if (0 <= nh[0] < game.W and 0 <= nh[1] < game.H and nh not in game.snake[:-1]):
        return d
    # 全部方向都不行，随便选一个不撞自己的
    for nd in DIRS:
        nh = (head[0] + nd[0], head[1] + nd[1])
        if 0 <= nh[0] < game.W and 0 <= nh[1] < game.H and nh not in game.snake[:-1]:
            return nd
    return d  # 必死


def flood_fill(start, snake, width, height):
    """计算从start可达的空格数量"""
    obstacle = set(snake)
    visited = set()
    stack = [start]
    while stack:
        p = stack.pop()
        if p in visited or p in obstacle:
            continue
        if not (0 <= p[0] < width and 0 <= p[1] < height):
            continue
        visited.add(p)
        for d in DIRS:
            stack.append((p[0] + d[0], p[1] + d[1]))
    return len(visited)


# ============ 终端渲染 ============
def render(game, step_count, gen):
    """渲染游戏状态到终端"""
    os.system('cls' if os.name == 'nt' else 'clear')

    # 构建网格
    grid = [[' ' for _ in range(game.W)] for _ in range(game.H)]

    # 画食物
    if game.food:
        fx, fy = game.food
        grid[fy][fx] = '🍎'

    # 画蛇
    for i, (sx, sy) in enumerate(game.snake):
        if i == 0:
            grid[sy][sx] = DIR_SYMBOLS.get(game.direction, '●')
        else:
            grid[sy][sx] = '●'

    # 边框
    top_border = '╔' + '══' * game.W + '╗'
    bottom_border = '╚' + '══' * game.W + '╝'

    print(f"   🐍 贪吃蛇 AI 演示  |  分数: {game.score}  |  步数: {step_count}  |  长度: {len(game.snake)}")
    print(top_border)
    for y, row in enumerate(grid):
        print('║' + ''.join(f'{c} ' if c != '🍎' else c for c in row) + '║')
    print(bottom_border)

    if game.dead:
        if game.food is None:
            print(f"\n   🎉 恭喜！蛇填满了整个棋盘！最终得分: {game.score}")
        else:
            print(f"\n   💀 游戏结束！蛇撞到了障碍物。最终得分: {game.score}")
    else:
        print(f"\n   🤖 AI 自动操控中... (第 {gen + 1} 次尝试)")


def main():
    game = SnakeGame(width=26, height=16)
    step_count = 0
    generation = 0
    max_steps_no_food = 200  # 如果200步没吃到食物就重来
    steps_since_food = 0
    total_scores = []

    print("=" * 60)
    print("          🐍 贪吃蛇 - AI 自动演示 🐍")
    print("=" * 60)
    print()
    print("   AI 使用 BFS 寻路算法自动寻找食物")
    print("   如果无路可走则选择最安全的方向")
    print("   按 Ctrl+C 退出")
    print()
    time.sleep(2)

    try:
        while generation < 20:  # 最多20轮
            if game.dead:
                total_scores.append(game.score)
                generation += 1
                if generation >= 15:
                    break
                game = SnakeGame(width=26, height=16)
                step_count = 0
                steps_since_food = 0
                time.sleep(0.8)

            # AI选择方向
            direction = safest_direction(game)

            prev_score = game.score
            alive, ate = game.step(direction)
            step_count += 1

            if ate:
                steps_since_food = 0
            else:
                steps_since_food += 1

            # 如果太久没吃到食物，认为AI卡住了
            if steps_since_food > max_steps_no_food:
                game.dead = True
                game.score = max(0, game.score - 5)

            render(game, step_count, generation)

            # 动态速度：蛇越长越快
            base_delay = 0.08
            speed = max(0.02, base_delay - len(game.snake) * 0.001)
            time.sleep(speed)

    except KeyboardInterrupt:
        print("\n\n   用户中断。")

    # 总结
    print("\n" + "=" * 60)
    if total_scores:
        print(f"   游戏结束！共运行 {len(total_scores)} 轮")
        print(f"   最高分: {max(total_scores)}")
        print(f"   平均分: {sum(total_scores)//len(total_scores)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
