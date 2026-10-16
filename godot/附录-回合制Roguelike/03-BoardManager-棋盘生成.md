# 03 · BoardManager：程序化生成棋盘

> 本章第一次"运行时造物"。重点：**`@export` 数组 + `instantiate()` + `add_child()`**，以及 Godot 的坐标换算。

---

## 1. 思路：三层，一层一层刷

```
第 1 层：外圈墙 + 地板          ← 铺满 (COLUMNS+2) × (ROWS+2) 的每个格子
第 2 层：随机撒上"墙块"、"食物"
第 3 层：出口（固定在右上角）、玩家（左下角）、敌人（随机）
```

坐标约定（`Grid.TILE = 16` 像素，一个 tile 一个格子）：

```
       x = -1  0   1   2   3   4   5   6   7   8
  y=8   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ← 外圈墙
  y=7   ▓  ·   ·   ·   ·   ·   ·   ·   ⬛  ▓      ← (7,7) 是 Exit
  y=6   ▓  ·   ·   ·   ·   ·   ·   ·   ·   ▓
  ...
  y=1   ▓  ·   ·   ·   ·   ·   ·   ·   ·   ▓
  y=0   ▓  ●   ·   ·   ·   ·   ·   ·   ·   ▓      ← (0,0) 是玩家起点
  y=-1  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

- **可放东西的内部区域**：`x ∈ [1, 6]`，`y ∈ [1, 6]`（36 个位置）
- **(0,0) 给玩家**，**(7,7) 固定放出口** —— 两个都不在"可随机"的范围内
- **外圈墙**：`Grid.is_outer(cell)`

> 这就是最朴素的**程序化生成**：不用手摆，用代码随机撒。

---

```csharp
```

Godot 版：

```gdscript
# GDScript —— Inspector 里拖 .tscn 文件
@export var floor_scenes: Array[PackedScene] = []
@export var wall_scenes: Array[PackedScene] = []
@export var outer_wall_scenes: Array[PackedScene] = []
@export var food_scenes: Array[PackedScene] = []
@export var enemy_scenes: Array[PackedScene] = []
@export var exit_scene: PackedScene
@export var player_scene: PackedScene
```

```csharp
// C#
[Export] public Godot.Collections.Array<PackedScene> FloorScenes { get; set; } = new();
[Export] public Godot.Collections.Array<PackedScene> WallScenes { get; set; } = new();
[Export] public Godot.Collections.Array<PackedScene> OuterWallScenes { get; set; } = new();
[Export] public Godot.Collections.Array<PackedScene> FoodScenes { get; set; } = new();
[Export] public Godot.Collections.Array<PackedScene> EnemyScenes { get; set; } = new();
[Export] public PackedScene ExitScene { get; set; }
[Export] public PackedScene PlayerScene { get; set; }
```

**为什么用数组**：随机挑一个变体，地图才不呆板。

```gdscript
var chosen := floor_scenes.pick_random()      # ← 内置方法，不用自己算下标
```

---

## 3. 核心概念②：`instantiate()` + `add_child()`

```csharp
```

Godot 版：

```gdscript
var tile := scene.instantiate()        # ① 复制一份（此刻它不在任何地方）
tile.position = Grid.to_world(cell)    # ② 摆好位置
add_child(tile)                        # ③ 挂进树（此刻它才开始"活")
```

> **为什么 Godot 这里更不容易错**：`add_child` 之后 `position` 就是**相对新父节点**的坐标。因为我们把它挂到 `Board` 节点下，而 `Board` 在原点、无旋转无缩放，所以 `position` 恰好等于世界坐标，不会出歧义。

### 3.1 别忘了 `add_child`！

```gdscript
# ❌ 什么都不显示
var p := player_scene.instantiate()
p.position = Vector2.ZERO

# ✅ 多加一行才"活"
add_child(p)
```

---

## 4. 核心概念③：随机——Godot 的区间是**闭区间**

```gdscript
randi_range(5, 9)      # 5,6,7,8,9 都可能 —— 闭区间，不用 +1
randf()                # [0, 1)
randf_range(0.0, 1.0)  # [0, 1]
```

```csharp
// C#：用 GD 的静态随机
GD.RandRange(5, 9);              // int 版本，闭区间
GD.RandRange(0.0, 1.0);          // double 版本
GD.Randf();                      // [0, 1)
```

---

## 5. 核心概念④：清理旧棋盘

```csharp
```

**Godot 里这两件事都不需要**：

1. `GameManager` 是 Autoload，**棋盘根本不是它的子节点**（`Board` 是 `Main` 的子节点）→ 不可能被"跨场景保留"。
2. `reload_current_scene()` 会**销毁整个旧场景树**（`Main` 连同 `Board` 和所有子节点一起被 `queue_free`）→ 不存在重叠。

> 如果你以后真的需要**原地重建**棋盘（不重载场景），一行就够：
> ```gdscript
> for child in get_children():
>     child.queue_free()      # 注意是 queue_free（帧末释放），不是 free
> ```

---

## 6. 写代码

把 `scripts/board_manager.gd` 的占位内容**整体替换**成：

```gdscript
# GDScript —— scripts/board_manager.gd
extends Node2D
## 挂在 main.tscn 的 Board 节点上。自己就是"棋盘容器"，
## 生成的所有 tile / 角色都 add_child 到自己下面。

@export_group("棋盘尺寸")
@export var columns := Grid.COLUMNS
@export var rows := Grid.ROWS

@export_group("随机撒物的数量区间（闭区间）")
## x = 最小值，y = 最大值
@export var wall_count := Vector2i(5, 9)
@export var food_count := Vector2i(1, 5)

@export_group("固定物件")
@export var exit_scene: PackedScene
@export var player_scene: PackedScene

@export_group("模板候选池")
@export var floor_scenes: Array[PackedScene] = []
@export var wall_scenes: Array[PackedScene] = []
@export var outer_wall_scenes: Array[PackedScene] = []
@export var food_scenes: Array[PackedScene] = []
@export var enemy_scenes: Array[PackedScene] = []

## 还空着的格子（放一个删一个，保证不重叠）
var _free_cells: Array[Vector2i] = []

# ---------------------------------------------------------------
#  由 level.gd 在每关开始时调用
# ---------------------------------------------------------------
func setup_scene(level: int) -> void:
	_build_floor_and_outer_walls()
	_collect_free_cells()

	_scatter_at_random(wall_scenes, wall_count.x, wall_count.y)
	_scatter_at_random(food_scenes, food_count.x, food_count.y)

	# 敌人数量随关卡以 2 为底对数增长：Lv1→0, Lv2→1, Lv4→2, Lv8→3, Lv16→4
	var enemy_count := int(log(level) / log(2.0))
	_scatter_at_random(enemy_scenes, enemy_count, enemy_count)

	_spawn(exit_scene, Vector2i(columns - 1, rows - 1))   # 出口固定在右上角
	_spawn(player_scene, Vector2i(0, 0))                 # 玩家固定在左下角

# ---------------------------------------------------------------
#  第 1 层：铺地板 + 围一圈外墙
# ---------------------------------------------------------------
func _build_floor_and_outer_walls() -> void:
	for x in range(-1, columns + 1):
		for y in range(-1, rows + 1):
			var cell := Vector2i(x, y)
			var scene: PackedScene
			if Grid.is_outer(cell):
				scene = outer_wall_scenes.pick_random()
			else:
				scene = floor_scenes.pick_random()
			_spawn(scene, cell)

# ---------------------------------------------------------------
#  收集"内部还可放东西"的格子
# ---------------------------------------------------------------
func _collect_free_cells() -> void:
	_free_cells.clear()
	for x in range(1, columns - 1):
		for y in range(1, rows - 1):
			_free_cells.append(Vector2i(x, y))

# ---------------------------------------------------------------
#  随机取一个空格子（取走后从候选里移除）
# ---------------------------------------------------------------
func _take_random_cell() -> Vector2i:
	return _free_cells.pop_at(randi_range(0, _free_cells.size() - 1))

# ---------------------------------------------------------------
#  在随机空格子上撒 count 个候选模板
# ---------------------------------------------------------------
func _scatter_at_random(scenes: Array[PackedScene], minimum: int, maximum: int) -> void:
	var count := randi_range(minimum, maximum)
	for i in count:
		_spawn(scenes.pick_random(), _take_random_cell())

# ---------------------------------------------------------------
#  造一个节点并挂进树
# ---------------------------------------------------------------
func _spawn(scene: PackedScene, cell: Vector2i) -> Node2D:
	var node: Node2D = scene.instantiate()
	node.position = Grid.to_world(cell)      # Board 在原点，所以 position == 世界坐标
	add_child(node)                          # ← 别忘了这一行，否则"造出来了但不存在"
	return node
```

对应的 C#：

```csharp
// C# —— scripts/BoardManager.cs
using Godot;

public partial class BoardManager : Node2D
{
    [ExportGroup("棋盘尺寸")]
    [Export] public int Columns { get; set; } = Grid.Columns;
    [Export] public int Rows { get; set; } = Grid.Rows;

    [ExportGroup("随机撒物的数量区间（x = 最小，y = 最大）")]
    [Export] public Vector2I WallCount { get; set; } = new(5, 9);
    [Export] public Vector2I FoodCount { get; set; } = new(1, 5);

    [ExportGroup("固定物件")]
    [Export] public PackedScene ExitScene { get; set; }
    [Export] public PackedScene PlayerScene { get; set; }

    [ExportGroup("模板候选池")]
    [Export] public Godot.Collections.Array<PackedScene> FloorScenes { get; set; } = new();
    [Export] public Godot.Collections.Array<PackedScene> WallScenes { get; set; } = new();
    [Export] public Godot.Collections.Array<PackedScene> OuterWallScenes { get; set; } = new();
    [Export] public Godot.Collections.Array<PackedScene> FoodScenes { get; set; } = new();
    [Export] public Godot.Collections.Array<PackedScene> EnemyScenes { get; set; } = new();

    private readonly System.Collections.Generic.List<Vector2I> _freeCells = new();

    public void SetupScene(int level)
    {
        BuildFloorAndOuterWalls();
        CollectFreeCells();

        ScatterAtRandom(WallScenes, WallCount.X, WallCount.Y);
        ScatterAtRandom(FoodScenes, FoodCount.X, FoodCount.Y);

        var enemyCount = (int)(Mathf.Log(level) / Mathf.Log(2.0));
        ScatterAtRandom(EnemyScenes, enemyCount, enemyCount);

        Spawn(ExitScene, new Vector2I(Columns - 1, Rows - 1));
        Spawn(PlayerScene, new Vector2I(0, 0));
    }

    private void BuildFloorAndOuterWalls()
    {
        for (var x = -1; x < Columns + 1; x++)
        for (var y = -1; y < Rows + 1; y++)
        {
            var cell = new Vector2I(x, y);
            var scene = Grid.IsOuter(cell) ? OuterWallScenes.PickRandom() : FloorScenes.PickRandom();
            Spawn(scene, cell);
        }
    }

    private void CollectFreeCells()
    {
        _freeCells.Clear();
        for (var x = 1; x < Columns - 1; x++)
        for (var y = 1; y < Rows - 1; y++)
            _freeCells.Add(new Vector2I(x, y));
    }

    private Vector2I TakeRandomCell()
    {
        var index = GD.RandRange(0, _freeCells.Count - 1);
        var cell = _freeCells[index];
        _freeCells.RemoveAt(index);
        return cell;
    }

    private void ScatterAtRandom(Godot.Collections.Array<PackedScene> scenes, int minimum, int maximum)
    {
        var count = GD.RandRange(minimum, maximum);
        for (var i = 0; i < count; i++)
            Spawn(scenes.PickRandom(), TakeRandomCell());
    }

    private Node2D Spawn(PackedScene scene, Vector2I cell)
    {
        var node = scene.Instantiate<Node2D>();
        node.Position = Grid.ToWorld(cell);
        AddChild(node);
        return node;
    }
}
```

---

### 7.1 `Vector2i` 当"区间"

```gdscript
@export var wall_count := Vector2i(5, 9)    # x = 最小，y = 最大
```

```csharp
[System.Serializable] public class Count { public int minimum; public int maximum; }
```

**Godot 不需要**：`Vector2i` 是**内建的可序列化类型**，Inspector 里直接显示成两个整数框（`x` / `y`）。

> 说句公道话：这里用 `Vector2i` 装 (min, max) 是**社区的惯例 hack**，语义上"两个整数"和"一个二维向量"确实不搭。
> Godot 的"正统"做法是**自定义 `Resource`**（[00 章 §4.1](./00-核心概念地图.md#41-复杂配置用-resource)），还能存成 `.tres` 文件复用。本项目用 `Vector2i` 图省事，但要记得有更好的选择。

### 7.2 `log(level) / log(2.0)` 求敌人数量

GDScript / C#：内置 `log()` 都是**自然对数**，所以要换底：`log(level) / log(2.0)`。

| level | `log(level)/log(2)` | `int()` 截断后 |
|---|---|---|
| 1 | 0.0 | 0 |
| 2 | 1.0 | 1 |
| 3 | 1.585 | 1 |
| 4 | 2.0 | 2 |
| 8 | 3.0 | 3 |
| 16 | 4.0 | 4 |

> ⚠️ **浮点误差陷阱**：`log(8)/log(2)` 在 double 下可能算出 `2.9999999999999996`，`int()` 截断就变成 **2** 而不是 3。
> 本项目无所谓（差一个敌人不影响手感），但你要**养成习惯**：这种"对数取整"该用 `roundi(log(level) / log(2.0))` 或干脆查表/公式化。

```csharp
Vector3 randomPosition = gridPositions[randomIndex];
gridPositions.RemoveAt(randomIndex);
return randomPosition;
```

```gdscript
# Godot：取走并从数组里删除，一个方法搞定
return _free_cells.pop_at(randi_range(0, _free_cells.size() - 1))
```

**GDScript 的 `Array` 比 C# 的 `List<T>` 方法更全**（`pop_at` / `pick_random` / `shuffle` / `map` / `filter` 都有）。这也是 GDScript 写起来"短"的原因之一。

### 7.4 GDScript 的 `for i in count`

```gdscript
for i in count:          # count 是 int → 相当于 for (int i = 0; i < count; i++)
	_spawn(...)
```

GDScript 里 `for x in <int>` 是"循环这么多次"（类似 Python 的 `range(n)` 简写）。**这不是笔误**，是惯用写法。等价于 `for i in range(count):`。

---

## 8. 在 Inspector 里配置

选中 `main.tscn` 里的 **`Board`** 节点：

**模板候选池**（把 `.tscn` 从文件系统面板拖进来）：

| 字段 | 拖入 |
|---|---|
| `Floor Scenes` | `floor.tscn`（**同名多份**，或者以后做 `floor_2.tscn` 再拖进来） |
| `Wall Scenes` | `wall.tscn` × N（或者做 `wall_2/wall_3` 变体） |
| `Outer Wall Scenes` | `outer_wall.tscn` |
| `Food Scenes` | `food.tscn`、`soda.tscn` |
| `Enemy Scenes` | `enemy.tscn` |
| `Exit Scene` | `exit.tscn` |
| `Player Scene` | `player.tscn` |

**尺寸与数量**：`Columns = 8`、`Rows = 8`、`Wall Count = (5, 9)`、`Food Count = (1, 5)`。

> **`soda.tscn` 想更稀有**？把它在数组里重复拖多份、`food.tscn` 拖少份就行（`pick_random` 均匀取样 → 出现次数 = 权重）。**数组元素可以重复**，这是个很好用的技巧。

---

## 9. 运行验证

按 `F5`：

1. 黑幕 `Day 1`
2. 输出面板不再打印"尚未实现"
3. 2 秒后黑幕消失，**一张 8×8 的棋盘出现**：外圈墙、内部随机散布墙块和食物、右下角有出口、左下角有玩家
4. 场景树面板（运行中）展开 `Board`，应该看到 **100 个地板/外墙**（10×10）+ 随机撒的墙块和食物 + 玩家 + 出口

**反复 `F5` 几次**，每次地图都应该不一样。

> **注意玩家现在只有一个 `Sprite2D`**：它还不能动（[04 章](./04-玩家与敌人-移动与回合制.md) 才写移动）。而且如果 `player.tscn` 还没配 `player.gd`，控制台可能提示"脚本为空"——**这正常**。

---

## 10. 小实验（强烈建议做）

1. **把 `Columns` / `Rows` 改成 12** → 棋盘变大，但**相机会不居中**。修正：
   ```gdscript
   # level.gd 里让相机自动对准棋盘中心
   @onready var board: BoardManager = $Board
   @onready var camera: Camera2D = $Camera2D

   func _ready() -> void:
       camera.position = Vector2(
           (board.columns - 1) * Grid.TILE / 2.0,
           (board.rows - 1) * Grid.TILE / 2.0)      # 8×8 → (56, 56)

       GameManager.begin_level()
       board.setup_scene(GameManager.level)
   ```
2. **把 `Wall Count` 改成 `(20, 20)`** → 看地图被堵死的样子。
3. **把 `enemy_count` 写死成 5** → 一次看到一堆敌人。
4. **把 `_scatter_at_random` 里的 `pick_random()` 换成 `scenes[0]`** → 地图变得整齐划一，你就明白"为什么要数组"了。

---

## 11. 本章的坑

| 现象 | 原因 |
|---|---|
| 一个 tile 都没生成 | `Floor Scenes` 数组**是空的**（不是"长度 0"，是根本没拖东西进去） |
| `Cannot call method 'instantiate' on a null value` | 某个 `@export` 是空的（`Exit Scene` / `Player Scene` 忘拖） |
| 报"数组越界" | `_free_cells` 被撒空了（`Wall Count` 的最大值超过 36 试试） |
| 生成的 tile 全在左上角堆成一坨 | `_spawn` 里忘了 `position = ...`，全部落在原点 |
| 生成的东西完全不显示 | `_spawn` 里忘了 `add_child(node)` |
| 所有地板长得一样 | `Floor Scenes` 只拖了 1 个（或者重复拖同一个文件） |
| 相机里棋盘偏在一边 | `Camera2D` 的位置不是 `(56, 56)`。用 §10.1 的公式自己算 |

---

## 12. ✅ 自检清单

- [ ] 能解释 `instantiate()` 和 `add_child()` 分别做了什么、少一个会怎样
- [ ] 能说出 `Vector2i` 为什么能直接在 Inspector 里当"(最小值, 最大值)"用
- [ ] 能自己把棋盘改成 12×12 并算出新的相机位置
- [ ] `F5` 后能看到随机棋盘，反复运行地图不同，无报错

下一章：[04 玩家与敌人：移动与回合制](./04-玩家与敌人-移动与回合制.md)
