# 用 Godot 4.7 做一个 2D Roguelike —— 写给"会 C#、没碰过 Godot"的人

> **引擎**：Godot **4.7.2 stable**（2026-08 发布，当前最新稳定版）
> **语言**：**GDScript 主线 + C# 对照**。每一段功能代码都给你两份，可以左右对着读。

---

## 0. 先读这一节：双语言怎么用

| 你想干什么 | 怎么写 |
|---|---|
| 最快跑通、最贴官方文档 | 只看 **GDScript** 代码块 |
| 复用 .NET 肌肉记忆、要 NuGet / 单元测试 | 只看 **C#** 代码块 |
| 想真正理解两种写法的取舍 | 两份都读，看每个代码块后面的「**⚠️ 差异点**」小方框 |

**三个必须先知道的硬事实**：

1. **C# 项目无法导出 Web（浏览器）**。Godot 4 的 .NET 运行时没有 WASM 版本，官方文档明确写了这条。想发网页游戏 → 必须 GDScript（详见 [Godot 07 章](../07-收尾与导出.md)）。
2. **GDScript != 阉割版 C#**。它是为引擎 API 量身设计的语言，`signal` / `await` / `@export` / `@onready` 都是一等语法。用 C# 写 Godot 要多打 30%~50% 的样板字。

---

## 1. 环境准备（10 分钟）

### 1.1 下载哪个 Godot

去 [godotengine.org/download/windows](https://godotengine.org/download/windows/)，有两个包，**选哪个取决于你要不要写 C#**：

| 包名 | 你要它吗 | 说明 |
|---|---|---|
| `Godot_v4.7.2-stable_win64.exe.zip` | **只在 GDScript 路线时** | 标准版，解压即用，单文件 exe，**免安装、无注册、无登录** |
| `Godot_v4.7.2-stable_mono_win64.zip` | **要写 C# 就用这个** | .NET 版（`mono` 是历史叫法），内置 C# 支持 |

> **建议直接下 .NET 版**，即使你打算只用 GDScript：它包含了标准版的全部功能，只是文件大一点。这样以后想切 C# 不用重装。

### 1.2 写 C# 的话还要装 .NET SDK

.NET 版 Godot **只带了运行游戏所需的 .NET 运行时，不带编译工具链**。你还需要系统里的 .NET SDK（8.0 或更新）：

```powershell
dotnet --list-sdks
```

没有输出就说明没装，去 [dotnet.microsoft.com/download](https://dotnet.microsoft.com/download) 装一个。作为 C# 老手，你大概早就有。

### 1.3 第一次启动

1. 解压 → 双击 `Godot_v4.7.2-stable_mono_win64.exe`（**不是** `Godot_console.exe`，那个是用来抓崩溃日志的）。
2. 首次启动没有中文：菜单 `Editor → Editor Settings → Interface → Editor → Language → 简体中文`。
3. 项目管理器里点 **新建项目** → **渲染器选 `Forward+`**（2D 游戏用不上，但它是默认且最完整；想极致轻量可以选 `Compatibility`）。
4. 项目路径同样**别带中文和空格**。

---

```
study/
├─ README.md
├─ godot/
│  ├─ README.md
│  ├─ 00-核心概念地图.md
│  ├─ 01-项目设置.md
│  ├─ 02-玩家场景.md
│  ├─ ...
│  ├─ 素材/                    ← 教程素材（复制到你的 Godot 项目里用）
│  └─ 附录-回合制Roguelike/
└─ （Unity 版教程：仓库根目录的 00~07 章）
```

Godot 入门教程的导出说明见 [07 收尾与导出](../07-收尾与导出.md)。

---

## 3. 教程地图

| 章节 | 你要动手做的事 | 核心内容 |
|---|---|---|
| [03 BoardManager：程序化生成棋盘](./03-BoardManager-棋盘生成.md) | 写 `board_manager.gd`，随机生成地图 | 棋盘生成、场景实例化、`add_child()` |
| [04 玩家与敌人：移动与回合制](./04-玩家与敌人-移动与回合制.md) | 写 `moving_object` / `player` / `enemy` / `wall` | 使用 `await` 控制移动流程，并通过 `intersect_ray` 探测障碍 |
| [05 动画与音效](./05-动画与音效.md) | 做 `AnimatedSprite2D` 动画、写音效池 | `AnimatedSprite2D`、`AnimationPlayer`、音效管理 |
| [06 UI 与游戏流程](./06-UI与游戏流程.md) | 搭 `CanvasLayer` UI，打通关卡循环 | Canvas 锚点 → **Control + anchors**；信号驱动 UI |
| [07 收尾与导出](../07-收尾与导出.md) | 导出 Windows / Web，下一步学什么 | 导出模板、`.gitignore`、生态 |

---

## 4. 最终项目长什么样（先有个目标）

```
2d-roguelike-godot/            ← Godot 项目根目录
│  ├─ sprites/                 （16×16 的 tile、角色、道具）
│  └─ audio/
├─ scenes/
│  ├─ main.tscn                ← 主场景 = 一个关卡
│  ├─ level_ui.tscn            ← 黑幕 + Day N + Food 文本
│     ├─ floor.tscn            Sprite2D
│     ├─ wall.tscn             StaticBody2D + Sprite2D + CollisionShape2D
│     ├─ outer_wall.tscn       StaticBody2D + ...
│     ├─ food.tscn             Area2D + Sprite2D + CollisionShape2D
│     ├─ soda.tscn             Area2D + ...
│     ├─ exit.tscn             Area2D + ...
│     ├─ player.tscn           CharacterBody2D + Sprite2D + CollisionShape2D + Area2D(拾取检测)
│     └─ enemy.tscn            CharacterBody2D + ...
└─ scripts/
   ├─ grid.gd                  网格常量与坐标换算（全局静态类）
   ├─ game_manager.gd          Autoload：跨关卡状态 + 回合裁判
   ├─ sfx.gd                   Autoload：音效池
   ├─ level.gd                 main.tscn 的根脚本：一关的装配与流程
   ├─ board_manager.gd         棋盘生成
   ├─ moving_object.gd         移动基类
   ├─ player.gd
   ├─ enemy.gd
   └─ wall.gd
```

---

## 5. 全局约定（先定规矩，后面不返工）

### 5.1 碰撞图层名字

`项目 → 项目设置 → 图层名称 → 2D 物理`，命名前两层：

| 位 | 名字 | 放什么 |
|---|---|---|
| 1 | `blocking` | Player、Enemy、Wall、OuterWall —— **会挡住移动的东西** |
| 2 | `pickup` | Food、Soda、Exit —— **踩上去触发的东西** |

```gdscript
add_to_group("food")
if body.is_in_group("food"): ...
```

### 5.3 命名规范

| 类型 | 风格 | 例子 |
|---|---|---|
| 文件、文件夹 | `snake_case` | `board_manager.gd`、`player.tscn` |
| 节点名 | `PascalCase` | `BoardManager`、`LevelUi` |
| 函数、变量 | `snake_case`（GDScript 强制） | `setup_scene()` |
| 常量 | `SCREAMING_CASE` | `TILE_SIZE` |
| 信号 | 过去式 / 名词 | `food_changed`、`level_started` |

> C# 侧仍按 .NET 习惯：**类名 PascalCase、方法 PascalCase、私有字段 `_camelCase`**。Godot 的 C# 绑定就是这么设计的，别强行统一。

---

## 6. GDScript ↔ C# 速查小抄（**建议先收藏**）

这是全程会反复用到的语法映射。看不懂细节没关系，写到对应章节再回来查。

### 6.1 定义与继承

```gdscript
# GDScript
extends CharacterBody2D          # 继承（必须第一行，或者用 class_name 后接 extends）
class_name Player                # 让这个类全局可访问（≈ C# 的 public class）
```

```csharp
// C#
public partial class Player : CharacterBody2D   // partial 是必须的！
```

> ⚠️ **C# 的 Godot 类必须写 `partial`**，因为引擎会为它生成源码（绑定信号、注册属性）。忘写就是一堆编译错误。

### 6.2 字段、导出、节点引用

```gdscript
# GDScript
@export var chop_sounds: Array[AudioStream]  # 数组也能导出

```

```csharp
// C#
[Export] public float MoveTime { get; set; } = 0.1f;   // ⚠️ 必须是属性，不能是字段
[Export] public Godot.Collections.Array<AudioStream> ChopSounds { get; set; } = new();

private Sprite2D _sprite;                              // 没有 @onready 对应物
public override void _Ready() => _sprite = GetNode<Sprite2D>("Sprite2D");
```

> ⚠️ **两个高频坑**：① C# 的 `[Export]` **只认属性**，写字段不报错但不显示；② GDScript 里 `@export var x = 0.1` 的 `:=` 推断类型，导出数组要**显式写类型**。

### 6.3 生命周期

> **顺序差异很重要**：Godot 的 `_ready()` 是**子节点先就绪**（自底向上），所以父节点在 `_ready()` 里可以安全访问所有子节点。这正是 `@onready` 能工作的原因。

### 6.4 常用 API 对照

| 想干什么 | GDScript | C# |
|---|---|---|
| 取子节点 | `$Sprite2D` / `get_node("Sprite2D")` | `GetNode<Sprite2D>("Sprite2D")` |
| 找节点 | `get_tree().get_first_node_in_group("player")` | `GetTree().GetFirstNodeInGroup("player")` |
| 加子节点 | `add_child(node)` | `AddChild(node)` |
| 销毁自己 | `queue_free()` | `QueueFree()` |
| 打印 | `print(x)` | `GD.Print(x)` |
| 随机整数 | `randi_range(1, 5)`（闭区间） | `GD.RandRange(1, 5)` |
| 随机取一个 | `array.pick_random()` | `array.PickRandom()` |
| 等一帧 | `await get_tree().process_frame` | `await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame)` |
| 等 N 秒 | `await get_tree().create_timer(1.0).timeout` | `await ToSignal(GetTree().CreateTimer(1.0), SceneTreeTimer.SignalName.Timeout)` |
| 做补间 | `var t := create_tween()` | `var t = CreateTween();` |
| 发信号 | `food_changed.emit(v)` | `EmitSignal(SignalName.FoodChanged, v)` |
| 连信号 | `node.foo.connect(_on_foo)` | `node.Foo += OnFoo;` |

### 6.5 声明信号

```gdscript
# GDScript
signal food_changed(food: int, delta_text: String)   # 参数可带类型
food_changed.emit(100, "")
```

```csharp
// C#
[Signal] public delegate void FoodChangedEventHandler(int food, string deltaText);
EmitSignal(SignalName.FoodChanged, 100, "");          // 用生成的 SignalName 常量，避免拼错
```

> ⚠️ C# 里信号委托**必须以 `EventHandler` 结尾**，否则引擎不认。而且它是**引擎生成 `SignalName` 常量**的来源，所以请务必用 `SignalName.Xxx` 而不是手写字符串。

### 6.6 `null` 与"已销毁对象"

```gdscript
# GDScript
if is_instance_valid(enemy):
    enemy.move_enemy()
```

```csharp
// C#
if (GodotObject.IsInstanceValid(enemy))
    enemy.MoveEnemy();
```

> 记住这条，[04 章](./04-玩家与敌人-移动与回合制.md) 的敌人列表就靠它。

---

## 7. 学完这个你会得到什么

| 概念 | 你会怎么用它 |
|---|---|
| `PackedScene` | 场景资源，用于创建节点实例 |
| `await` | 等待信号或异步操作完成 |
| `intersect_ray` | 移动前的障碍探测 |
| Tween | 在指定时间内平滑修改属性 |

准备好了就翻 [00 章](./00-核心概念地图.md)。
