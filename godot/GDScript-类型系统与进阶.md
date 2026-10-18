# GDScript 类型系统与进阶（面向有经验的程序员）

> 环境：**Godot 4.7.2** · 配套项目：[DodgeTheCreepsGD](./DodgeTheCreepsGD/)
> 不铺垫变量、循环、函数这些基础语法；只讲**类型系统、边界、性能和工程实践**。

---

## 0. 一句话模型

GDScript 4 是**渐进类型（gradual typing）**语言：

| 写法 | 静态类型 | 运行时 |
|---|---|---|
| `var hp: int = 10` | ✅ `int` | 直接操作 `int` |
| `var hp := 10` | ✅ 推断为 `int`（仍是静态类型） | 直接操作 `int` |
| `var hp = 10` | ❌ `Variant` | 动态分派 |

`Variant` 是**顶层类型**（类似 C# `object`），不是"随便什么都能编译通过"的 `any`：它带着运行时类型标签，但静态检查基本帮不上忙。

**结论**：把 `Variant` 限制在边界上（JSON、`Dictionary`、`call()`、资源加载），进入业务代码前立刻收窄成具体类型。

---

## 1. 本项目如何强制静态类型

`project.godot` 里已经把这些警告**当成错误**：

```ini
[debug]

gdscript/warnings/untyped_declaration=2
gdscript/warnings/unsafe_property_access=2
gdscript/warnings/unsafe_method_access=2
gdscript/warnings/unsafe_cast=2
gdscript/warnings/unsafe_call_argument=2
gdscript/warnings/return_value_discarded=1
gdscript/warnings/missing_await=1
```

值含义：`0` 忽略、`1` 警告、`2` 错误。

| 设置 | 能抓到什么 |
|---|---|
| `untyped_declaration` | `var x = 1` 这种不写类型的声明 |
| `unsafe_property_access` | 在 `Variant` 上访问属性 |
| `unsafe_method_access` | 在 `Variant` / 过宽类型上调用方法（典型：`load(...).instantiate()`） |
| `unsafe_cast` | 把 `Variant` 直接转成具体类型 |
| `unsafe_call_argument` | 把 `Variant` 传给有类型要求的参数 |
| `return_value_discarded` | 忽略有返回值的函数结果 |
| `missing_await` | 调用 `async` 函数却没 `await` |

另外几个**默认就是错误**的相关项，也值得知道：

| 设置 | 默认 | 触发例子 |
|---|---|---|
| `inference_on_variant` | `2` | `var x := null`（推断出 `Variant`） |
| `get_node_default_without_onready` | `2` | 在成员变量默认值里用 `$Node` / `get_node()`，却没写 `@onready` |
| `onready_with_export` | `2` | 同时写 `@onready` 和 `@export` |

> 想改回来：**项目设置 → 调试 → GDScript → 警告**，或者直接改 `project.godot`。

---

## 2. 类型标注手册

### 2.1 变量、参数、返回值

```gdscript
var score: int = 0
var speed: float = 400.0
var player: Player = null          # 对象类型可以为 null
var mobs: Array[Mob] = []

func start(pos: Vector2) -> void:
	position = pos

func find_player() -> Player:
	return get_node_or_null("Player") as Player
```

- `-> void` 建议显式写，读者一眼能看出这是过程而不是查询。
- 局部变量可以用 `:=` 推断；**本项目为了示范类型系统，全部显式标注**。
- 不要写 `var x = ...`：在 `untyped_declaration=2` 下直接编译失败。

### 2.2 值类型

| 类型 | 说明 |
|---|---|
| `int` | 64 位有符号整数 |
| `float` | 64 位浮点（GDScript 层）；`Vector2` 内部是 32 位 `real_t`（标准构建） |
| `bool` | 布尔 |
| `String` | UTF-32 字符串，适合展示/拼接 |
| `StringName` | 驻留字符串，适合**高频 API 调用**（动作名、属性名、节点名） |
| `NodePath` | 场景路径，`^"MobPath/MobSpawnLocation"` 是字面量写法 |
| `Vector2` / `Vector3` | 值类型，赋值是拷贝 |
| `Color` / `Rect2` / `Transform2D` | 值类型 |

`StringName` 不是"更短的 String"：它全局驻留、哈希缓存，比较和作为键都更快。代价是创建开销比普通字符串高，所以**适合常量/高频名字，不适合每帧拼接**。

### 2.3 对象类型与可空性

GDScript **没有** `Player?` / `Player!` 这种可空性标注。所有对象类型都可以是 `null`：

```gdscript
var player: Player = null
if player == null:
	return
```

已经被 `queue_free()` 的节点是"悬空引用"：`player != null` 仍可能为 `true`，但访问会报错。跨帧保存节点引用时用：

```gdscript
if not is_instance_valid(player):
	return
```

### 2.4 `is`、`as` 与类型收窄

```gdscript
var node: Node = get_node("Player")

if node is Player:
	node.start(Vector2(240, 450))   # 这里 node 被收窄为 Player

var player: Player = node as Player   # 失败时返回 null，不抛异常
if player == null:
	push_error("Player node has the wrong script")
```

- `is` 只做判断，但 GDScript 4 会在分支内**收窄**类型。
- `as` 是**运行时**检查；不会做数值/字符串转换。
- 数值转换用 `int()`、`float()`；字符串转换用 `str()`。

### 2.5 `class_name`：给脚本一个全局类型

```gdscript
class_name Player
extends Area2D
```

注册后，`Player` 就成了全局类型，可以用在：

```gdscript
var player: Player = null
var target: Player = null
var mobs: Array[Mob] = []
signal died(who: Player, score: int)
```

本项目的四个脚本都注册了全局类：[Player](./DodgeTheCreepsGD/player.gd)、[Mob](./DodgeTheCreepsGD/mob.gd)、[HUD](./DodgeTheCreepsGD/hud.gd)、[Main](./DodgeTheCreepsGD/main.gd)。

注意：`class_name` 是**全局命名空间**，项目内不能重名；两个都叫 `Player` 的脚本会冲突。

### 2.6 泛型容器（typed containers）

```gdscript
var mobs: Array[Mob] = []
var scores: Dictionary[String, int] = {"alice": 10}

for mob: Mob in mobs:
	mob.queue_free()
```

- `Array[T]` 和 `Dictionary[K, V]` 的**运行时**也会检查插入类型，不是只给编辑器看的。
- `Dictionary[K, V]` 需要 Godot 4.4+；本项目用的 4.7.2 支持。
- `PackedStringArray`、`PackedInt32Array`、`PackedVector2Array` 等是**连续内存**的打包数组，适合大量数值/顶点数据；`Array[T]` 仍是通用数组。

### 2.7 函数、信号与 `Callable`

信号参数也可以有类型：

```gdscript
signal died(who: Player, score: int)

func _on_died(who: Player, score: int) -> void:
	print(who.name, score)

func _ready() -> void:
	died.connect(_on_died)        # 推荐：Callable，方法名不会拼错
	# connect("died", Callable(self, "_on_died"))   # 旧式动态连接，绕开类型检查
```

- `died.emit(who, score)` 的参数在**编译期**检查。
- `died.connect(_on_died)` 至少能避免字符串方法名；**信号参数与回调签名的匹配在运行时检查**（`emit` 时校验）。
- 用字符串连接（`connect("died", ...)`）或 `call_group` 时，**方法名和参数都在运行时才检查**。
- `await timer.timeout` 在 `timer: Timer` 类型下是静态可解析的；如果 `timer` 是 `Variant`，就退化成动态。

### 2.8 枚举

```gdscript
enum State { IDLE, RUN }

var state: State = State.IDLE
```

枚举在底层是 `int`，但 `State` 可以作为类型标注。相关警告：`int_as_enum_without_cast`、`int_as_enum_without_match`、`enum_variable_without_default`——默认都是警告级别。

### 2.9 `@export` 与 Inspector

```gdscript
@export_range(0.0, 2000.0, 10.0) var speed: float = 400.0
@export var mob_scene: PackedScene
@export var target: Player
@export var mobs: Array[Mob] = []
```

- `@export_range` 只适用于数值类型。
- `@export var target: Player` 可以直接在 Inspector 里拖节点，类型必须是 `Player` 或其子类。
- 场景里如果没赋值，运行时是 `null`；**静态类型不代表一定有值**，仍要判空。

---

## 3. `Variant` 的边界

这些 API 返回的是宽类型，进入业务代码前要收窄：

| API | 返回 | 收窄方式 |
|---|---|---|
| `Dictionary.get()` / `dict[key]` | `Variant` | 用 `Dictionary[K, V]`，或 `as`/转换函数 |
| `Object.get()` / `get_meta()` | `Variant` | 同上 |
| `Object.call()` / `call_deferred()` / `call_group()` | `Variant` | 尽量改成直接方法调用 |
| `JSON.parse_string()` | `Variant` | `if data is Dictionary:` 后再取字段 |
| `load(path)` | `Resource` | 用 `preload()` 得到具体资源类型，或显式 `as` |
| `PackedScene.instantiate()` | `Node` | `as Mob` + null 检查 |

一个典型的边界写法：

```gdscript
var data: Variant = JSON.parse_string(text)
if data is not Dictionary:
	push_error("invalid save file")
	return

var save: Dictionary = data
var score: int = 0
var raw_score: Variant = save.get("score", 0)
if raw_score is int:
	score = raw_score
elif raw_score is float:
	var raw_float: float = raw_score
	score = int(raw_float)

var player_name: String = str(save.get("name", "anonymous"))
```

> 在 `unsafe_call_argument=2` 下，`int(save.get(...))` 会直接报错：`get()` 返回 `Variant`，而 `int()` 的重载要求 `int` / `bool` / `float`。所以**边界值必须先收窄**再转换。

> `as` 不做转换：`"12" as int` 是错误用法；用 `int("12")`。

---

## 4. 静态类型带来的性能收益

GDScript 编译器对**已知类型**会生成更直接的字节码；`Variant` 则要走动态分派/装箱。

### 4.1 热路径原则

1. **缓存节点**：`@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D`，不要在 `_process` 里反复 `$Path` / `get_node`。
2. **只写变化的属性**：本项目 `player.gd` 用 `_is_animating`、`_current_animation`、`_flip_h/_flip_v` 做脏检查，避免每帧写 `animation`/`flip_h`。
3. **一次读取、一次写入**：`position` 是引擎属性，先读到局部 `Vector2` 里算完，再写回一次。
4. **停掉不需要的处理**：标题界面和死亡后 `set_process(false)`，不要在隐藏状态里空跑 `_process`。
5. **用 `StringName`**：`Input.is_action_pressed(&"move_left")`、`get_node(^"MobPath/MobSpawnLocation")`。
6. **避免每帧分配**：不在 `_process` 里建闭包、拼字符串、`new` 对象、用 LINQ 式链式调用。
7. **区分容器**：`Array[T]` 方便但仍是通用数组；大量数值用 `Packed*Array`。

### 4.2 信号 vs 直接调用

信号适合**一对多、解耦**（HUD ↔ Main、Player → Main）；热路径里大量 `emit` + `Callable` 调用会比直接方法调用贵。不要为了"架构漂亮"把每帧逻辑做成信号。

### 4.3 `await` 的成本

`await` 会创建协程状态，适合**低频流程**（游戏结束动画、过场、加载）；不要放进 `_process` 做逐帧等待。

### 4.4 物理回调

物理回调里不能直接改碰撞形状/物理属性，用：

```gdscript
_collision.set_deferred(&"disabled", true)
```

这不是类型问题，但和"热路径/生命周期"一起出现，容易踩。

---

## 5. 静态类型**不能**保证什么

1. **不能保证非空**：对象类型都可为 `null`；`@export` 节点可能没拖。
2. **不能保证场景结构**：`@onready var _player: Player = $Player` 只是运行时转换；节点名写错、脚本挂错，运行时报错。
3. **不能保证信号连接**：字符串连接的信号名/方法名在运行时才检查。
4. **不能保证 `Variant` 不回来**：`Dictionary`、`call()`、JSON、资源加载都是入口。
5. **没有接口/泛型函数**：用基类、组合或 `Callable` 代替；不要硬套 C# 的泛型设计。
6. **不能代替测试**：类型检查抓语法/类型错误，抓不到逻辑错误、数值平衡、场景接线错误。

可以用一个继承 `SceneTree` 的脚本做 headless 验证：加载主场景、跑完整游戏流程、断言难度曲线，比手点可靠。思路见下面的最小骨架：

```gdscript
extends SceneTree

const MAIN_SCENE: PackedScene = preload("res://main.tscn")

var _main: Main

func _initialize() -> void:
	_main = MAIN_SCENE.instantiate() as Main
	root.add_child(_main)

func _process(_delta: float) -> bool:
	# 在这里驱动 new_game() / 断言 / 模拟受击，完成后 return true 退出。
	return false
```

运行时用 `--fixed-fps 60` 让计时器按固定步长推进：

```powershell
godot --headless --path . --fixed-fps 60 --script res://tests/smoke_test.gd
```

---

## 6. 本项目的类型化对照

| 位置 | 类型化写法 | 说明 |
|---|---|---|
| [player.gd](./DodgeTheCreepsGD/player.gd) | `class_name Player`、`@export_range var speed: float`、`@onready var _sprite: AnimatedSprite2D` | 玩家脚本全部显式类型 |
| [player.gd](./DodgeTheCreepsGD/player.gd) | `var direction: Vector2 = Input.get_vector(...)` | `Input.get_vector` 返回已知 `Vector2` |
| [player.gd](./DodgeTheCreepsGD/player.gd) | `_set_animation(animation: StringName)` | 动画名用 `StringName`，避免字符串比较 |
| [main.gd](./DodgeTheCreepsGD/main.gd) | `@export var mob_scene: PackedScene` + `as Mob` + null 检查 | 资源边界收窄的标准写法 |
| [main.gd](./DodgeTheCreepsGD/main.gd) | `@onready var _mob_timer: Timer = $MobTimer` | 不再用 `$MobTimer.start()` 这种宽类型调用 |
| [main.gd](./DodgeTheCreepsGD/main.gd) | `floori(float(score) / float(points_per_level))` | 显式浮点除法，避免整数除法警告 |
| [mob.gd](./DodgeTheCreepsGD/mob.gd) | `PackedStringArray` + `StringName(...)` | 引擎返回打包数组，再转成动画名类型 |
| [hud.gd](./DodgeTheCreepsGD/hud.gd) | 所有 Label/Timer/Button 都有具体类型 | `await _message_timer.timeout` 可静态解析 |
| [project.godot](./DodgeTheCreepsGD/project.godot) | `untyped_declaration=2` 等 | 把动态写法挡在编译期 |

---

## 7. 进阶练习

1. **把难度参数做成 `Resource`**
   新建 `DifficultyConfig`（`class_name DifficultyConfig extends Resource`），把 `points_per_level`、`spawn_interval_step` 等放进去，然后 `@export var difficulty: DifficultyConfig`。这是 Godot 里替代"配置类"的常用做法。

2. **用 `Array[Mob]` 管理活着的敌人**
   在 `Main` 里维护 `var _active_mobs: Array[Mob] = []`，刷怪时 append，敌人 `tree_exited` 时 remove；对比"遍历 `get_tree().get_nodes_in_group()`"的成本。

3. **给 HUD 加类型化信号**
   `signal level_changed(level: int)`，让 HUD 自己订阅；对比现在的直接方法调用，理解解耦和开销的取舍。

4. **做一份类型化的存档**
   `Dictionary[String, int]` 存最高分，写入 JSON；读回时按 §3 的边界写法逐步收窄，体会"静态类型 + 运行时校验"如何配合。

5. **故意打开/关闭警告**
   把 `unsafe_method_access` 从 `2` 改成 `1`，写一行 `load("res://mob.tscn").instantiate()`，看警告如何出现，再改回 `preload` 的写法。

6. **性能对照**
   写一个循环，用 `Array[int]` 和 `PackedInt32Array` 各存 100 万个整数，用 `Time.get_ticks_usec()` 比较遍历耗时；理解"类型化数组"和"连续内存"不是一回事。

---

## 8. 延伸阅读

- [GDScript 参考：静态类型](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/static_typing.html)
- [GDScript 风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
- [GDScript 警告系统](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/warning_system.html)
- [C# 与 GDScript 的差异](https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_differences.html)
