# 从零做一个 2D 游戏 —— Godot 4.7 一步步教程

> **本篇是官方教程《Your first 2D game / Dodge the Creeps》的中文伴读 + 手把手操作手册。**
> 目标：**你从"没装过 Godot"开始，照着本篇走完 7 章，手上会有一个能玩、能打包发出去的游戏。**
>
> - **引擎**：Godot **4.7.2 stable**
> - **语言**：每段代码给 **GDScript 与 C# 两份**，你挑一条路线走完
> - **原文**：[官方教程（7 节）](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html)
> - **配套**：素材已经在本仓库里备好 → [素材/](./素材/)

---

## 0. 你会做出什么

一个竖屏躲避游戏：**你的角色在屏幕里移动，敌人从屏幕四边不断涌进来，撞到就结束。活得越久分数越高。**

```
┌─────────────────┐  480 × 720 竖屏
│       12        │  ← ScoreLabel（每秒 +1）
│                 │
│   Dodge the     │  ← MessageLabel（提示 / 标题）
│     Creeps!     │
│                 │
│        ●        │  ← Player（你，方向键控制）
│      ● ●        │  ← Mob（敌人，从边缘飞入）
│                 │
│    [ Start ]    │  ← StartButton（仅标题界面显示）
└─────────────────┘
```

**全部工作量**：4 个场景、4 个脚本、约 80 行逻辑代码。**预计 2~4 小时**（第一次用 Godot 的话）。

---

## 1. 路线图：每一步做完你会有什么

**严格按顺序做，每一章都依赖上一章的成果。** 每章末尾都有「✅ 自检清单」，勾完再往下走。

| 章 | 官方节 | 做完之后你会拥有 | 能运行验证吗 |
|---|---|---|---|
| [01 项目设置](./01-项目设置.md) | Setting up | 一个配好分辨率、导好素材的空项目 | — |
| [02 玩家场景](./02-玩家场景.md) | Player scene | `player.tscn`（有图、有判定框，但还不会动） | ✅ `F6` 能看静态图 |
| [03 玩家脚本](./03-玩家脚本.md) | Coding the player | 玩家**能按方向键移动**、会切动画、会被撞到 | ✅ `F6` 单独玩玩家（**先把 `Hide()` 临时注释掉**，见 03 章 §6） |
| [04 敌人](./04-敌人.md) | The enemy | `mob.tscn`（会飞的敌人，离屏自动消失） | ⭕ 单独跑只能看它飘 |
| [05 主场景](./05-主场景.md) | Main scene | `main.tscn`：**敌人从边缘刷出来了**、有分数 | ✅ `F5` 能玩（差 UI） |
| [06 HUD](./06-HUD.md) | HUD | `hud.tscn`：**分数 / 提示 / Start 按钮** → 游戏完整闭环 | ✅ `F5` **完整可玩** |
| [07 收尾与导出](./07-收尾与导出.md) | Finishing up | 背景色、背景音乐、死亡音效，**导出成 exe / 网页** | ✅ 成品 |

> **额外**：[00 核心概念地图](./00-核心概念地图.md) 是**只读**的一章，1 小时读完，能让你后面每章都"知道自己在干什么"。**强烈建议先读它。**
> 想了解工具链/插件/美术软件，看 [环境与工具生态](./环境与工具生态.md)。

---

## 2. 素材已经备好了（不用下载）

本仓库的 [素材/](./素材/) 目录里就是官方教程要用的全部素材：

```
godot/素材/
├─ art/
│  ├─ playerGrey_walk1.png  playerGrey_walk2.png   ← 玩家左右走（2 帧）
│  ├─ playerGrey_up1.png    playerGrey_up2.png     ← 玩家上下走（2 帧）
│  ├─ enemyFlyingAlt_1.png  enemyFlyingAlt_2.png   ← 敌人动画 1：fly
│  ├─ enemySwimming_1.png   enemySwimming_2.png    ← 敌人动画 2：swim
│  ├─ enemyWalking_1.png    enemyWalking_2.png     ← 敌人动画 3：walk
│  ├─ House In a Forest Loop.ogg                   ← 背景音乐
│  └─ gameover.wav                                 ← 死亡音效
└─ fonts/
   ├─ Xolonium-Regular.ttf                         ← UI 字体
   ├─ LICENSE.txt    （字体许可，保留）
   └─ FONTLOG.txt    （字体变更记录，保留）
```

**用法**：做 [01 章 §3](./01-项目设置.md) 时，把 `art/` 和 `fonts/` **两个目录整个复制**到你新建的 Godot 项目根目录下。就这一步，没有别的操作。

> **想从官方源头下载**（内容一样）：[dodge_the_creeps_2d_assets.zip](https://github.com/godotengine/godot-docs-project-starters/releases/download/latest-4.x/dodge_the_creeps_2d_assets.zip)
>
> **素材来源与授权**：
> - 图片、音频、字体来自官方素材包（[godot-docs-project-starters](https://github.com/godotengine/godot-docs-project-starters)）
> - 字体 Xolonium 的许可见 [素材/fonts/LICENSE.txt](./素材/fonts/LICENSE.txt)
> - **仅用于学习/原型没问题；商用前请自己复核每个文件的授权**

---

## 3. 环境准备（10 分钟，**这是唯一的"装软件"环节**）

### 3.1 下载 Godot

打开 [godotengine.org/download/windows](https://godotengine.org/download/windows/)，页面上有两个 Windows 包：

| 包 | 文件名特征 | 你该选哪个 |
|---|---|---|
| 标准版 | `Godot_v4.7.2-stable_win64.exe.zip` | 只写 GDScript 时 |
| **.NET 版** | `Godot_v4.7.2-stable_mono_win64.zip` | **想写 C# 就必须用它** |

> **建议直接下 .NET 版**：它包含标准版的全部功能，只是体积大一点。这样以后想切 C# 不用重装。

**解压到任意目录**（比如 `D:\Tools\Godot\`）。**Godot 是免安装的**——解压出来就是一个 exe，双击就跑，不写注册表、不需要管理员权限、不需要登录账号。

你会看到两个 exe：

| 文件 | 用途 |
|---|---|
| `Godot_v4.7.2-stable_mono_win64.exe` | **平时用这个**（图形界面） |
| `Godot_v4.7.2-stable_mono_win64_console.exe` | 命令行/抓崩溃日志用，平时不用管 |

### 3.2 首次启动 + 换成中文

1. **双击** `Godot_v4.7.2-stable_mono_win64.exe`
2. 首次打开是**项目管理器**（Project Manager）——你还没有任何项目，列表是空的
3. 换中文界面：菜单 **`Editor → Editor Settings`** → 左侧 `Interface → Editor` → **`Language`** 选 **`简体中文`**
4. 关掉设置窗口

> **本篇后面同时给出中文界面名和英文原名**（如「检查器（Inspector）」），因为搜索结果、官方文档、视频教程大多是英文。

### 3.3 写 C# 的话，还要装 .NET SDK（GDScript 路线跳到 §3.4）

.NET 版 Godot **只带运行游戏所需的 .NET 运行时，不带编译工具链**。打开 PowerShell 检查：

```powershell
dotnet --list-sdks
```

- **有输出**（版本 8.0 或更高）→ 没问题
- **没输出或报"找不到命令"** → 去 [dotnet.microsoft.com/download](https://dotnet.microsoft.com/download) 下载 **.NET SDK**（不是 Runtime！）安装

再装一个 C# 编辑器（可选但强烈建议）：**VS Code + C# 扩展**，或 Rider / Visual Studio。

### 3.4 环境检查清单

| 检查项 | 怎么确认 |
|---|---|
| Godot 能打开 | 双击 exe，出现项目管理器 |
| 界面是中文 | 菜单上写着「编辑器」「项目」 |
| （C# 路线）`dotnet --list-sdks` 有输出 | 在 PowerShell 里跑一次 |
| （C# 路线）确认是 .NET 版 | 新建项目时，语言下拉里**有 `C#` 选项**——标准版没有 |

---

## 4. 怎么用这套文档

### 4.1 推荐节奏

```
读 [00 核心概念地图]  ──  1 小时，只读不写，建立 Godot 的世界观
        ↓
[01] → [02] → [03] → [04] → [05] → [06] → [07]   一站到底
        ↓
对照官方原文检查（可选）：每章开头都有官方链接
```

**每一章的结构都是一样的**：

| 小节 | 内容 |
|---|---|
| 官方对应节 | 需要时点开看官方原文/截图 |
| **开始时 / 结束时你的状态** | 知道自己站在哪儿 |
| **逐步操作** | 精确到"点哪个菜单、填什么值" |
| **✅ 检查点** | 每做完几步，确认自己没走偏 |
| 代码（双语言） | 完整可复制，另有逐段讲解 |
| 和 Unity 对照 | 你带着 Unity 经验来时，哪里会撞墙 |
| 本章的坑 | 常见错误 → 原因 |
| ✅ 自检清单 | 全勾上再进下一章 |

### 4.2 语言怎么选（**先定，别中途换**）

| | GDScript | C# |
|---|---|---|
| 上手成本 | **零**（语法像 Python，且和引擎 API 结合最紧） | 你已会 C#，但要记 Godot 的 C# 规矩 |
| 官方示例 | **官方示例 95% 是 GDScript** | 官方有 [C# 版示例](https://github.com/godotengine/godot-demo-projects/tree/master/mono) |
| 改代码生效 | 保存即生效 | **必须点「Build」**（🔴 最容易忘的一步） |
| **导出 Web（网页）** | ✅ 可以 | ❌ **不行**（[07 章 §5](./07-收尾与导出.md)） |
| 其它平台 | 全平台 | 桌面全支持；Android/iOS 官方标注 experimental |

**建议**：**没有 C# 强需求就走 GDScript**（能省掉一整类"忘了 Build / 忘了 partial"的问题，而且能发网页）。
**你已会 C#、且不打算发网页** → 走 C#，跟每章的 C# 代码块。

> **一个节点只能挂一个脚本**，所以"双语言"= 你**选一条走完**，不是两条混着用。（想两条都试，就建两个项目各走一遍——本仓库的 [C# 版](./DodgeTheCreeps/) 和 [GDScript 版](./DodgeTheCreepsGD/) 就是这么来的。）

### 4.3 C# 路线：先把这 6 条记住

| # | 规矩 | 不遵守会怎样 |
|---|---|---|
| 1 | **改完代码点「Build」**（编辑器右上角） | 新增的 `[Export]` 变量和信号**不出现在 Inspector 里** |
| 2 | 类必须写 `public partial class X : Y` | 一堆编译错误 |
| 3 | `[Export]` **只能标属性**（`{ get; set; }`） | 不报错，但 Inspector 里没有 |
| 4 | 信号委托**必须以 `EventHandler` 结尾** | 引擎不认这个信号 |
| 5 | 编辑器里连信号时，**方法名要手打且完全正确**（`OnBodyEntered`，不是 `on_body_entered`） | 运行时才发现"方法不存在" |
| 6 | 调用 Godot 自带方法用**引擎的 snake_case 常量**（`Node.MethodName.QueueFree`） | 静默失败或报错 |

**命名规范**（官方约定）：

| | GDScript | C# |
|---|---|---|
| 类 / 节点 | `PascalCase` | 同左 |
| 变量 / 函数 | `snake_case` | **`PascalCase`** |
| 私有字段 | `_underscore` | `_camelCase` |

### 4.4 双语言速查小抄（写代码时随时翻回来）

| 想干什么 | GDScript | C# |
|---|---|---|
| 继承 | `extends Area2D`（第一行） | `public partial class Player : Area2D` |
| 导出到 Inspector | `@export var speed = 400` | `[Export] public int Speed { get; set; } = 400;` |
| 拿子节点 | `$AnimatedSprite2D` | `GetNode<AnimatedSprite2D>("AnimatedSprite2D")` |
| 缓存子节点 | `@onready var x = $Child` | 无，在 `_Ready()` 里 `GetNode` |
| 声明信号 | `signal hit` | `[Signal] public delegate void HitEventHandler();` |
| 发信号 | `hit.emit()` | `EmitSignal(SignalName.Hit);` |
| 连信号 | `node.hit.connect(_on_hit)` | `node.Hit += OnHit;` |
| 隐藏/显示 | `hide()` / `show()` | `Hide()` / `Show()` |
| 销毁自己 | `queue_free()` | `QueueFree()` |
| 打印 | `print(x)` | `GD.Print(x)` |
| 报错输出 | `push_error("...")` | `GD.PushError("...")` |
| 随机浮点 | `randf()` / `randf_range(a,b)` | `GD.Randf()` / `GD.RandRange(a,b)` |
| 随机整数 | `randi_range(a,b)` | `GD.RandRange(a,b)` |
| 等信号 | `await node.timeout` | `await ToSignal(node, Timer.SignalName.Timeout)` |
| 临时计时器 | `get_tree().create_timer(1.0)` | `GetTree().CreateTimer(1.0)` |
| 生命周期 | `_ready` / `_process` / `_physics_process` | `_Ready` / `_Process` / `_PhysicsProcess` |
| 判断对象有效 | `is_instance_valid(x)` | `GodotObject.IsInstanceValid(x)` |

> ⚠️ **生命周期函数名写错不会报错，只是永远不被调用**——这是最阴的一类 bug。GDScript 全小写、C# 首字母大写。

> 📌 上面的代码块以教程的**简化写法**为主；本仓库的 [GDScript 版成品项目](./DodgeTheCreepsGD/) 已经把代码升级为**全静态类型**（`class_name`、typed `@onready`、`PackedScene` + `as`、警告即错误）。两边的差异和进阶用法见 [GDScript 类型系统与进阶](./GDScript-类型系统与进阶.md)。

---

## 5. 官方资源（想深挖时用）

| 资源 | 链接 |
|---|---|
| **本教程官方原文**（7 节） | [Your first 2D game](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html) |
| 官方前置课（基础概念） | [Introduction](https://docs.godotengine.org/en/stable/getting_started/introduction/index.html) → [Step by step](https://docs.godotengine.org/en/stable/getting_started/step_by_step/index.html) |
| 官方 3D 版教程（同流程换维度） | [Your first 3D game](https://docs.godotengine.org/en/stable/getting_started/first_3d_game/index.html) |
| **官方成品源码 · GDScript** | [2d/dodge_the_creeps](https://github.com/godotengine/godot-demo-projects/tree/master/2d/dodge_the_creeps) |
| **官方成品源码 · C#** | [mono/dodge_the_creeps](https://github.com/godotengine/godot-demo-projects/tree/master/mono/dodge_the_creeps) |
| 官方全部示例（**MIT 授权**） | [godot-demo-projects](https://github.com/godotengine/godot-demo-projects) |
| 在线试玩官方所有示例 | [godotengine.github.io/godot-demo-projects](https://godotengine.github.io/godot-demo-projects/) |
| 类参考手册（查 API 用这个） | [Class reference](https://docs.godotengine.org/en/stable/classes/index.html) |
| C# 与 GDScript 的差异（C# 路线必读） | [C# API differences to GDScript](https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_differences.html) |

> **本仓库保留了两份练习成品**：[C# 版](./DodgeTheCreeps/) 和 [GDScript 版](./DodgeTheCreepsGD/)。需要最新官方源码时，直接点上面的链接看官方仓库。
> 想深入 GDScript 的静态类型、`Variant` 边界和性能，见 [GDScript 类型系统与进阶](./GDScript-类型系统与进阶.md)。
> 官方仓库分支：`master` 对应**下一个 4.x 开发版**，版本对齐分支最新到 `4.3`。你在 4.7.2 上用 `master`。

---

## 6. 关于"官方教程 vs 官方成品代码"的一个提醒

**官方教程正文和官方成品代码有几处不一致**（命名、参数值）。这不是你写错了，是两边各自演化导致的。

| 位置 | 教程正文 | 官方成品 |
|---|---|---|
| 玩家动画名 | `walk` | **`right`** |
| HUD 中间的 Label | `Message` | **`MessageLabel`** |
| HUD 字号 | `64` | **`60`** |
| Mob 的离屏回调名 | `_on_visible_on_screen_notifier_2d_screen_exited` | `_on_VisibilityNotifier2D_screen_exited` |

**铁律**：**名字以"你自己实际命名的"为准，脚本里必须完全一致（大小写敏感）**。不一致的后果是运行时报 `Node not found: xxx`——**不会在编辑期报错**。

本篇的处理：**统一用官方成品那套名字**（`right` / `MessageLabel`），并在每处标注教程正文的差异。

---

## 7. 附录：回合制 Roguelike（进阶）

[附录-回合制Roguelike/](./附录-回合制Roguelike/README-原Roguelike主线.md) 是一套**独立**的进阶内容：用 Godot 做一个 **8×8 回合制格子 Roguelike**。

它和官方入门教程是**互补**关系——里面这几个概念**官方入门教程完全不讲**：

| 概念 | 用在哪 |
|---|---|
| **Autoload** | 跨关卡单例（≈ Unity 的 `DontDestroyOnLoad`） |
| **`intersect_ray`** | 射线探测（≈ Unity 的 `Physics2D.Linecast`） |
| **Tween** | 补间动画（≈ 手写协程 / DOTween） |
| **`CharacterBody2D`** | 官方教程提到但没用的另一条角色路线 |
| **回合制状态机** | `await` + 状态位给轮询加锁 |

**建议**：**先把官方这 7 章做完**（你会掌握 Godot 的全套基础机制），再玩附录。反过来会有点吃力。

---

## 8. 来源与许可

| 内容 | 来源 | 许可 |
|---|---|---|
| 官方教程设计与原始文字出处 | [Godot 官方文档](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 示例代码（`player` / `mob` / `main` / `hud`） | [godot-demo-projects](https://github.com/godotengine/godot-demo-projects) | [MIT](https://github.com/godotengine/godot-demo-projects/blob/master/LICENSE.md) |
| 素材（`art/`、`fonts/`） | 官方素材包 | 见 [素材/fonts/LICENSE.txt](./素材/fonts/LICENSE.txt) |

**本篇的代码块源自官方示例（MIT），保留了原始英文注释；中文讲解、操作步骤与对照表为原创。**

---

准备好了 → 先读 [00 核心概念地图](./00-核心概念地图.md)，然后从 [01 项目设置](./01-项目设置.md) 开始动手。
