# 06 · HUD（分数、提示、Start 按钮）

> 官方对应节：[Heads up display](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/06.heads_up_display.html)
> **本章是最后一块拼图**：加上 UI 之后，整个游戏就闭环了（标题 → 开始 → 躲避 → 死亡 → 重开）。

---

## 0. 本章导航

| | |
|---|---|
| **开始时** | `main.tscn` 敌人能刷出来（[05 章](./05-主场景.md) 完成） |
| **结束时** | **`F5` 一个完整可玩的游戏**：分数、提示、Start 按钮、重开 |
| **耗时** | 40~50 分钟 |
| **产出** | `hud.tscn` + `hud.gd` / `HUD.cs`，并把 HUD 装进 `main.tscn` |

**最终结构**：

```
HUD (CanvasLayer)                 ← UI 层，永远画在游戏画面上方
├─ ScoreLabel (Label)             ← 分数，顶部居中
├─ MessageLabel (Label)           ← 提示/标题，屏幕正中
├─ StartButton (Button)           ← 开始按钮，底部居中
└─ MessageTimer (Timer)           ← 控制提示显示多久
```

---

## 1. 新建场景 + 选根节点

1. `场景 → 新建场景`
2. `Ctrl+A` → 搜索 **`CanvasLayer`** → 创建
3. 改名 **`HUD`**

**`HUD` 是什么**：heads-up display（抬头显示），就是"**叠在游戏画面上的信息层**"。

官方对 `CanvasLayer` 的解释（翻译）：

> `CanvasLayer` 节点让我们**把 UI 元素画在游戏其余部分之上的一层**，这样它显示的信息就不会被玩家或敌人之类的游戏元素挡住。

| | Unity | Godot |
|---|---|---|
| UI 层 | `Canvas`（`Screen Space - Overlay`） | **`CanvasLayer` 节点** |
| UI 元素 | 必须是 Canvas 的子物体 | 必须是 `Control` 系节点（`Label` / `Button` / `TextureRect`…） |

> **`CanvasLayer` 的特殊之处**：它**脱离世界坐标系**——相机怎么移动、缩放，UI 都稳稳贴在屏幕上。所以 UI 一定要放进它里面，**否则相机一动 UI 就跟着跑**。

---

## 2. 加 4 个子节点

选中 `HUD`，逐个 `Ctrl+A` 添加：

| 节点名 | 类型 | 作用 |
|---|---|---|
| `ScoreLabel` | `Label` | 显示分数 |
| **`MessageLabel`** | `Label` | 显示"Get Ready" / "Game Over" / 游戏标题 |
| `StartButton` | `Button` | 开始按钮 |
| `MessageTimer` | `Timer` | 控制 Message 显示多久 |

> ⚠️ **又一处"官方教程 vs 官方成品"的不一致**：
>
> | | 官方教程正文 | 官方成品 |
> |---|---|---|
> | 中间那个 Label | **`Message`** | **`MessageLabel`** |
> | 字号 | `64` | `60` |
> | `MessageTimer.Wait Time` | `2` | 未设（默认 1） |
>
> **本篇统一用 `MessageLabel`**（和官方成品一致，代码也按这个写）。
> **如果你跟着官方教程正文起名 `Message`**，那代码里的 `$MessageLabel` 就要改成 `$Message`。
>
> **命名不一致的后果是实打实的**：教程版代码写 `$Message.text`，成品版写 `$MessageLabel.text`。**你选了哪个名字，代码里就得用哪个**，否则运行时报 `Node not found: Message`。

---

## 3. 设置字体（`Control` 默认字体太小）

官方原话（翻译）：

> `Control` 节点的**默认字体很小，而且缩放效果不好**。游戏素材里有一个字体文件 `Xolonium-Regular.ttf`。

### 3.1 对三个文字节点都做一遍

**对 `ScoreLabel`、`MessageLabel`、`StartButton` 各做一次**：

| 步骤 | 操作 |
|---|---|
| 1 | 选中节点 → 检查器里找到 **`主题覆盖 (Theme Overrides)`** 分组 |
| 2 | 展开 **`字体 (Fonts)`** → 点 `[empty]` → **「加载 (Load)」** → 选 `fonts/Xolonium-Regular.ttf` |
| 3 | 展开 **`字体大小 (Font Sizes)`** → 把 `字体大小 (Font Size)` 设成 **`64`**（成品是 `60`，都行） |

### 3.2 ✅ 检查点

- 三个节点的文字**明显变大了**，而且是 Xolonium 那种科技感字体
- 如果字还是很小 → 说明"字体大小"没设（只换了字体，字号还是默认的 16）

> **对照 Unity**：Unity 里换字体要建 Font Asset（TextMeshPro 还得生成字符图集），中文字体更麻烦。
> Godot 里就是"**拖一个 TTF 到主题覆盖**"。
> ⚠️ 但注意：**Godot 4 的默认字体不含中文字形**——要显示中文仍需自己提供一个中文 TTF。本项目 UI 全是英文，不受影响。

---

## 4. 排布三个元素（锚点）

官方对锚点的解释（翻译）：

> `Control` 节点有位置和大小，但它们还有**锚点（Anchors）**。**锚点定义了原点——即节点各边的参考点。**

**锚点预设的操作入口**：选中 `Control` 节点，切换到 **2D** 视图，在视口上方的工具栏打开 **「布局 (Layout)」** 菜单 → **「锚点预设 (Anchors Preset)」**，再选需要的预设（如 `Center Top`）。检查器里的「布局」属性可以查看或编辑锚点和偏移，但预设菜单在 2D 视口工具栏中。

**理解锚点的两个数字**：

```
Control
├─ 锚点 (Anchors)：0~1 的比例，"相对父容器" —— 决定"钉在屏幕的哪个位置"
└─ 偏移 (Offsets)：像素值，"相对锚点"     —— 决定"离那个位置多远"
```

### 4.1 `ScoreLabel`（分数，顶部）

| 设置 | 值 |
|---|---|
| `文本 (Text)` | **`0`** |
| `水平对齐 (Horizontal Alignment)` | **`居中 (Center)`** |
| `垂直对齐 (Vertical Alignment)` | **`居中 (Center)`** |
| **锚点预设** | **`Center Top`（居中顶部）** |

### 4.2 `MessageLabel`（提示/标题，正中）

| 设置 | 值 |
|---|---|
| `文本 (Text)` | **`Dodge the Creeps!`** |
| `水平对齐` / `垂直对齐` | 都 **`居中`** |
| **`自动换行模式 (Autowrap Mode)`** | **`Word`** ← 官方原话：*"否则这个 Label 会一直挤在一行里"* |
| `布局 → 变换 → 大小 X (Size X)` | **`480`**（用满屏幕宽度） |
| **锚点预设** | **`Center`（居中）** |

### 4.3 `StartButton`（按钮，底部）

| 设置 | 值 |
|---|---|
| `文本 (Text)` | **`Start`** |
| `大小 X (Size X)` | **`200`** |
| `大小 Y (Size Y)` | **`100`** |
| **锚点预设** | **`Center Bottom`（居中底部）** |
| `位置 Y (Position Y)` | **`580`** |

官方对 `Size X/Y` 的解释（翻译）：*"在边框和文字之间留点内边距。"*

> 💡 **官方成品用的是另一种设置方式**：锚点 `Center Bottom` + `偏移 上 = -200`、`偏移 下 = -100`——效果是"**高 100 像素、离底部 200 像素**"。
> **两种都能用**，成品那种在窗口尺寸变化时更稳（因为它是"从底部往上算"）。
> 成品还额外给按钮加了 **`快捷键 (Shortcut)`**：新建一个 `InputEventAction`（动作名 `start_game`）——这样**键盘/手柄也能触发按钮**，不只是鼠标点击。

### 4.4 ✅ 检查点

2D 视图里（或者运行时）三个元素的位置：

```
┌─────────────────────┐
│         0           │  ← ScoreLabel（顶部居中）
│                     │
│   Dodge the Creeps! │  ← MessageLabel（正中）
│                     │
│                     │
│      [ Start ]      │  ← StartButton（底部居中，离底 200px → y≈580）
└─────────────────────┘
```

---

## 5. 设置 `MessageTimer`

| 属性 | 值 |
|---|---|
| `等待时间 (Wait Time)` | **`2`** |
| **`单次 (One Shot)`** | **勾上** |

**为什么 `One Shot`**：它只负责"显示 2 秒后隐藏"，不需要周期性地重复触发。

---

## 6. 挂脚本 + 写代码

1. 选中 `HUD` → 「附加脚本」→ 文件名 **`hud.gd`**（C#：选语言后 `HUD.cs`）
2. 内容整体替换成下面的代码

### 6.1 GDScript —— `hud.gd`

```gdscript
extends CanvasLayer

signal start_game

func show_message(text):
	$MessageLabel.text = text
	$MessageLabel.show()
	$MessageTimer.start()

func show_game_over():
	show_message("Game Over")
	await $MessageTimer.timeout
	$MessageLabel.text = "Dodge the\nCreeps"
	$MessageLabel.show()
	await get_tree().create_timer(1).timeout
	$StartButton.show()

func update_score(score):
	$ScoreLabel.text = str(score)

func _on_StartButton_pressed():
	$StartButton.hide()
	start_game.emit()

func _on_MessageTimer_timeout():
	$MessageLabel.hide()
```

### 6.2 C# —— `HUD.cs`

```csharp
using Godot;

public partial class HUD : CanvasLayer
{
    [Signal]
    public delegate void StartGameEventHandler();

    public void ShowMessage(string text)
    {
        var messageLabel = GetNode<Label>("MessageLabel");
        messageLabel.Text = text;
        messageLabel.Show();

        GetNode<Timer>("MessageTimer").Start();
    }

    public async void ShowGameOver()
    {
        ShowMessage("Game Over");

        var messageTimer = GetNode<Timer>("MessageTimer");
        await ToSignal(messageTimer, Timer.SignalName.Timeout);

        ShowMessage("Dodge the\nCreeps!");
        await ToSignal(GetTree().CreateTimer(1.0), SceneTreeTimer.SignalName.Timeout);

        GetNode<Button>("StartButton").Show();
    }

    public void UpdateScore(int score)
    {
        GetNode<Label>("ScoreLabel").Text = score.ToString();
    }

    public void OnStartButtonPressed()
    {
        GetNode<Button>("StartButton").Hide();
        EmitSignal(SignalName.StartGame);
    }

    public void OnMessageTimerTimeout()
    {
        GetNode<Label>("MessageLabel").Hide();
    }
}
```

> 🔴 **C# 路线：点「Build」**。官方教程在这里专门加了一句注释（翻译）：
> *"**别忘了重新构建项目，这样编辑器才知道这个新信号。**"* —— 说的就是 `[Signal] StartGameEventHandler`。

---

## 7. 连 `HUD` 内部的 2 条信号

| # | 从 | 信号 | 到 | 接收方法（GDScript / C#） |
|---|---|---|---|---|
| 1 | `StartButton` | `pressed` | `HUD` | `_on_StartButton_pressed` / `OnStartButtonPressed` |
| 2 | `MessageTimer` | `timeout` | `HUD` | `_on_MessageTimer_timeout` / `OnMessageTimerTimeout` |

**操作**：选中发出信号的节点 → 右侧「**节点**」面板 → 「**信号**」标签 → 双击信号 → 接收节点选 **`HUD`** → 填方法名 → 「连接」。

保存 `hud.tscn`（`Ctrl+S`）。

---

## 8. 把 HUD 装进 `main.tscn`

1. 打开 **`main.tscn`**
2. 选中 `Main` 节点
3. 点工具栏的 **「实例化子场景」**（链环图标）→ 选 **`hud.tscn`**
4. 改名为 **`HUD`**（**必须叫 `HUD`**，因为 `main.gd` 里是 `$HUD`）
5. **把 `HUD` 节点拖到子节点列表的最后**（保证它画在最上面）

### 8.1 连最后一条信号

`HUD` 的 `start_game` 信号（我们在 `hud.gd` 里自定义的）→ `Main` 的 `new_game`：

| 从 | 信号 | 到 | 接收方法 |
|---|---|---|---|
| `HUD` | **`start_game`** | `Main` | **`new_game` / `NewGame`** |

**操作**：选中 `HUD` → 「节点」面板 → 双击 `start_game` → 接收节点选 **`Main`** → 方法名填 **`new_game`**（GDScript）/ **`NewGame`**（C#）→ 「连接」。

> ⚠️ **如果 `start_game` 不在信号列表里**：**C# 路线** 99% 是忘了 Build；GDScript 检查 `signal start_game` 那行。

### 8.2 ✅ 此时 `main.tscn` 的完整结构

```
Main (Node)                        [main.gd]
├─ ColorRect                        （07 章加）
├─ Player                           （实例化自 player.tscn）
├─ MobTimer (Timer)                 0.5 秒
├─ ScoreTimer (Timer)               1 秒
├─ StartTimer (Timer)               2 秒，One Shot
├─ StartPosition (Marker2D)         (240, 450)
├─ MobPath (Path2D)
│  └─ MobSpawnLocation (PathFollow2D)
├─ HUD                              （实例化自 hud.tscn）
├─ Music (AudioStreamPlayer)        （07 章加）
└─ DeathSound (AudioStreamPlayer)   （07 章加）
```

**信号连接**（`main.tscn` 里应该有 5 条）：

```
[connection signal="hit"       from="Player"     to="." method="game_over"]
[connection signal="timeout"   from="MobTimer"   to="." method="_on_MobTimer_timeout"]
[connection signal="timeout"   from="ScoreTimer" to="." method="_on_ScoreTimer_timeout"]
[connection signal="timeout"   from="StartTimer" to="." method="_on_StartTimer_timeout"]
[connection signal="start_game" from="HUD"       to="." method="new_game"]
```

---

## 9. 取消 [05 章](./05-主场景.md) 的临时注释

如果你在 [05 章 §8](./05-主场景.md#8-临时验证可选但推荐现在做一次) 注释掉了几行，**现在把它们恢复**：

- `$HUD.show_game_over()` / `$HUD.update_score(score)` / `$HUD.show_message("Get Ready")`
- `$HUD` 的对应 C# 行
- 删掉临时加的 `print("Score: ", score)` / `GD.Print(...)`

**`$Music` / `$DeathSound` 那两行先留着注释** —— 它们是 [07 章](./07-收尾与导出.md) 的节点。

---

## 10. 运行验证（**完整可玩了！**）

按 **`F5`**。

### 10.1 完整流程验收

| # | 应该发生什么 | 对应章节 |
|---|---|---|
| 1 | 显示 **`Dodge the Creeps!`** 标题和 **`Start`** 按钮 | 06 |
| 2 | **点 `Start`** → 标题消失 → 显示 **`Get Ready`** | 05 / 06 |
| 3 | 2 秒后 `Get Ready` 消失，**玩家在屏幕下方中央出现** | 03 / 05 |
| 4 | 按方向键能移动，动画正确切换 | 03 |
| 5 | 敌人**从屏幕四边不断涌进来**，朝屏幕内部随机方向飞 | 04 / 05 |
| 6 | 分数**每秒 +1** | 05 |
| 7 | 敌人飞出屏幕后**消失**（不会越积越多变卡） | 04 |
| 8 | 撞到敌人 → 玩家消失 → 显示 **`Game Over`** | 03 / 06 |
| 9 | 2 秒后标题重新出现，再过 1 秒 **`Start` 按钮**出现 | 06 |
| 10 | **再点 `Start`** → 旧敌人**全部清空**、分数归零、玩家回起点 | 05 |

**10 项全过 → 你已经用 Godot 做出了一个完整的游戏。** 🎉

---

## 11. 逐段讲解

### 11.1 `signal start_game`：HUD 唯一要说的话

```gdscript
signal start_game
...
func _on_StartButton_pressed():
	$StartButton.hide()
	start_game.emit()
```

**HUD 不知道游戏怎么开始、也不知道谁是 `Main`**。它只做两件事：把自己藏起来、喊一声"有人想开始了"。

**"游戏怎么开始"的逻辑在 `main.gd` 的 `new_game()` 里**——通过**编辑器连线**接上：

```
StartButton.pressed
   → HUD._on_StartButton_pressed()     （按钮藏起来）
      → HUD.start_game.emit()          （广播）
         → Main.new_game()             （真正开始）
```

> **这就是"关注点分离"**：UI 只管 UI，流程只管流程，两边靠**一根信号线**连接。
> **对照 Unity**：常见写法是 `Button.onClick.AddListener(() => GameManager.instance.NewGame())`——**UI 脚本里得知道 `GameManager`**。**Godot 里 UI 谁都不用知道。**

### 11.2 `show_message()`：给 `Main` 调用的"接口"

```gdscript
func show_message(text):
	$MessageLabel.text = text
	$MessageLabel.show()
	$MessageTimer.start()
```

配合：

```gdscript
func _on_MessageTimer_timeout():
	$MessageLabel.hide()
```

**效果**：文字显示 `MessageTimer.Wait Time`（2 秒）后自动隐藏。

> **为什么用 `show()` / `hide()` 而不是清空文字**：`hide()` 只是"不可见"，**文字还在**——这样"Get Ready"消失后，标题文字还能被 `show_game_over()` 复用。

### 11.3 `show_game_over()`：`await` 的最佳示例（**本节精华**）

```gdscript
func show_game_over():
	show_message("Game Over")                          # ① 显示 "Game Over"（同时启动 2 秒计时器）
	await $MessageTimer.timeout                        # ② 等这 2 秒过去
	$MessageLabel.text = "Dodge the\nCreeps"           # ③ 换成游戏标题
	$MessageLabel.show()
	await get_tree().create_timer(1).timeout           # ④ 再等 1 秒
	$StartButton.show()                                # ⑤ 让 Start 按钮出现
```

**四步是按顺序"读下来"的**——这就是 `await` 的价值。

| 写法 | 代码形态 |
|---|---|
| **`await`**（官方选的） | 从上到下一行行读，**流程一目了然** |
| 计时器 + 回调 | 拆成 `_on_timer1_timeout` → `_on_timer2_timeout`，**逻辑散在几个函数里** |
| 手写计时变量 | `if elapsed > 1.0: ...`，**状态机自己维护** |

**两种 `await` 的细微差别**（值得体会）：

| 写法 | 等的是什么 | 谁在计时 |
|---|---|---|
| `await $MessageTimer.timeout` | **节点上那个 `Timer`** 的信号 | 复用 `MessageTimer`（用它设的 2 秒） |
| `await get_tree().create_timer(1).timeout` | **临时创建一个计时器** | 一次性、用完就丢，**不用在场景里加节点** |

> **`get_tree().create_timer(秒)` 是"临时计时器"**：不用在场景树里摆 `Timer` 节点，适合"就地等一会儿"。**要周期性重复还是用 `Timer` 节点。**

**`await` 之后发生了什么**：函数**暂停在这里**，把控制权还给引擎；等信号发出后**从下一行继续**。所以：
- `show_game_over()` 被调用后**立刻返回**（不会卡住游戏）；
- 但**后面的代码会在将来继续执行**——那几行必须在"玩家还在、按钮还在"的前提下才安全。

> ⚠️ **C# 的 `async void`**：`public async void ShowGameOver()`。`async void` 通常被认为有害（异常无法捕获），但**在 Godot 里这是官方推荐写法**——因为它等价于"**启动一个和信号绑定的异步流程**"。

### 11.4 `update_score()`

```gdscript
func update_score(score):
	$ScoreLabel.text = str(score)
```

**`str(score)` 是必须的**——`Label.text` 是**字符串**（`String`），不是数字。

> **GDScript 的隐式转换有时很宽松**，但有些地方不行；**C# 更严格**（官方写 `score.ToString()`）。
> **养成显式转换的习惯**，能省掉一类"显示成奇怪内容"的问题。

---

## 12. 和 Unity 的对照小结

| 概念 | Unity | Godot |
|---|---|---|
| UI 层 | `Canvas`（Overlay） | **`CanvasLayer`** |
| 换字体 | 建 Font Asset（TMP 还要生成图集） | **主题覆盖 → 加载 TTF** |
| 字号 | `fontSize` | **主题覆盖 → Font Sizes** |
| 文本换行 | TMP 的 `Word Wrapping` | **`Autowrap Mode = Word`** |
| 位置 | `RectTransform` 的 Anchor + Left/Top/Right/Bottom | **`Control` 的 锚点 + 偏移** |
| 显示/隐藏 | `SetActive(false)` | **`hide()` / `show()`** |
| 按钮点击 | `onClick.AddListener(...)` | **`pressed` 信号** |
| 通知别人 | 直调单例 / `UnityEvent` | **自定义信号 `start_game` + `.emit()`** |
| 延迟流程 | 协程 `IEnumerator` + `yield` | **`await`（语言原生语法）** |
| 临时计时 | `new WaitForSeconds(t)` | **`get_tree().create_timer(t)`** |

---

## 13. 本章的坑

| 现象 | 原因 |
|---|---|
| `Node not found: MessageLabel` | **节点名不一致**（`Message` vs `MessageLabel`）——改成一致 |
| 文字小到看不清 | 只换了字体、**没设「主题覆盖 → 字体大小」** |
| 中间文字挤成一行、超出屏幕 | `Autowrap Mode` 没设成 `Word`，或 `Size X` 不是 480 |
| UI 被玩家/敌人挡住 | 根节点不是 `CanvasLayer`；或 `HUD` 没排在 `main.tscn` 子节点**最后** |
| 点 Start 没反应 | ① `StartButton.pressed` 没连 ② `HUD.start_game` 没连到 `Main.new_game` |
| "Game Over" 后按钮不出现 | `show_game_over()` 的 `await` 链断了（某个节点名写错会中断）——看「输出」面板的报错 |
| 分数不更新 | `ScoreTimer.timeout` 没连，或 `update_score` 里忘了 `str()` |
| `Game Over` 了还在刷怪 | `game_over()` 里的 `.stop()` 漏了 |
| **C# 里看不到 `start_game` 信号** | **忘了点「Build」** |
| C# 编译警告 CS1998 | `async void` 里没有任何 `await`——检查 `await ToSignal(...)` 是否都在 |

---

## 14. ✅ 自检清单（全勾上再进最后一章）

- [ ] `hud.tscn` 根节点是 `CanvasLayer`、名字 `HUD`
- [ ] 4 个子节点：`ScoreLabel` / `MessageLabel`（或 `Message`）/ `StartButton` / `MessageTimer`
- [ ] 三个文字节点都设了 **Xolonium 字体 + 字体大小**
- [ ] 锚点：分数 `Center Top`、消息 `Center`（`Autowrap = Word`、`Size X = 480`）、按钮 `Center Bottom`
- [ ] `MessageTimer`：`One Shot` **勾上**
- [ ] `HUD` 内部 2 条信号已连（`pressed`、`timeout`）
- [ ] `hud.tscn` 已**实例化**进 `main.tscn`、节点名是 **`HUD`**、排在子节点**最后**
- [ ] `HUD.start_game → Main.new_game` 已连
- [ ] [05 章](./05-主场景.md) 的临时注释**已恢复**（除了 `$Music` / `$DeathSound`）
- [ ] 🔴 **`F5` 后 [§10.1](#101-完整流程验收) 的 10 项验收全部通过**

---

**下一章**：[07 收尾与导出](./07-收尾与导出.md) —— 背景、音乐、音效，以及**导出成 exe / 网页**。
**官方对应节**：[Finishing up](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/07.finishing-up.html)
