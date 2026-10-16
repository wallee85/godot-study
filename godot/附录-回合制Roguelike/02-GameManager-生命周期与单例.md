# 02 · GameManager：Autoload、信号与生命周期

---

## 1. GameManager 到底管什么

**它不管**地图生成（`BoardManager`），也不管玩家怎么走（`Player`）。

---

## 2. 核心概念①：Autoload —— 引擎自带的"跨场景单例"

```csharp
if (instance == null) instance = this;
InitGame();      // ← "第一次那个 sceneLoaded 我们错过了"，所以手动补一次
```

### 2.2 Godot 的答案：Autoload

`项目 → 项目设置 → 自动加载`：

| 路径 | 节点名 |
|---|---|
| `res://scripts/game_manager.gd`（或 `.cs`） | `GameManager` |

点「添加」，然后**在场景树顶部的「自动加载」分组里能看到它**。

Autoload 的含义是：**在游戏启动时把这个节点挂到根节点下，它是整个游戏最外层节点，永远不随场景切换而销毁**。

于是三件事一次性解决：

```gdscript
# 任何脚本、任何场景里，直接这样写：
GameManager.player_food_points -= 10
print(GameManager.level)
```

```csharp
// C#：Autoload 也是节点，但因为 C# 没有"全局变量"，通常再包一层静态属性
GameManager.Instance.PlayerFoodPoints -= 10;
```

C# 侧的惯用写法（**少了这一层，你就得满项目写 `GetNode<GameManager>("/root/GameManager")`**）：

```csharp
// C# —— scripts/GameManager.cs
public partial class GameManager : Node
{
    // 只为少写 GetNode 而存在的一个静态引用
    public static GameManager Instance { get; private set; }

    public override void _Ready()
    {
        Instance = this;
        SetProcess(false);
    }
}
```

> ⚠️ **C# 必须用手动静态属性**，因为 C# 里没有"用节点名当全局变量"这种事。这是 C# 路线在 Godot 里少数几个**不如 GDScript 方便**的地方之一。

### 2.3 Autoload 的顺序**是有意义的**

项目设置里 Autoload 列表**从上到下依次 `_ready`**。所以：

- 后面的 Autoload 在 `_ready` 时可以访问前面的；
- 前面的**不能**在 `_ready` 里访问后面的。

本项目 [05 章](./05-动画与音效.md) 会加第二个 Autoload `Sfx`（音效池）。因为 `GameManager` 和 `Player` 都要用音效，所以**列表顺序必须是 `Sfx` 在上面、`GameManager` 在下面**。

---

```csharp
```

原文自己标注了"更好的做法是挂个 `UIManager`"。**Godot 的信号就是那个"更好的做法"，而且是语言内建的。**

### 3.2 Godot 的写法

**广播方（GameManager）只管说"发生了什么事"**：

```gdscript
signal level_started(level: int)
signal food_changed(food: int, delta_text: String)
signal game_over_reached(level: int)

func begin_level() -> void:
    level_started.emit(level)         # 广播
```

**接收方（UI）自己订阅**：

```gdscript
# level_ui.gd
func _ready() -> void:
    GameManager.level_started.connect(_on_level_started)
    GameManager.food_changed.connect(_on_food_changed)

func _on_level_started(level: int) -> void:
    $LevelLabel.text = "Day %d" % level
```

```csharp
// C# —— 广播方：先声明信号
[Signal] public delegate void LevelStartedEventHandler(int level);
[Signal] public delegate void FoodChangedEventHandler(int food, string deltaText);
[Signal] public delegate void GameOverReachedEventHandler(int level);

public void BeginLevel() => EmitSignal(SignalName.LevelStarted, Level);

// C# —— 接收方
public override void _Ready()
{
    GameManager.Instance.LevelStarted += OnLevelStarted;
    GameManager.Instance.FoodChanged += OnFoodChanged;
}
```

---

## 4. 核心概念③：`_ready` 是"子先父后"——它消灭了一整类初始化顺序 bug

**这是本章最重要的一条。**

回顾 [00 章 §3](./00-核心概念地图.md#3-节点树与生命周期godot-什么时候调你的代码)：Godot 的 `_ready()` 是**自底向上**调用的——**子节点全部就绪后，父节点的 `_ready()` 才跑**。

为什么这条能救命？看本项目的结构：

```
Main                         ← level.gd（父）
├─ Camera2D
├─ Board                     ← board_manager.gd
└─ LevelUi                   ← level_ui.gd（子，先 _ready）
```

- `LevelUi._ready()` （子）**先**跑 → 在信号上订阅好
- `Main._ready()` （父）**后**跑 → 调 `GameManager.begin_level()` → 广播 → **一定有人接着**

**顺序是引擎保证的，不需要任何补丁。**

> **Godot 用"确定的顺序 + 信号"把这件事变成了不可能出错。**

---

## 5. 核心概念④：回合制的锁 —— "同步执行到第一个 `await`"

调用异步函数时，`await` 之前的语句会同步执行：

```gdscript
func _process(_delta: float) -> void:
    if players_turn or enemies_moving or doing_setup or game_ended:
        return
    _run_enemy_turn()    # 调用的瞬间，函数体同步跑到第一个 await 才交还控制权

func _run_enemy_turn() -> void:
    enemies_moving = true                              # ← 这个赋值在"调用它的那一帧"就生效
    await get_tree().create_timer(TURN_DELAY).timeout   # ← 到这才交还控制权
```

因为 `enemies_moving = true` 在**当帧**就生效，下一帧 `_process` 的条件不成立 → **不会重复启动**。这就是"用状态位给轮询加锁"的 Godot 版本。

> **一句话总结**：`await` 不是"另开一条执行流"，而是"**我先把话说清楚（改状态），然后让出去等**"。理解这一点，整个回合制代码就通了。

---

## 6. 写代码

### 6.1 先建一个占位 BoardManager（让工程能跑）

`GameManager` 会引用 `BoardManager`，但它在 [03 章](./03-BoardManager-棋盘生成.md) 才真正实现。先放占位版：

```gdscript
# scripts/board_manager.gd（占位，03 章整体替换）
extends Node2D

func setup_scene(level: int) -> void:
	print("[Board] setup_scene(level=%d) —— 棋盘生成尚未实现" % level)
```

```csharp
// scripts/BoardManager.cs（占位）
public partial class BoardManager : Node2D
{
    public void SetupScene(int level) => GD.Print($"[Board] setup_scene(level={level}) —— 棋盘生成尚未实现");
}
```

### 6.2 `scripts/game_manager.gd`

```gdscript
# GDScript —— scripts/game_manager.gd
# 注册为 Autoload，节点名 GameManager
extends Node
## 跨关卡的持久状态 + 回合制裁判。

# ---------- 信号：GameManager 只管"广播发生了什么事" ----------
signal level_started(level: int)
signal food_changed(food: int, delta_text: String)
signal game_over_reached(level: int)

# ---------- 常量 ----------
const LEVEL_START_DELAY := 2.0   # 开场黑幕停留时间
const TURN_DELAY := 0.1          # 敌人逐个行动的间隔

# ---------- 持久状态（Autoload 天然跨场景） ----------
var level := 1
var player_food_points := 100    # 玩家初始 Food，同时也是"血条"

# ---------- 回合状态 ----------
var players_turn := true
var enemies_moving := false
var doing_setup := true          # 开场演出 / 过关转场期间：禁止操作
var game_ended := false

var _enemies: Array[Enemy] = []  # 本关所有敌人（场景重载后会重建）

func _ready() -> void:
	# Autoload 的 _process 会一直跑，但没进关卡时不该跑
	set_process(false)

# ---------------------------------------------------------------
#  敌人登记（Enemy 在自己的 _ready 里调用）
# ---------------------------------------------------------------
func register_enemy(enemy: Enemy) -> void:
	_enemies.append(enemy)

# ---------------------------------------------------------------
#  关卡流程
# ---------------------------------------------------------------
func begin_level() -> void:
	_enemies.clear()
	players_turn = true
	enemies_moving = false
	doing_setup = true
	game_ended = false
	set_process(true)
	level_started.emit(level)    # → LevelUi 显示黑幕

## 由 UI 在黑幕消失时调用：现在可以操作了
func finish_setup() -> void:
	doing_setup = false

## 玩家走到出口：关卡 +1，然后重载场景
func advance_level() -> void:
	doing_setup = true           # 先冻结回合，别让敌人在转场里继续动
	level += 1
	get_tree().reload_current_scene()

func end_game() -> void:
	game_ended = true
	doing_setup = true
	set_process(false)
	game_over_reached.emit(level)

func spend_food(amount: int, delta_text := "") -> void:
	player_food_points = amount
	food_changed.emit(player_food_points, delta_text)

# ---------------------------------------------------------------
#  回合裁判
# ---------------------------------------------------------------
func _process(_delta: float) -> void:
	if players_turn or enemies_moving or doing_setup or game_ended:
		return
	_run_enemy_turn()

func _run_enemy_turn() -> void:
	enemies_moving = true                                     # ← 同步生效，给 _process 上锁
	await get_tree().create_timer(TURN_DELAY).timeout

	if _enemies.is_empty():
		await get_tree().create_timer(TURN_DELAY).timeout      # 没敌人也让玩家等等，节奏更稳

	for enemy in _enemies:
		if not is_instance_valid(enemy):
			continue
		await get_tree().physics_frame                        # 射线查询必须在物理帧里
		enemy.move_enemy()
		await get_tree().create_timer(enemy.move_time).timeout

	enemies_moving = false
	players_turn = true
```

C# 版：

```csharp
// C# —— scripts/GameManager.cs
using System.Collections.Generic;
using Godot;

public partial class GameManager : Node
{
    [Signal] public delegate void LevelStartedEventHandler(int level);
    [Signal] public delegate void FoodChangedEventHandler(int food, string deltaText);
    [Signal] public delegate void GameOverReachedEventHandler(int level);

    public const double LevelStartDelay = 2.0;
    public const double TurnDelay = 0.1;

    public static GameManager Instance { get; private set; }

    public int Level { get; set; } = 1;
    public int PlayerFoodPoints { get; set; } = 100;

    public bool PlayersTurn { get; set; } = true;
    public bool EnemiesMoving { get; set; }
    public bool DoingSetup { get; set; } = true;
    public bool GameEnded { get; set; }

    private readonly List<Enemy> _enemies = new();

    public override void _Ready()
    {
        Instance = this;
        SetProcess(false);
    }

    public void RegisterEnemy(Enemy enemy) => _enemies.Add(enemy);

    public void BeginLevel()
    {
        _enemies.Clear();
        PlayersTurn = true;
        EnemiesMoving = false;
        DoingSetup = true;
        GameEnded = false;
        SetProcess(true);
        EmitSignal(SignalName.LevelStarted, Level);
    }

    public void FinishSetup() => DoingSetup = false;

    public void AdvanceLevel()
    {
        DoingSetup = true;
        Level += 1;
        GetTree().ReloadCurrentScene();
    }

    public void EndGame()
    {
        GameEnded = true;
        DoingSetup = true;
        SetProcess(false);
        EmitSignal(SignalName.GameOverReached, Level);
    }

    public void SpendFood(int amount, string deltaText = "")
    {
        PlayerFoodPoints = amount;
        EmitSignal(SignalName.FoodChanged, PlayerFoodPoints, deltaText);
    }

    public override void _Process(double delta)
    {
        if (PlayersTurn || EnemiesMoving || DoingSetup || GameEnded)
            return;
        RunEnemyTurn();
    }

    private async void RunEnemyTurn()
    {
        EnemiesMoving = true;   // ← 同步生效，给 _Process 上锁

        await ToSignal(GetTree().CreateTimer(TurnDelay), SceneTreeTimer.SignalName.Timeout);

        if (_enemies.Count == 0)
            await ToSignal(GetTree().CreateTimer(TurnDelay), SceneTreeTimer.SignalName.Timeout);

        foreach (var enemy in _enemies)
        {
            if (!GodotObject.IsInstanceValid(enemy))
                continue;
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
            enemy.MoveEnemy();
            await ToSignal(GetTree().CreateTimer(enemy.MoveTime), SceneTreeTimer.SignalName.Timeout);
        }

        EnemiesMoving = false;
        PlayersTurn = true;
    }
}
```

| 点 | 说明 |
|---|---|
| `set_process(false)` | Autoload 存活于**整个游戏生命周期**，但只在关卡里才需要跑回合裁判。这就是 Godot 的"禁用"——不是 `enabled`，是关掉某一路 process |
| `_enemies: Array[Enemy]` | 类型化数组（GDScript 4 的特性），这样 `enemy.move_enemy()` 有代码补全。**注意：GDScript 没有泛型，但有"类型化数组"**，这已经够用了 |
| `is_instance_valid(enemy)` | 被 `queue_free()` 的节点变量**不是 `null`**，必须用这个函数（[附录总览 §6.6](./README-原Roguelike主线.md#66-null-与已销毁对象)） |
| `await get_tree().physics_frame` | 敌人移动前要查物理空间，而**空间查询只能在物理帧里做**（[00 章 §8](./00-核心概念地图.md#8-物理查询使用-intersect_ray)） |
| `spend_food()` | 把"改数值 + 广播"封在一起，避免有人改了值忘了广播 |

### 6.3 `scripts/level.gd`（挂在 `main.tscn` 根节点）

```gdscript
# GDScript —— scripts/level.gd
extends Node2D
## 一个关卡 = 一个 main.tscn。每次重载场景都会重新跑 _ready()。

@onready var board: BoardManager = $Board

func _ready() -> void:
	GameManager.begin_level()                    # ① 广播"新关卡开始" → UI 显示黑幕
	board.setup_scene(GameManager.level)         # ② 铺地图、放玩家和敌人
```

```csharp
// C# —— scripts/Level.cs
using Godot;

public partial class Level : Node2D
{
    private BoardManager _board;

    public override void _Ready()
    {
        _board = GetNode<BoardManager>("Board");
        GameManager.Instance.BeginLevel();
        _board.SetupScene(GameManager.Instance.Level);
    }
}
```

> 因为 `reload_current_scene()` 会**重新跑新场景的 `_ready()`**，所以"一关开始时该干什么"永远发生在一个确定的地方，不需要任何事件订阅，也不需要"第一次要手动补一次"的补丁。

### 6.4 `scripts/level_ui.gd`（挂在 `LevelUi` 上）

```gdscript
# GDScript —— scripts/level_ui.gd
extends CanvasLayer
## 只负责显示。它不知道游戏逻辑，只订阅信号。

@onready var black_overlay: ColorRect = $BlackOverlay
@onready var level_label: Label = $LevelLabel
@onready var food_label: Label = $FoodLabel

func _ready() -> void:
	# 子节点先 _ready（所以这里订阅是安全的，父节点的 begin_level 还没发出）
	GameManager.level_started.connect(_on_level_started)
	GameManager.food_changed.connect(_on_food_changed)
	GameManager.game_over_reached.connect(_on_game_over)

func _on_level_started(level: int) -> void:
	level_label.text = "Day %d" % level
	food_label.text = "Food: %d" % GameManager.player_food_points
	black_overlay.visible = true

	await get_tree().create_timer(GameManager.LEVEL_START_DELAY).timeout
	black_overlay.visible = false
	GameManager.finish_setup()          # 放开操作

func _on_food_changed(food: int, delta_text: String) -> void:
	food_label.text = "%sFood: %d" % [delta_text, food]

func _on_game_over(level: int) -> void:
	level_label.text = "After %d days, you starved." % level
	black_overlay.visible = true
```

```csharp
// C# —— scripts/LevelUi.cs
using Godot;

public partial class LevelUi : CanvasLayer
{
    private ColorRect _blackOverlay;
    private Label _levelLabel;
    private Label _foodLabel;

    public override void _Ready()
    {
        _blackOverlay = GetNode<ColorRect>("BlackOverlay");
        _levelLabel = GetNode<Label>("LevelLabel");
        _foodLabel = GetNode<Label>("FoodLabel");

        var gm = GameManager.Instance;
        gm.LevelStarted += OnLevelStarted;
        gm.FoodChanged += OnFoodChanged;
        gm.GameOverReached += OnGameOver;
    }

    private async void OnLevelStarted(int level)
    {
        _levelLabel.Text = $"Day {level}";
        _foodLabel.Text = $"Food: {GameManager.Instance.PlayerFoodPoints}";
        _blackOverlay.Visible = true;

        await ToSignal(GetTree().CreateTimer(GameManager.LevelStartDelay), SceneTreeTimer.SignalName.Timeout);
        _blackOverlay.Visible = false;
        GameManager.Instance.FinishSetup();
    }

    private void OnFoodChanged(int food, string deltaText) => _foodLabel.Text = $"{deltaText}Food: {food}";

    private void OnGameOver(int level)
    {
        _levelLabel.Text = $"After {level} days, you starved.";
        _blackOverlay.Visible = true;
    }
}
```

> ⚠️ **C# 里信号用 `+=` 订阅**（它就是普通的 C# event，非常自然）；GDScript 里用 `.connect(方法引用)`。
> ⚠️ C# 的 `_Ready` 里 `_blackOverlay` 等字段要**手动 `GetNode`**，没有 GDScript `@onready` 那种语法糖。

### 6.5 注册 Autoload

`项目 → 项目设置 → 自动加载`：

| 顺序 | 路径 | 节点名 |
|---|---|---|
| 1 | `res://scripts/game_manager.gd`（或 `GameManager.cs`） | `GameManager` |

> [05 章](./05-动画与音效.md) 加 `Sfx` 时要**插在 GameManager 上面**（因为 GameManager 那层的代码会用到 Sfx）。

---

## 7. 运行验证

`F5`（第一次会问主场景，选 `main.tscn`）。应该看到：

1. **黑色遮罩 + `Day 1`**
2. 输出面板打印 `[Board] setup_scene(level=1) —— 棋盘生成尚未实现`
3. **2 秒后黑幕消失**，能看到左下角 `Food: 100`
4. 再按 `F8` 停止

**没报错就说明：Autoload、信号连接、`await` 计时、`_ready` 顺序、UI 引用全部打通了。** 这就是本章的成果。

---

## 8. 顺手验证生命周期顺序

在 `game_manager.gd` 和 `level.gd` 里临时加几行，运行一次对着输出面板看顺序：

```gdscript
# game_manager.gd
func _ready() -> void:
	print("[GM] _ready")
	set_process(false)

func _process(_delta: float) -> void:
	if Engine.get_process_frames() <= 3:
		print("[GM] _process frame ", Engine.get_process_frames())
```

```gdscript
# level.gd
func _ready() -> void:
	print("[Level] _ready  ← 注意它比 LevelUi._ready() 晚")
```

你应该看到（顺序固定）：

```
[GM] _ready                ← Autoload 最先，早于所有场景节点
[LevelUi] _ready           ← 子先
[Level] _ready             ← 父后
[GM] _process frame 1/2/3
```

> **跑完记得删掉**。`print` 放在 `_process` 里是性能杀手（每帧字符串拼接）。

---

## 9. 本章的坑

| 现象 | 原因 |
|---|---|
| `Identifier "GameManager" not declared` | Autoload 没注册，或节点名拼错（**大小写敏感**） |
| `Invalid call. Nonexistent function 'begin_level'` | Autoload 里还留着旧代码，**改完 Autoload 脚本要重启编辑器**（Godot 热重载只覆盖场景里的脚本） |
| UI 不显示 `Day 1` | `LevelUi._ready()` 里的 `connect` 写在 `begin_level()` 之后了。**检查节点树顺序**：`LevelUi` 必须是 `Main` 的子节点 |
| 黑幕不消失 | `create_timer` 的时长写错，或者 `_on_level_started` 里 `await` 后面抛异常了（看输出面板） |
| 敌人回合连跑好几次 | `enemies_moving = true` 被写在了第一个 `await` **之后** |
| `Node not found: "BlackOverlay"` | 子节点名字和 `$BlackOverlay` 不一致（大小写/拼写） |
| 运行两次后关卡变成 2 | 这正是**期望行为**吗？不是的话检查是不是把 `level` 写成了场景里的字段而不是 Autoload 的 |

---

## 10. ✅ 自检清单

- [ ] 能解释 `_ready()` 为什么是"子先父后"，以及它怎么保证了信号订阅一定早于广播
- [ ] 能说出 `set_process(false)` 在这里的作用
- [ ] 能说出 `is_instance_valid()` 为什么比 `== null` 正确
- [ ] `F5` 后能看到：黑幕 + `Day 1` → 2 秒后消失 + `Food: 100`
- [ ] Autoload 列表里 `GameManager` 已注册

下一章：[03 BoardManager：程序化生成棋盘](./03-BoardManager-棋盘生成.md)
