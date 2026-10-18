# Dodge the Creeps · GDScript 版

这是官方入门教程《Your first 2D game》的 **GDScript 成品项目**，和同目录的 C# 版 [DodgeTheCreeps](../DodgeTheCreeps/) 一一对应。

| | |
|---|---|
| 引擎 | Godot 4.7.2 |
| 语言 | GDScript |
| 渲染器 | GL Compatibility（2D 足够，且可直接导出 Web） |
| 分辨率 | 480 × 720，`canvas_items` 拉伸 |
| 操作 | 方向键移动；标题界面点 **Start** |

## 运行

1. 打开 Godot 项目管理器 → **导入（Import）** → 选择本目录的 `project.godot`。
2. 按 **F5** 运行。

GDScript 保存脚本后**不需要编译/Build**，直接重新运行即可。

## 目录

```
DodgeTheCreepsGD/
├─ project.godot          # 项目配置：分辨率、输入映射、主场景
├─ player.gd / .tscn      # 玩家：移动、动画、碰撞、hit 信号
├─ mob.gd / .tscn         # 敌人：随机动画、飞出屏幕后自毁
├─ main.gd / .tscn        # 主场景：刷怪、计分、游戏流程
├─ hud.gd / .tscn         # HUD：分数、提示、Start 按钮
├─ art/                   # 图片与音频
└─ fonts/                 # UI 字体（含授权文件）
```

## 和 C# 版的关键差异

| 概念 | C# 版 | GDScript 版 |
|---|---|---|
| 脚本文件 | `Player.cs` | `player.gd` |
| 继承 | `public partial class Player : Area2D` | `extends Area2D` |
| 全局类型 | `public partial class Player` | `class_name Player` |
| 导出变量 | `[Export] public float Speed { get; set; } = 400` | `@export var speed: float = 400.0` |
| 节点引用 | `GetNode<AnimatedSprite2D>("...")` | `@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D` |
| 声明信号 | `[Signal] delegate void HitEventHandler()` | `signal hit` |
| 发信号 | `EmitSignal(SignalName.Hit)` | `hit.emit()` |
| 等待信号 | `await ToSignal(timer, Timer.SignalName.Timeout)` | `await timer.timeout` |
| 改代码生效 | 先点「Build」 | 保存即生效 |
| 工程文件 | `.csproj` / `.sln` | 无 |
| 导出 Web | ❌ 不支持 | ✅ 支持（已用 GL Compatibility） |

## GDScript 代码里值得注意的点

- **缩进即语法**：用 Tab 缩进，同一块代码缩进必须一致。
- **`@onready`**：等节点进入场景树后再取子节点，等价于 C# 在 `_Ready()` 里 `GetNode`。
- **`&"move_left"`**：`&` 前缀创建 `StringName`，比普通字符串更适合高频 API 调用。
- **`:=` 是类型推断，不是动态类型**：`var x := 1` 仍然是静态 `int`。本项目为了示范类型系统，成员、参数、返回值全部显式标注。
- **`_` 开头的参数**：表示"我知道这个参数用不到"（例如 `_body`），避免未使用警告。
- **`await` 是语言内建的**：`hud.gd` 的 `show_game_over()` 用两次 `await` 串起"Game Over → 标题 → Start 按钮"的流程。

## 静态类型（本项目默认强制）

四个脚本都用了 `class_name`（`Player` / `Mob` / `HUD` / `Main`），所有成员变量、函数参数、返回值都有具体类型，节点引用用 `@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D` 这种方式缓存。

`project.godot` 把下面这些警告当成**错误**（`2`）：

| 设置 | 抓什么 |
|---|---|
| `untyped_declaration` | `var x = 1` 这种不写类型的声明 |
| `unsafe_property_access` | 在 `Variant` 上访问属性 |
| `unsafe_method_access` | 在 `Variant` / 过宽类型上调用方法 |
| `unsafe_cast` | 把 `Variant` 直接转成具体类型 |
| `unsafe_call_argument` | 把 `Variant` 传给有类型要求的参数 |

资源加载用 `PackedScene.instantiate() as Mob` + `null` 检查，而不是 `load(...).instantiate()`（后者会触发 `unsafe_method_access`）。

完整的类型系统、`Variant` 边界、`StringName`、typed array/dictionary、性能建议和练习，见 **[GDScript 类型系统与进阶](../GDScript-类型系统与进阶.md)**。

## 难度递增

每 **10 分**升一级，最高 **10 级**。刷怪越来越快，敌人也越来越快：

| 等级 | 分数 | 刷怪间隔 | 敌人速度 |
|---|---|---|---|
| Lv.1 | 0–9 | 0.50 s | 150–250 |
| Lv.2 | 10–19 | 0.46 s | 170–270 |
| Lv.3 | 20–29 | 0.42 s | 190–290 |
| Lv.5 | 40–49 | 0.34 s | 230–330 |
| Lv.10 | 90+ | 0.15 s | 330–430 |

所有参数都在 `Main` 节点的 **Inspector → Difficulty** 分组里，可以直接改来调整手感：

| 参数 | 默认值 | 作用 |
|---|---|---|
| `points_per_level` | 10 | 升一级需要多少分 |
| `max_level` | 10 | 最高等级 |
| `base_spawn_interval` | 0.5 | 1 级时多久刷一个敌人 |
| `spawn_interval_step` | 0.04 | 每升一级缩短多少秒 |
| `min_spawn_interval` | 0.15 | 刷怪间隔下限 |
| `base_speed_min` / `base_speed_max` | 150 / 250 | 1 级敌人速度范围 |
| `speed_bonus_per_level` | 20 | 每升一级给敌人加多少速度 |

> 想更狠：把 `spawn_interval_step` 调大、`min_spawn_interval` 调小；想轻松：把 `speed_bonus_per_level` 调成 5。

## 下一步：更难的官方示例

按难度从低到高：

| 示例 | 类型 | 能学到什么 |
|---|---|---|
| [Your first 3D game / Squash the Creeps](https://docs.godotengine.org/en/stable/getting_started/first_3d_game/index.html) | 官方教程 | 3D 坐标、跳跃、踩怪、物理层、3D UI |
| [2D Platformer](https://github.com/godotengine/godot-demo-projects/tree/master/2d/platformer) | 官方 Demo | 完整平台跳跃：斜坡、射击、敌人、金币、相机边界、暂停菜单 |
| [2D Role Playing Game](https://github.com/godotengine/godot-demo-projects/tree/master/2d/role_playing_game) | 官方 Demo | 格子移动、JRPG 对话与战斗系统 |
| [2D Isometric Game](https://github.com/godotengine/godot-demo-projects/tree/master/2d/isometric) | 官方 Demo | 等距视角、深度排序、2D 光照与遮挡 |
| [3D Truck Town](https://github.com/godotengine/godot-demo-projects/tree/master/3d/truck_town) | 官方 Demo | 载具物理、关节、3D 场景与相机 |
| [TPS Demo](https://github.com/godotengine/tps-demo) | 官方 Demo | 大型 3D 第三人称射击项目 |

> 官方 Demo 都能直接在线试玩：<https://godotengine.github.io/godot-demo-projects/>
> 本仓库还有一套更贴近独立游戏开发的 [回合制 Roguelike 附录](../附录-回合制Roguelike/README-原Roguelike主线.md)（Autoload、棋盘生成、回合制状态机、Tween）。

## 快速自检

- [ ] 标题界面显示 `Dodge the Creeps!`、`Lv.1` 和 Start 按钮
- [ ] 点 Start 后出现 `Get Ready`，约 2 秒后开始刷怪
- [ ] 方向键移动玩家，动画/翻转正常，撞到敌人后显示 `Game Over`
- [ ] 分数每秒 +1，达到 10 分时升到 `Lv.2`，刷怪明显变快
- [ ] 重开后分数、等级、刷怪间隔全部归零
- [ ] 背景音乐循环，死亡音效播放一次
