# 3D 基础与 Blender 游戏资产实战

> **从 AI 生成的模型，到 Godot 里能跑、能打、能上线的游戏资产。**
>
> - **面向**：零 3D 基础、已经会一点 Godot / 编程的独立开发者
> - **软件**：Blender **5.2**（2026-10 当前稳定版）或 **4.5 LTS**；Godot **4.x**
> - **用法**：先读第 0～2 章（约 1.5 小时），再跟着第 9 章完整做一遍；第 3～8 章当手册随时查
> - **目标**：2 周入门，21 天形成稳定的资产管线；之后靠刻意练习变熟练

---

## 目录

- [0. 先看结论：AI 模型不是游戏资产](#0-先看结论ai-模型不是游戏资产)
- [1. 3D 基础：只学够用的](#1-3d-基础只学够用的)
- [2. AI 生成 3D：把它当“数字黏土”](#2-ai-生成-3d把它当数字黏土)
- [3. Blender 快速上手](#3-blender-快速上手)
- [4. 清理与重拓扑](#4-清理与重拓扑)
- [5. UV 展开](#5-uv-展开)
- [6. 材质与贴图](#6-材质与贴图)
- [7. 骨骼、蒙皮与动画](#7-骨骼蒙皮与动画)
- [8. 导出到 Godot](#8-导出到-godot)
- [9. 实战：混元 3D 模型到 Godot 道具](#9-实战混元-3d-模型到-godot-道具)
- [10. 21 天训练计划](#10-21-天训练计划)
- [11. 常见问题 FAQ](#11-常见问题-faq)
- [12. 速查卡](#12-速查卡)
- [13. 资源与继续学习](#13-资源与继续学习)
- [附录 A. 术语中英对照](#附录-a-术语中英对照)
- [附录 B. 资产规格模板](#附录-b-资产规格模板)

---

## 0. 先看结论：AI 模型不是游戏资产

### 0.1 AI 输出 vs 游戏需要

AI 生成的是**高精度的“数字黏土”**，不是可以直接进引擎的资产。两者差在下面这些地方：

| AI 通常给你 | 游戏实际需要 |
|---|---|
| 几万到几十万个三角面，通常是三角面高模 | 几千到几万个三角面，且有合理拓扑 |
| 自动生成的 UV，可能重叠、拉伸 | 规范 UV，纹素密度合理，接缝藏在隐蔽处 |
| 一张或多张烘焙好的贴图 | PBR 通道齐全，材质数量少，贴图尺寸受控 |
| 任意尺度、任意朝向 | 统一单位（1 单位 = 1 米）、统一朝向、原点在脚底/底部 |
| 多个松散部件、底座、背景 | 合并或分离清楚的部件，无多余物体 |
| 不封闭、破面、内部面、法线混乱 | 流形网格、法线朝外、无重叠面 |
| 没有骨骼、没有动画 | 骨骼、蒙皮权重、动画剪辑、root motion |
| 没有碰撞、没有 LOD | 碰撞体、LOD、阴影网格 |

> **一句话**：AI 负责“想出形状”，Blender 负责“把它变成能进游戏的工程件”。

### 0.2 三条铁律

不管你做静态道具还是角色，先记住这三条，能避开 80% 的返工：

1. **缩放必须应用**：Object Mode → `Ctrl+A` → `Scale`。
2. **法线必须朝外**：Edit Mode → 全选 → `Shift+N`（Recalculate Outside）。
3. **单位与朝向必须统一**：Blender 是 **Z 轴向上、-Y 朝前**；glTF / Godot 是 **Y 轴向上、-Z 朝前**。导出时勾选 `+Y Up`，让转换自动完成。

### 0.3 两条路线，先选一条

| 路线 | 适用 | 核心步骤 | 第一次预计 |
|---|---|---|---|
| **静态道具** | 箱子、石灯、武器、家具、场景摆件 | 导入 → 清理 → 减面 → UV → 材质 → 原点 → 导出 | 30～60 分钟/个 |
| **角色** | 有骨骼、会动的角色 | 重拓扑 → UV → 烘焙 → 骨骼 → 权重 → 动画 → 导出 | 1～3 天/个 |

**不要一上来做角色。** 先用 3～5 个静态道具把管线跑通，再碰骨骼。

### 0.4 你需要建立的判断力

- 面数不是唯一标准：**剪影、拓扑、UV、材质、动画**缺一不可。
- 游戏资产不是“越精细越好”，而是“**在目标平台上看起来够好、跑得够快**”。
- AI 生成结果**必须验收**，不能默认它是对的；背面、内部、UV、法线经常是坏的。

### 0.5 只有两小时？按这个顺序

| 时间 | 做什么 | 对应章节 |
|---|---|---|
| 0:00～0:20 | 读 3D 核心概念，建立坐标系/拓扑/UV/材质的心智模型 | [1.1～1.7](#11-一个模型由什么组成) |
| 0:20～0:50 | Blender 导航 + 做一个带倒角的箱子 | [3.3～3.9](#33-视图导航先学会看) |
| 0:50～1:40 | 完整走一遍 AI 模型 → 清理 → UV → 材质 → 导出 | [第 9 章](#9-实战混元-3d-模型到-godot-道具) |
| 1:40～2:00 | 导入 Godot，检查比例/朝向/材质/碰撞 | [8.3～8.6](#83-godot-导入设置) |

> 没有现成的 AI 模型，就先用 3.9 的箱子，从 9.6 开始走导出和 Godot 验证。

---

## 1. 3D 基础：只学够用的

### 1.1 一个模型由什么组成

| 概念 | 英文 | 你可以这样理解 |
|---|---|---|
| 顶点 | Vertex | 空间中的一个点 |
| 边 | Edge | 两个顶点之间的连线 |
| 面 | Face | 三条或更多边围成的表面 |
| 网格 | Mesh | 顶点、边、面组成的整体 |
| 法线 | Normal | 每个面/顶点“朝外”的方向，决定光照和正反面 |
| UV | UV Coordinates | 把 3D 表面“摊平”到 2D 贴图上的坐标 |
| 材质 | Material | 表面如何反光、什么颜色、是否透明 |
| 贴图 | Texture | 贴在材质上的图片（颜色、法线、粗糙度等） |
| 骨骼 | Armature / Bones | 控制模型变形的骨架 |
| 权重 | Weight | 每根骨骼对每个顶点的影响程度 |
| 变换 | Transform | 位置（Location）、旋转（Rotation）、缩放（Scale） |
| 原点 | Origin | 物体的“把手”，决定移动、旋转、缩放的基准点 |

### 1.2 坐标系与朝向：最容易踩的坑

Blender 和游戏引擎的轴向不一样：

```
Blender（右手系，Z 向上）          glTF / Godot（右手系，Y 向上）
        Z                                 Y
        │                                 │
        │                                 │
        └──── Y                           └──── Z
       /                                 /
      X                                 X

Blender：+Z 上，-Y 前              Godot：+Y 上，-Z 前
```

- **Blender 里建模时，让角色/道具的“正面”朝向 -Y**。
- 导出 glTF 时保持 **`+Y Up` 勾选**，Blender 会自动把 Z-up 转成 Y-up。
- 到 Godot 里，模型正面就会朝向 **-Z**，和 `Camera3D`、`CharacterBody3D` 的前方一致。
- **单位**：Blender 默认 1 单位 = 1 米；Godot 默认 1 单位 = 1 米。不要改，保持一致。

> 如果导入 Godot 后发现模型“躺着”或“背对镜头”，先检查导出时的 `+Y Up` 和 Blender 里的朝向，不要急着重做。

### 1.3 变换与原点

| 操作 | 说明 | 为什么重要 |
|---|---|---|
| Location | 物体位置 | 导出后节点位置 |
| Rotation | 物体旋转 | 朝向、动画、绑定 |
| Scale | 物体缩放 | **非均匀缩放是万恶之源** |
| Apply Scale | `Ctrl+A` → `Scale` | 让缩放变成 1,1,1，避免法线/修改器/物理/蒙皮出错 |
| Origin | 物体原点 | 角色原点放脚底，道具放底部中心，门放铰链处 |

**非均匀缩放会导致**：

- 法线方向错误，光照发黑/发亮；
- 修改器（Bevel、Solidify、Boolean）厚度不一致；
- 骨骼蒙皮被拉歪；
- 物理碰撞尺寸和视觉不一致；
- UV 和贴图被拉伸。

**正确习惯**：建模时尽量在 Object Mode 用 `S` 缩放后立刻 `Ctrl+A` → `Scale`；或者进入 Edit Mode 直接缩放顶点。

### 1.4 网格质量：什么叫“拓扑好”

| 概念 | 说明 | 游戏里的要求 |
|---|---|---|
| 三角面 Triangle | 三条边的面 | 引擎最终都按三角面渲染；静态道具可以接受 |
| 四边面 Quad | 四条边的面 | 角色、需要变形的部位优先 |
| 多边形 N-gon | 五条边以上 | 尽量避免，容易在引擎三角化时出错 |
| 流形 Manifold | 每条边正好连接两个面，没有破洞/内部面 | 角色和需要物理碰撞的资产尽量流形 |
| 非流形 Non-manifold | 破洞、孤立边、内部面、重叠面 | 会导致法线、烘焙、碰撞、打印出问题 |
| 法线 Normal | 面朝外的方向 | 必须统一朝外 |
| 边环 Edge Loop | 一圈连续的边 | 关节处需要，方便变形和加线 |
| 重叠面 Overlapping Faces | 两个面在同一位置 | 会闪烁（Z-fighting）、烘焙出错 |

**快速检查**：

- Edit Mode → `Select > All by Trait > Non Manifold`：选中非流形边。
- Edit Mode → `Select > All by Trait > Interior Faces`：选中内部面。
- Edit Mode → `Mesh > Clean Up > Delete Loose`：删除孤立点/边。
- `Shift+N`：重算法线朝外。
- 打开 **Face Orientation** 叠加层（Viewport Overlays → Face Orientation）：蓝色朝外，红色朝内。

**拓扑好坏的直观标准**：

- 剪影正确；
- 没有明显破面/黑斑；
- 关节处有足够的环线；
- 面密度均匀，不在小角落堆几万个面；
- 静态道具允许三角面，角色变形区域尽量四边面。

### 1.5 UV：把 3D 表面摊平

UV 是“每个顶点在贴图上的 2D 坐标”。没有 UV，贴图就不知道往哪儿贴。

- **接缝 Seam**：你人为切开网格的边，展开时从这里“剪开”。
- **UV 岛 Island**：切开后摊平的一块块区域。
- **纹素密度 Texel Density**：单位长度上有多少像素。密度不一致，贴图就会有的地方糊、有的地方清晰。
- **重叠 UV**：两个面共用同一块 UV。镜像部件可以共用，但**光照贴图（Lightmap）需要不重叠的 UV2**。

**经验值**：

| 平台 | 推荐纹素密度 | 贴图尺寸 |
|---|---|---|
| 移动端 | 256～512 px/m | 512～1024 |
| PC 普通 | 512～1024 px/m | 1024～2048 |
| PC 主角/特写 | 1024～2048 px/m | 2048～4096 |

### 1.6 材质与 PBR

现代游戏材质基本都遵循 **PBR（基于物理的渲染）**。Blender 里用 **Principled BSDF**，Godot 里对应 **StandardMaterial3D**。

| 通道 | 英文 | 作用 | 色彩空间 |
|---|---|---|---|
| 基础色 | Base Color / Albedo | 表面颜色 | **sRGB** |
| 金属度 | Metallic | 0=非金属，1=金属 | Non-Color |
| 粗糙度 | Roughness | 0=镜面，1=完全粗糙 | Non-Color |
| 法线 | Normal | 表面凹凸细节（不改变几何） | Non-Color |
| 环境光遮蔽 | AO | 缝隙变暗 | Non-Color |
| 高度 | Height / Displacement | 视差/置换 | Non-Color |
| 自发光 | Emission | 发光颜色 | sRGB |
| 透明度 | Alpha | 透明程度 | Non-Color |
| ORM | Occlusion/Roughness/Metallic | R=AO，G=Roughness，B=Metallic 的打包图 | Non-Color |

**色彩空间是新手最容易错的地方**：颜色贴图用 sRGB，数据贴图（法线、粗糙度、金属度、AO）必须设为 **Non-Color**，否则数值会被 gamma 曲线扭曲。

**透明模式**（Godot）：

- `Opaque`：不透明，性能最好；
- `Alpha Scissor`：二值透明，适合树叶、破布；
- `Alpha Blend`：半透明，排序问题多，尽量少用。

### 1.7 骨骼、蒙皮与动画

- **Armature**：骨架对象，里面有很多 Bone。
- **蒙皮 Skinning**：把网格顶点绑定到骨骼上。
- **权重 Weight**：每个顶点受哪几根骨骼影响、影响多少。所有权重应归一化到 1。
- **T-pose / A-pose**：角色绑定前的标准姿势。Mixamo 一般要求 T-pose。
- **关键帧 Keyframe**：在时间线上记录某个属性（位置/旋转/缩放）的值。
- **循环 Loop**：首尾帧一致，动画才能无缝循环。
- **Root Motion**：把位移烘焙到根骨骼上，让角色“真正”向前走，而不是原地滑步。

**游戏里的权重原则**：

- 每个顶点最多受 **4 根骨骼**影响（移动端常用上限；PC 可放宽，但没必要）；
- 权重必须归一化；
- 关节处要有足够的环线，否则弯曲会像折纸；
- 绑定前应用缩放，否则骨骼会歪。

### 1.8 性能预算：先定目标，再动手

下面是**经验值**，不是硬性标准，按你的目标平台调整：

| 资产类型 | 三角面 | 材质数 | 贴图 | 骨骼数 |
|---|---|---|---|---|
| 移动端小道具 | 300～3,000 | 1 | 512～1024 | — |
| 移动端角色 | 3,000～10,000 | 1～2 | 1024 | 20～40 |
| PC 小道具 | 1,000～10,000 | 1～2 | 1024～2048 | — |
| PC 角色 | 15,000～50,000 | 2～4 | 2048 | 40～80 |
| 主角/特写 | 50,000～150,000 | 2～6 | 2048～4096 | 60～120 |

**比面数更影响性能的**：

- **Draw Call**：材质数、网格数越多，Draw Call 越高；
- **贴图尺寸/带宽**：4K 贴图在移动端很贵；
- **骨骼数/蒙皮计算**；
- **Overdraw**：半透明、粒子；
- **阴影**：阴影贴图分辨率和投射者数量。

**优化手段**：合并材质、贴图图集（Atlas）、LOD、遮挡剔除（Occlusion Culling）、远处小物体用 Impostor/公告板。

### 1.9 文件格式：为什么游戏首选 glTF

| 格式 | 扩展名 | 特点 | 推荐用途 |
|---|---|---|---|
| Blender 工程 | `.blend` | 保留全部编辑数据 | **源文件，必须保留** |
| glTF 二进制 | `.glb` | 单文件、开放标准、PBR、动画、骨骼 | **Godot/Web/移动端首选** |
| glTF 分离 | `.gltf` + `.bin` + 贴图 | 可读、便于调试 | 需要单独检查贴图时 |
| FBX | `.fbx` | Autodesk 生态、兼容广、体积大 | Mixamo、传统 DCC 交换 |
| OBJ | `.obj` | 只有几何+简单材质，无动画 | 3D 打印、简单交换 |
| STL | `.stl` | 只有三角面，无 UV/材质 | 3D 打印 |
| USD / USDZ | `.usd` / `.usdz` | 影视/AR 生态 | 影视、Apple AR |

**结论**：Blender 源文件存 `.blend`，给 Godot 用 `.glb`，给 Mixamo 用 `.fbx`。

### 1.10 自测 12 问

读完这一章，试着回答；答不上来就回头查：

1. 顶点、边、面分别是什么？
2. Blender 和 Godot 的“上”和“前”分别是什么轴？
3. 为什么导出前要 `Ctrl+A` → `Scale`？
4. 非流形网格会导致什么问题？
5. 法线朝内会有什么现象？
6. UV 接缝的作用是什么？
7. 哪些贴图要设成 Non-Color？
8. Metallic 和 Roughness 分别控制什么？
9. 角色关节处为什么需要边环？
10. 每个顶点最多建议受几根骨骼影响？
11. 为什么游戏里要控制材质数量？
12. `.blend`、`.glb`、`.fbx` 分别什么时候用？

---

## 2. AI 生成 3D：把它当“数字黏土”

### 2.1 原理一句话

主流图生 3D 的流程大致是：**输入图片 → 多视角扩散/重建 → 得到几何（SDF/NeRF/Gaussian/网格）→ 生成或投影纹理**。

这意味着：

- 正面通常最准，**背面和内部是“猜”出来的**；
- 薄片、镂空、细长结构、透明材质、毛发容易失败；
- 几何是三角面高模，UV 和拓扑通常不适合直接做游戏资产；
- 纹理可能是“烘焙投影”，接缝和拉伸需要修。

### 2.2 工具地图

| 工具 | 类型 | 特点 | 适合 |
|---|---|---|---|
| **腾讯混元 3D** | 在线平台/开源模型 | 文生/图生 3D、纹理生成、3D 动画、低模、草图生 3D、人物生成 | 中文用户、快速出草模 |
| **Tripo AI** | 在线 | 图生/文生 3D，速度快，导出格式多 | 道具、概念模型 |
| **Meshy** | 在线 | 文生/图生 3D、纹理、动画 | 游戏道具、角色草模 |
| **Rodin / Hyper3D** | 在线 | 高质量几何、支持多视角 | 需要较好几何的资产 |
| **TRELLIS** | 开源 | 微软系，图生 3D，可本地部署 | 有显卡、想本地跑 |
| **CSM** | 在线 | 图生 3D、场景/物体重建 | 真实物体扫描式重建 |
| **Sloyd** | 在线 | 参数化/程序化生成 | 风格化道具、快速迭代 |

> 这些工具迭代非常快，具体功能、免费额度、导出格式、商用条款**以官网为准**。本文只讲通用管线。

### 2.3 输入图怎么准备

图生 3D 的质量，**七分靠输入图**。

**推荐**：

- 单个物体，居中，占画面 60%～80%；
- 纯白/纯色背景，无地面阴影；
- 均匀照明，不要强逆光、不要彩色环境光；
- 正交或长焦视角，避免透视畸变；
- 1024×1024 以上；
- 如果工具支持多视角：正面、侧面、背面、45° 各一张，光照一致；
- 物体完整，不被遮挡。

**避免**：

- 多个物体、复杂背景；
- 透明、反光、毛发、薄片、细线；
- 文字、logo、商标、受版权保护的角色；
- 极端透视、广角、鱼眼；
- 运动模糊、噪点、低分辨率。

### 2.4 提示词与参数

不同工具的参数名不同，但方向一致：

| 目标 | 提示词/参数建议 |
|---|---|
| 低模 | `low-poly game asset`, `low poly`, 选择“低模/游戏模型”选项 |
| 四边面 | 选择 `quad mesh` / `remesh` / `retopology` 选项（如果有） |
| 风格 | `stylized`, `hand-painted`, `realistic PBR` |
| 单物体 | `single object`, `no base`, `no background`, `isolated` |
| 角色 | `T-pose` / `A-pose`, `full body`, `symmetrical` |
| 纹理 | `PBR textures`, `4K texture`, `clean UV` |
| 不要 | `no text`, `no logo`, `no watermark`, `no floor` |

**实践建议**：

- 一次生成 **4～8 个候选**，不要只生成一个就定稿；
- 先选**剪影最好**的，再修细节；
- 同一张输入图换种子多跑几次；
- 生成结果不满意，先换输入图，再改提示词。

### 2.5 生成结果验收清单

拿到模型后，别急着导入 Blender，先按这张表打分：

| 检查项 | 合格标准 | 不合格怎么办 |
|---|---|---|
| 剪影 | 正面/侧面轮廓正确，比例舒服 | 重新生成或手动修 |
| 朝向 | 正面朝向一致（建议 -Y） | 旋转后应用 |
| 尺度 | 高度/尺寸符合现实 | 缩放后应用 |
| 封闭性 | 没有大破洞、没有明显内部面 | 补洞/删内部面 |
| 法线 | 大部分朝外 | `Shift+N` 重算 |
| UV | 有 UV，没有大面积重叠/拉伸 | 重新展开 |
| 贴图 | 分辨率够，接缝可接受 | 修接缝/重烘焙 |
| 材质数 | 越少越好（1～3 个） | 合并/图集 |
| 面数 | 在预算内，或可减面 | Decimate/重拓扑 |
| 部件 | 没有底座、地面、背景、多余物体 | 分离删除 |
| 对称性 | 左右基本对称（角色/道具） | Mirror/手动修 |
| 绑定友好 | 角色为 T/A pose，关节处有环线 | 重拓扑/摆姿势 |
| 版权 | 商用条款允许，输入图有授权 | 换工具/换素材 |

### 2.6 版权与合规（重要）

- **看服务条款**：是否允许商用、是否允许修改、是否要求署名、免费额度生成的东西归谁。
- **输入图必须有授权**：不要拿别人的角色、商标、影视截图去生成。
- **AI 生成物的版权在不同国家/地区规则不同**，商用前建议咨询专业人士。
- **保留生成记录**：提示词、输入图、生成时间、工具版本，方便后续维权/平台审核。
- **平台披露**：Steam 等平台对 AI 生成内容有披露要求；上架前查最新政策。
- 本节不是法律意见，只是提醒你把合规当成资产管线的一部分。

### 2.7 什么适合 AI，什么不适合

| 适合 | 不适合 |
|---|---|
| 场景道具（箱子、石头、家具、路灯） | 主角/重要角色（需要精确控制拓扑和表情） |
| 风格化草模/概念模型 | 需要精确碰撞的关卡几何 |
| 背景摆件、远景建筑 | 需要复杂动画/布料/毛发的资产 |
| 纹理/材质灵感 | 有严格版权要求的 IP 角色 |
| 快速迭代形状 | 薄片、镂空、透明、细长结构 |

---

## 3. Blender 快速上手

### 3.1 安装与初始设置

1. 从 [blender.org](https://www.blender.org/download/) 下载 **官方安装包**（不要用微软商店的旧版）。
2. 版本选择：
   - **5.2**：当前稳定版，功能最新；
   - **4.5 LTS**：长期支持版，教程兼容性更好。
   - 两者操作基本一致，本文以 5.x 为主。
3. **建议用英文界面**：绝大多数教程、快捷键、菜单名都是英文；中文翻译会降低搜索效率。
   - `Edit > Preferences > Interface > Translation > Language: English`。
4. 笔记本/触控板用户：
   - `Preferences > Input > Emulate 3 Button Mouse`：用 `Alt+左键` 代替中键；
   - `Emulate Numpad`：没有小键盘时用主键盘数字键模拟视角。
5. 建议开启：
   - `Preferences > Save & Load > Auto Save Temporary Files`；
   - `Save Versions` 设为 2～3；
   - `Preferences > System > Undo Steps` 调到 64 以上。
6. 检查单位：`Scene Properties > Units`，Unit System `Metric`，Unit Scale `1.0`，Length `Meters`。
7. 保存习惯：`Ctrl+S` 保存；Blender 会保留 `.blend1` 备份；大改前用 `Ctrl+Shift+S` 另存一个版本。
8. 内置插件（一般默认开启）：
   - **glTF 2.0**：导入/导出 `.glb`；
   - **Node Wrangler**：材质节点快捷操作；
   - **Rigify**：人形绑定。
   - 可选扩展：**LoopTools**（环工具）、**Extra Objects**（更多基本体）。

### 3.2 界面：先认清 6 个区域

```
┌──────────────────────────────────────────────────────────────┐
│ 顶部菜单 / Workspace（Layout, Modeling, UV Editing, ...）      │
├───────────────┬──────────────────────────────┬───────────────┤
│               │                              │               │
│  Outliner     │        3D Viewport           │  Properties   │
│  大纲视图      │        3D 视图               │  属性面板      │
│  （场景树）    │  （建模、选择、变换）          │ （修改器/材质）│
│               │                              │               │
├───────────────┴──────────────────────────────┴───────────────┤
│  Timeline（时间线） / Dope Sheet / Graph Editor                │
├──────────────────────────────────────────────────────────────┤
│  Status Bar（状态栏：提示当前操作、快捷键）                     │
└──────────────────────────────────────────────────────────────┘
```

| 区域 | 作用 | 快捷操作 |
|---|---|---|
| 3D Viewport | 建模、选择、变换、预览 | `T` 工具栏，`N` 侧边栏 |
| Outliner | 场景树，管理物体/集合 | 双击重命名，`Ctrl+单击` 孤立显示 |
| Properties | 修改器、材质、灯光、渲染设置 | 图标切换标签 |
| Timeline | 关键帧、播放 | `Space` 播放/暂停 |
| Workspace | 预设布局 | `Modeling`、`UV Editing`、`Shading`、`Animation` |
| Status Bar | 当前工具提示 | 卡住时看这里 |

**常用布局操作**：

- `Ctrl+Space`：最大化当前区域（再按恢复）；
- 拖动区域边角：拆分/合并区域；
- `Shift+F5`：切回 3D Viewport；`Shift+F10`：UV Editor；`Shift+F3`：节点编辑器。

### 3.3 视图导航：先学会“看”

| 操作 | 快捷键 |
|---|---|
| 旋转视角 | **中键拖动**（触控板：`Alt+左键`） |
| 平移视角 | **Shift+中键拖动** |
| 缩放 | **滚轮**（或 `Ctrl+中键拖动`） |
| 正视图 | `小键盘 1` |
| 右视图 | `小键盘 3` |
| 顶视图 | `小键盘 7` |
| 反方向视图 | `Ctrl+小键盘 1/3/7` |
| 切换透视/正交 | `小键盘 5` |
| 聚焦选中物体 | `小键盘 .` |
| 全览场景 | `Home` |
| 独立显示选中 | `小键盘 /` |
| 相机视角 | `小键盘 0` |
| 着色模式饼菜单 | `Z`（Wireframe/Solid/Material/Rendered） |
| X-Ray 透视 | `Alt+Z` |
| 最大化区域 | `Ctrl+Space` |

> **练习**：新建场景，放 3 个立方体，用上面的快捷键在 30 秒内依次看到正、右、顶、透视、相机视角，并聚焦每个物体。

### 3.4 选择

| 操作 | 快捷键 |
|---|---|
| 点选 | 左键 |
| 加选/减选 | `Shift+左键` |
| 框选 | `B`，拖框，左键确认 |
| 圈选 | `C`，滚轮调半径，左键涂抹，`Esc` 退出 |
| 全选 | `A` |
| 取消全选 | `Alt+A` |
| 反选 | `Ctrl+I` |
| 选择相连（悬停） | `L` |
| 选择相连（全部） | `Ctrl+L` |
| 边环选择 | `Alt+左键` |
| 边环（环向） | `Ctrl+Alt+左键` |
| 隐藏选中 | `H` |
| 取消隐藏 | `Alt+H` |
| 隐藏未选中 | `Shift+H` |

### 3.5 变换：G / R / S 三件套

| 操作 | 快捷键 |
|---|---|
| 移动 | `G` |
| 旋转 | `R` |
| 缩放 | `S` |
| 约束到 X/Y/Z 轴 | 按 `G/R/S` 后按 `X` / `Y` / `Z` |
| 约束到平面 | `Shift+X` / `Shift+Y` / `Shift+Z` |
| 数值输入 | 变换中直接输入数字，`Enter` 确认 |
| 临时吸附 | 按住 `Ctrl` |
| 清除位置/旋转/缩放 | `Alt+G` / `Alt+R` / `Alt+S` |
| 应用变换 | `Ctrl+A` → 选择 `Location/Rotation/Scale` |
| 复制 | `Shift+D` |
| 关联复制 | `Alt+D` |
| 删除 | `X` |
| 重命名 | `F2` |
| 重复上一步 | `Shift+R` |
| 调整上一步参数 | `F9` |

**数值输入示例**：

- `G` → `Z` → 输入 `2` → `Enter`：沿 Z 轴移动 2 米。
- `S` → `X` → 输入 `0.5` → `Enter`：X 轴缩放到 50%。
- `R` → `Z` → 输入 `90` → `Enter`：绕 Z 轴旋转 90°。

### 3.6 五种模式

| 模式 | 进入方式 | 用途 |
|---|---|---|
| Object Mode | `Ctrl+Tab` → Object | 选择、变换、加修改器、导出 |
| Edit Mode | `Tab` | 编辑顶点/边/面 |
| Sculpt Mode | `Ctrl+Tab` → Sculpt | 雕刻高模 |
| UV Edit | `Ctrl+Tab` → UV Edit | 展开、排布 UV |
| Weight Paint | `Ctrl+Tab` → Weight Paint | 绘制骨骼权重 |
| Pose Mode | 选中骨架后 `Ctrl+Tab` | 摆姿势、做动画 |

> `Tab` 只在 Object/Edit 之间切换；其他模式用 `Ctrl+Tab` 饼菜单。

### 3.7 修改器：非破坏性建模

修改器是 Blender 的核心优势：先加修改器，不满意随时改参数，最后再应用。

| 修改器 | 位置 | 用途 | 关键参数 |
|---|---|---|---|
| **Decimate** | Generate | 减面 | Collapse / Ratio |
| **Remesh** | Generate | 重建网格 | Voxel Size / Quad |
| **Mirror** | Generate | 镜像 | Axis / Clipping / Merge |
| **Subdivision Surface** | Generate | 细分平滑 | Levels |
| **Solidify** | Generate | 加厚 | Thickness / Offset |
| **Bevel** | Generate | 倒角 | Width / Segments / Angle |
| **Boolean** | Generate | 布尔运算 | Difference / Union / Intersect |
| **Shrinkwrap** | Deform | 贴合高模 | Target / Offset |
| **Weighted Normal** | Normals | 改善硬表面法线 | Weight / Keep Sharp |
| **Triangulate** | Generate | 三角化 | Quad Method |
| **Data Transfer** | Deform | 传递法线/UV/权重 | Face Corner Data |
| **Armature** | Deform | 骨骼变形 | Object / Vertex Groups |

**修改器顺序原则**：

- 先做**改变几何形状**的（Mirror、Solidify、Bevel、Boolean）；
- 再做**减面/细分**（Decimate、Subdivision）；
- 最后做**法线相关**（Weighted Normal）；
- 不确定就拖到最上面试，观察结果。

> 导出前可以保留修改器，导出 glTF 时勾选 **Apply Modifiers**；但绑定/烘焙前建议先应用关键修改器。

### 3.8 必会快捷键（按组练）

**视图**

| 操作 | 快捷键 |
|---|---|
| 旋转视角 | `中键拖动` |
| 平移视角 | `Shift+中键拖动` |
| 缩放 | `滚轮` |
| 正/右/顶视图 | `小键盘 1 / 3 / 7` |
| 聚焦选中 | `小键盘 .` |
| 全览 | `Home` |
| 独立显示选中 | `小键盘 /` |
| 切换着色模式 | `Z` |
| X-Ray 透视 | `Alt+Z` |
| 最大化区域 | `Ctrl+Space` |
| 透视/正交 | `小键盘 5` |
| 相机视角 | `小键盘 0` |

**选择**

| 操作 | 快捷键 |
|---|---|
| 点选 | `左键` |
| 加选/减选 | `Shift+左键` |
| 框选 | `B` |
| 圈选 | `C` |
| 全选 | `A` |
| 取消全选 | `Alt+A` |
| 反选 | `Ctrl+I` |
| 选择相连 | `L` |
| 边环选择 | `Alt+左键` |
| 隐藏选中 | `H` |
| 取消隐藏 | `Alt+H` |
| 隐藏未选中 | `Shift+H` |

**变换**

| 操作 | 快捷键 |
|---|---|
| 移动 | `G` |
| 旋转 | `R` |
| 缩放 | `S` |
| 轴向约束 | `X` / `Y` / `Z` |
| 平面约束 | `Shift+X/Y/Z` |
| 临时吸附 | `Ctrl` |
| 清除位置/旋转/缩放 | `Alt+G` / `Alt+R` / `Alt+S` |
| 应用变换 | `Ctrl+A` |
| 复制 | `Shift+D` |
| 关联复制 | `Alt+D` |
| 删除 | `X` |
| 重命名 | `F2` |

**编辑模式**

| 操作 | 快捷键 |
|---|---|
| Object/Edit 切换 | `Tab` |
| 点/边/面模式 | `1 / 2 / 3` |
| 挤出 | `E` |
| 内插 | `I` |
| 倒角 | `Ctrl+B` |
| 环切 | `Ctrl+R` |
| 切割 | `K` |
| 合并 | `M` |
| 建面 | `F` |
| 边/面/点菜单 | `Ctrl+E` / `Ctrl+F` / `Ctrl+V` |
| 法线朝外 | `Shift+N` |
| 分离 | `P` |
| 合并对象 | `Ctrl+J` |
| 吸附菜单 | `Shift+S` |

**其他**

| 操作 | 快捷键 |
|---|---|
| 搜索命令 | `F3` |
| 调整上一步 | `F9` |
| 撤销/重做 | `Ctrl+Z` / `Ctrl+Shift+Z` |
| 保存/另存 | `Ctrl+S` / `Ctrl+Shift+S` |
| 播放/暂停 | `Space` |
| 渲染 | `F12` |

> **记忆方法**：不要一次背 40 个。每天挑 5 个，在练习里强制使用，一周就能形成肌肉记忆。

### 3.9 第一个 10 分钟练习：做一个带倒角的箱子

目标：熟悉“新建 → 编辑 → 挤出 → 倒角 → 材质 → 导出”。

1. `Shift+A` → Mesh → Cube。
2. `Tab` 进入 Edit Mode，`S` → `Z` → 输入 `0.5`，压扁。
3. `Ctrl+B`，拖动鼠标做倒角，滚轮增加段数（2～3 段）。
4. `Tab` 回 Object Mode，`Ctrl+A` → `Scale` 应用缩放。
5. 右键 → `Shade Smooth`；硬表面建议用 `Object > Shade Auto Smooth`（Blender 4.1+ 会自动加一个 `Smooth by Angle` 修改器），再用 `Weighted Normal` 改善光照。
6. 打开 `Shading` 工作区，给箱子一个 Principled BSDF 材质：
   - Base Color 设为木色；
   - Roughness 0.7；
   - Metallic 0。
7. `Object > Set Origin > Origin to Geometry`。
8. `File > Export > glTF 2.0`，导出 `box.glb`。

**验收**：箱子没有黑面、没有拉伸、缩放是 1,1,1、原点在几何中心、能在 Godot 里正常显示。

### 3.10 “熟练”的量化标准

达到下面这些，说明你已经脱离新手：

- 30 秒内完成任意视角定位 + 聚焦；
- 3 分钟做出一个带倒角的箱子/桌子；
- 5 分钟完成一个硬表面道具的 UV；
- 10 分钟接好一套 PBR 材质；
- 20 分钟清理一个 AI 模型并导出；
- 不看教程，能把一个 `.glb` 导入 Godot 并跑起来。

---

## 4. 清理与重拓扑

### 4.1 导入 AI 模型

1. `File > Import > glTF 2.0 (.glb/.gltf)`。
2. 选中模型，按 `N` 打开侧边栏，看 **Dimensions（尺寸）**：
   - 一个石灯应该是 1～2 米；
   - 如果显示 200 米，说明 AI 用了厘米/任意单位，需要缩放。
3. 检查朝向：`小键盘 1` 正视图，模型正面应朝 **-Y**（也就是你面对屏幕时，模型面向你）。
4. 检查材质：`Material Preview` 模式（`Z` → Material）看贴图是否正常。
5. 检查面数：打开视口右上角的 `Overlays > Statistics`，左上角会显示顶点数、面数、三角面数。

**修正尺度**：

- Object Mode → `S` → 输入目标比例 → `Enter`；
- `Ctrl+A` → `Scale`；
- 再把原点设到合适位置。

### 4.2 清理五连

AI 模型导入后，按顺序做这五步：

1. **合并重复顶点**：`Tab` → `A` → `M` → `By Distance`，阈值 `0.0001`。
2. **重算法线**：`Shift+N`。
3. **删除孤立点/边**：`Mesh > Clean Up > Delete Loose`。
4. **检查非流形**：`Select > All by Trait > Non Manifold`，能补的补（`F` 或 `Mesh > Clean Up > Fill Holes`），不能补的删。
5. **删除内部面/重叠面**：`Select > All by Trait > Interior Faces`，确认后删除。

**补充**：

- `Select > All by Trait > Faces by Sides` 可以找 N-gon；
- `Mesh > Clean Up > Merge by Distance` 也可以处理重叠顶点；
- 打开 **Face Orientation** 叠加层，红色面就是法线朝内。

### 4.3 分离、删除、合并

| 操作 | 做法 | 用途 |
|---|---|---|
| 按松散块分离 | `Tab` → 选中 → `P` → `By Loose Parts` | 把底座、地面、配件分开 |
| 按材质分离 | `P` → `By Material` | 拆分不同材质 |
| 删除物体 | Object Mode → `X` | 删除底座/背景 |
| 合并物体 | 选中多个 → `Ctrl+J` | 合并成一个网格 |
| 合并到目标 | 先选其他，最后选目标 → `Ctrl+J` | 目标保留名字/数据 |

**常见 AI 垃圾**：底座、地面圆盘、背景板、漂浮的小碎片、重复的对称部件。先分离，再删。

### 4.4 减面三条路

| 方法 | 速度 | 质量 | 适用 |
|---|---|---|---|
| **Decimate（Collapse）** | 快 | 中/差 | 静态道具、远景、快速草模 |
| **Remesh（Voxel/Quad）** | 中 | 中 | 需要均匀拓扑、雕刻后重建 |
| **手动重拓扑** | 慢 | 最好 | 角色、主角道具、需要变形的资产 |
| **QuadriFlow Remesh** | 中 | 较好 | 想要四边面、但不想手动重拓扑 |

#### Decimate 用法

1. 选中物体 → `Properties > Modifier > Add Modifier > Generate > Decimate`。
2. Mode 选 `Collapse`。
3. Ratio 从 `0.5` 开始试，逐渐降。**按原始面数算目标**：原始 100k 面、目标 5k 面，Ratio 约 `0.05`；原始 30k 面、目标 6k 面，Ratio 约 `0.2`。
4. 观察剪影；如果开始破面，往回加。
5. 满意后 `Apply`。

**技巧**：

- 先 `Ctrl+B` 给硬边倒角，再减面，剪影更稳；
- 用 `Weighted Normal` 改善减面后的硬表面光照；
- 不要对角色关节区域暴力减面。

#### Remesh / QuadriFlow

- `F3` 搜索 `Voxel Remesh`（Sculpt Mode 下 `Ctrl+R`）：按体素重建，适合雕刻/破损模型；
- `F3` 搜索 `QuadriFlow Remesh`：生成四边面，面数可控；
- 重建后通常需要重新 UV。

#### 手动重拓扑

核心思路：**在低模上“贴着”高模重建表面**。

1. 复制一份高模，命名为 `High`，隐藏或半透明显示；
2. 新建一个平面/立方体，命名为 `Low`；
3. 给 `Low` 加 **Shrinkwrap** 修改器，Target 选 `High`，Offset 0.001；
4. 开启 **Snap**（磁铁图标），Snap To 选 `Face Project`；
5. 用 `E` 挤出、`Ctrl+R` 环切、`K` 切割、`Ctrl+E > Bridge Edge Loops` 建面；
6. 用 `Alt+左键` 选边环，保持四边面；
7. 关节处增加环线（肩膀、肘、膝、腰）；
8. 完成后应用 Shrinkwrap，删除高模或留作烘焙。

**重拓扑原则**：

- 先大形，后细节；
- 面密度均匀；
- 关节处环线垂直于弯曲方向；
- 避免 N-gon 和三角形（角色变形区域）；
- 左右对称用 Mirror 修改器；
- 面数控制在预算内。

### 4.5 高低模与烘焙法线

AI 高模的细节（石纹、凹槽、铆钉）不需要用几何保留，可以**烘焙成法线贴图**贴到低模上。

流程：

1. 高模命名 `High`，低模命名 `Low`，两者位置重合；
2. 低模有 UV；
3. 低模材质里新建 Image Texture 节点，新建一张 `2048×2048` 的图片，命名 `T_Low_Normal`，色彩空间设 **Non-Color**；
4. 选中该 Image Texture 节点（让它成为激活节点）；
5. 先选 `High`，再 `Shift+左键` 选 `Low`（Low 是激活对象）；
6. Render Engine 切 **Cycles**；
7. `Properties > Render > Bake`：
   - Bake Type：`Normal`；
   - 勾选 `Selected to Active`；
   - Cage Extrusion：`0.02～0.05`；
   - Max Ray Distance：`0.1`；
   - Margin：`8～16 px`；
8. 点击 `Bake`；
9. 烘焙完成后，在 Image Editor 里 `Save As` 保存为 PNG/TGA。

**同理可烘焙**：AO、Roughness、Base Color（从程序化材质/高模）。

**常见失败**：

- 高低模位置不重合 → 射线打不到；
- 低模没有 UV → 无法写图；
- Cage 太小 → 边缘缺失；
- Margin 太小 → 接缝有缝；
- 法线图色彩空间不是 Non-Color → 光照错误。

### 4.6 拓扑验收标准

- [ ] 剪影和原模型一致；
- [ ] 面数在预算内；
- [ ] 没有非流形边/内部面/重叠面；
- [ ] 法线统一朝外；
- [ ] 关节处有足够环线；
- [ ] UV 已展开，没有大面积重叠；
- [ ] 缩放已应用；
- [ ] 原点位置正确；
- [ ] 命名规范，没有多余物体。

---

## 5. UV 展开

### 5.1 为什么要 UV

贴图是 2D 图片，模型是 3D 表面。UV 就是“把 3D 表面剪开、摊平、放到图片上”的过程。UV 做不好，贴图就会拉伸、接缝明显、纹素密度不一致。

### 5.2 标记接缝

接缝要藏在**不容易被看到**的地方：

- 角色：手臂内侧、腿内侧、后脑、腋下、裆部；
- 道具：底部、背面、结构转折处；
- 建筑：墙角、屋檐下。

操作：

1. Edit Mode → 选边（`Alt+左键` 选边环）；
2. `Ctrl+E` → `Mark Seam`；
3. 需要取消：`Ctrl+E` → `Clear Seam`。

### 5.3 展开

| 方法 | 适用 | 操作 |
|---|---|---|
| **Unwrap** | 有明确接缝的模型 | 选所有面 → `U` → `Unwrap` |
| **Smart UV Project** | 硬表面、AI 模型快速展开 | 选所有面 → `U` → `Smart UV Project` |
| **Cube Projection** | 立方体/建筑 | `U` → `Cube Projection` |
| **Cylinder Projection** | 柱子/瓶子 | `U` → `Cylinder Projection` |
| **Sphere Projection** | 球体 | `U` → `Sphere Projection` |
| **Follow Active Quads** | 规则四边面 | 先选一个面，再 `U` → `Follow Active Quads` |

**Smart UV Project 参数**：

- Angle Limit：`66°`（默认）；
- Island Margin：`0.02`（给接缝留空间）；
- Area Weight：`0`；
- Correct Aspect：勾选。

### 5.4 排布 UV

1. 打开 `UV Editing` 工作区；
2. `A` 全选 UV 岛；
3. `UV > Pack Islands`（或 `Ctrl+P`）；
4. `Ctrl+A` → `Average Island Scale`：统一纹素密度；
5. 检查是否有岛重叠：`UV > Select Overlap`；
6. 调整 margin，保证贴图边缘有 2～4 像素 bleed；
7. 旋转/缩放岛，尽量填满 0～1 空间。

**纹素密度公式**：

```
texel density = 贴图分辨率 / 模型实际尺寸（米）
```

例如 2048 px 贴图覆盖 2 米宽的物体，密度约 1024 px/m。

### 5.5 UV 检查

- 给模型临时贴一张 **Checker（棋盘格）** 贴图；
- 观察格子是否均匀：格子被拉长 = 拉伸；格子大小差很多 = 密度不一致；
- 检查接缝是否在显眼位置；
- 检查 UV 是否超出 0～1 范围（会重复平铺，通常不是想要的）；
- 检查是否有重叠岛（镜像/对称部件除外）。

### 5.6 常见错误

| 现象 | 原因 | 解决 |
|---|---|---|
| 贴图拉伸 | 接缝不合理/未展开 | 重新标记接缝，`U > Unwrap` |
| 纹理糊 | 岛太小/贴图太小 | 放大岛/提高分辨率 |
| 接缝明显 | 接缝在正面/Margin 太小 | 移动接缝/增加 Margin |
| UV 重叠 | 自动展开重叠 | `Select Overlap` 后手动排布 |
| 镜像部件共用 UV | 正常，但光照贴图需要 UV2 | 单独展开 UV2 |
| 贴图方向不对 | UV 旋转 | 在 UV Editor 里 `R` 旋转 |

### 5.7 重新 UV 后，原贴图怎么办？

这是 AI 资产管线里**最容易翻车的一步**：

> AI 模型自带的贴图，是按它**原来的 UV** 烘焙的。你一重新展开 UV，贴图就会错位。

两条路：

**路线 A：不改 UV，只修接缝/排布**

如果原 UV 没有大面积重叠、拉伸可接受，优先保留原 UV，只做 `Pack Islands`、`Average Island Scale`、移动接缝。这样贴图不会丢。

**路线 B：必须重新 UV → 把旧贴图烘焙到新 UV**

1. `Shift+D` 复制一份模型，原模型命名 `Source`，副本命名 `Baked`；
2. 在 `Baked` 上新建 UV Map（`Properties > Object Data > UV Maps > +`），重新展开；
3. 给 `Baked` 的材质新建一张 `2048×2048` 图片，命名 `T_New_BaseColor`，色彩空间 **sRGB**；
4. 在 `Baked` 材质里新建 Image Texture 节点，选中它（激活），并保持它被选中；
5. 先选 `Source`，再 `Shift+左键` 选 `Baked`（`Baked` 为激活对象）；
6. Render Engine 切 **Cycles**；
7. `Bake Type` 选 `Diffuse`，只勾选 `Color`，取消 `Direct` 和 `Indirect`；
8. 勾选 `Selected to Active`，Cage Extrusion 设 `0`，Max Ray Distance 设 `0.1`；
9. Bake，保存新贴图；
10. 用新贴图替换 `Baked` 的 Base Color，旧模型可以删除或留作备份。

**如果 AI 贴图里已经带了烘焙光照/阴影**：它不适合直接做 PBR Base Color，最好重新做材质，或至少把阴影压平。

---

## 6. 材质与贴图

### 6.1 Principled BSDF 参数

| 参数 | 游戏含义 | 常用值 |
|---|---|---|
| Base Color | 基础色 | 贴图 |
| Metallic | 金属度 | 金属 1，非金属 0 |
| Roughness | 粗糙度 | 0.2（光滑）～0.9（粗糙） |
| IOR | 折射率 | 默认 1.45 |
| Alpha | 透明度 | 1（不透明） |
| Normal | 法线贴图 | Normal Map 节点 |
| Emission Color | 自发光颜色 | 黑色=不发光 |
| Emission Strength | 自发光强度 | 0～5 |
| Coat | 清漆层 | 汽车漆、瓷器 |
| Transmission | 透射 | 玻璃、水 |

> Blender 4.x/5.x 的参数名和 3.x 略有不同（如 `Specular` → `Specular IOR Level`），以界面为准。

### 6.2 贴图通道与命名

| 贴图 | 命名示例 | 色彩空间 | 说明 |
|---|---|---|---|
| 基础色 | `T_Rock_BaseColor.png` | sRGB | 颜色 |
| 法线 | `T_Rock_Normal.png` | Non-Color | 切线空间法线 |
| 粗糙度 | `T_Rock_Roughness.png` | Non-Color | 灰度 |
| 金属度 | `T_Rock_Metallic.png` | Non-Color | 灰度 |
| AO | `T_Rock_AO.png` | Non-Color | 灰度 |
| ORM | `T_Rock_ORM.png` | Non-Color | R=AO, G=Roughness, B=Metallic |
| 自发光 | `T_Rock_Emission.png` | sRGB | 发光 |
| 高度 | `T_Rock_Height.png` | Non-Color | 视差/置换 |

**命名规范**：`T_` 贴图、`M_` 材质、`SM_` 静态网格、`SK_` 骨骼网格。Godot 不强制，但团队协作时非常有用。

### 6.3 色彩空间

- **sRGB**：Base Color、Emission、UI 贴图；
- **Non-Color**：Normal、Roughness、Metallic、AO、Height、Mask。

在 Blender 里：`Image Texture` 节点 → `Color Space` 下拉。在 Godot 里：glTF 导入会按用途处理色彩空间；手动导入贴图时，在 `Import` 面板确认颜色贴图按 sRGB、法线/数据贴图没有被当成颜色图。

### 6.4 把 AI 贴图接入材质

AI 模型通常自带一张“颜色贴图”，可能没有独立的粗糙度/金属度/法线。做法：

1. 把颜色贴图接到 Base Color；
2. 用 `Color > RGB to BW` 或 `Separate Color` 从颜色图里提取粗糙度（不精确，但可用）；
3. 用 `Bump` 节点从颜色图生成微弱法线（临时方案）；
4. 更好的做法：在 Blender 里重新烘焙 AO/法线，或在材质软件里重做 PBR。

> AI 生成的贴图常常把**光照/阴影**直接烘进了颜色里，严格来说不算 PBR。做写实资产时，最好把它当参考，重新做一套干净的 BaseColor/Roughness/Metallic/Normal。

**Node Wrangler 快捷操作**：

- 选中 Principled BSDF，`Ctrl+Shift+T`：自动弹出贴图选择，按命名自动连接；
- `Ctrl+T`：给选中节点加 Texture Coordinate + Mapping；
- 也可以直接从输出端口拖到输入端口手动连接。

### 6.5 烘焙

除了法线，还可以烘焙：

| 烘焙类型 | 用途 |
|---|---|
| Normal | 高模细节 → 低模 |
| Ambient Occlusion | 缝隙阴影，增强体积感 |
| Roughness | 从程序化材质烘焙 |
| Base Color / Diffuse | 合并多个材质 |
| Emission | 发光贴图 |
| Combined | 完整光照（通常不用于游戏） |

**烘焙设置要点**：

- Render Engine：Cycles；
- Samples：32～128（Normal/AO 可以低一些）；
- Margin：8～16 px；
- Selected to Active：高模→低模时勾选；
- 目标贴图节点必须选中；
- 输出 16-bit PNG（法线）或 8-bit PNG（颜色/AO）。

### 6.6 贴图优化

- **尺寸**：按预算选 512/1024/2048/4096，不要无脑 4K；
- **图集**：多个小道具共用一张贴图，减少材质和 Draw Call；
- **通道打包**：AO/Roughness/Metallic 打包成 ORM；
- **压缩**：Godot 导入时选 VRAM 压缩（移动端 ETC2/ASTC，PC S3TC/BPTC）；
- **Mipmap**：默认开启，远处不闪烁；
- **Alpha**：只有需要透明的材质才用 Alpha，其他用 Opaque。

### 6.7 在 Godot 里对应

| Blender | Godot StandardMaterial3D |
|---|---|
| Base Color | Albedo > Texture |
| Metallic | Metallic > Texture |
| Roughness | Roughness > Texture |
| Normal | Normal Map > Texture |
| AO | AO > Texture |
| Emission | Emission > Texture |
| Alpha | Transparency > Alpha |
| Height | Heightmap > Texture（视差） |

**注意**：

- Godot 的 glTF 导入会自动识别 ORM 打包；
- 法线贴图如果看起来“凹变成凸”，翻转绿色通道（G）——Blender 用 OpenGL 风格（+Y），部分工具用 DirectX 风格（-Y）；
- 透明材质优先用 `Alpha Scissor`，少用 `Alpha Blend`。

---

## 7. 骨骼、蒙皮与动画

> 这一章是角色路线。第一次做角色，建议先用 **Mixamo** 跑通，再学 Rigify。

### 7.1 角色资产的前置条件

- 角色是 **T-pose 或 A-pose**；
- 左右对称；
- 关节处有足够环线（肩膀、肘、腕、髋、膝、踝）；
- 网格是流形、法线朝外；
- 缩放已应用；
- 面数在预算内；
- UV 已完成（绑定后改拓扑会很痛苦）。

### 7.2 Armature 基础

1. `Shift+A` → Armature；
2. `Tab` 进入 Edit Mode，选中骨骼，`E` 挤出子骨骼；
3. 命名规范：`Hips`、`Spine`、`Chest`、`Neck`、`Head`、`UpperArm.L`、`LowerArm.L`、`Hand.L`、`UpperLeg.L`、`LowerLeg.L`、`Foot.L`；
4. 用 `.L` / `.R` 后缀，方便镜像和对称；
5. 选中一侧骨骼，`Armature > Symmetrize` 生成另一侧；
6. 回 Object Mode，选中网格，再 `Shift+左键` 选骨架，`Ctrl+P` → `With Automatic Weights`。

### 7.3 权重绘制

自动权重只是起点，必须检查：

1. 选中网格 → `Weight Paint` 模式；
2. 选中某根骨骼，看红色影响区域；
3. 用 `Add`/`Subtract`/`Smooth` 笔刷修；
4. `Weights > Normalize All`：所有权重归一化；
5. `Weights > Limit Total`：限制每顶点 4 根骨骼；
6. `Weights > Clean`：清除微小权重（阈值 0.01）；
7. 摆几个极端姿势检查：抬臂、弯腰、蹲下、转头。

**常见问题**：

- 关节处塌陷 → 环线不足/权重过渡太硬；
- 腋下撕裂 → 权重分配不均；
- 模型整体变形 → 缩放未应用/骨架和网格不匹配；
- 左右不对称 → 权重没镜像。

### 7.4 Mixamo 路线（最省事）

适合人形角色，快速获得骨骼和动画。

1. 在 Blender 导出角色为 **FBX**（或 OBJ）：
   - 只选角色网格；
   - 应用缩放；
   - T-pose；
   - 不要带骨架（让 Mixamo 自动绑）。
2. 打开 [Mixamo](https://www.mixamo.com/)，上传模型；
3. 按提示放置关节标记；
4. 选择动画（Idle、Walk、Run、Attack 等）；
5. 下载 **FBX Binary**，勾选 `With Skin`；
   - 要原地动画（走路不位移）就勾 `In Place`；
   - 要 root motion 就不勾；
6. 导入 Blender，检查尺度、朝向、骨骼：
   - Mixamo 的 FBX 常以厘米为单位，导入后可能是 100 倍大，必要时 `S` → `0.01` → `Ctrl+A` → `Scale`；
7. 导出 `.glb` 给 Godot。

**注意**：

- Mixamo 对人形比例和 T-pose 有要求；
- 手指、尾巴、翅膀等非标准骨骼可能需要手动补；
- Mixamo 的动画版权/商用条款以其官网为准。

### 7.5 Rigify 路线（更可控）

1. `Shift+A` → Armature → Human (Meta-Rig)；
2. 对齐骨骼到角色；
3. `Properties > Armature > Rigify` → `Generate Rig`；
4. 选中网格，再选生成的 rig，`Ctrl+P` → `With Automatic Weights`；
5. 用 rig 的控制器摆姿势；
6. 需要 IK/FK 切换时，用 rig 自带的控制器。

### 7.6 动画基础

- 在 `Pose Mode` 选中骨骼，`I` 插入关键帧（Location/Rotation/Scale）；
- 时间线拖动到下一帧，摆新姿势，再 `I`；
- `Graph Editor` 调曲线（缓入缓出）；
- `Dope Sheet` 管理多个动作；
- 循环动画：首帧和末帧姿势一致；
- `NLA Editor`：把动作 push down 成 strip，方便导出多个剪辑。

**导出多个动画**：

- 每个动作命名清楚（`Idle`、`Walk`、`Run`）；
- 在 NLA 里 push down；
- glTF 导出时 Animation Mode 选 `NLA Tracks`。

### 7.7 角色验收

- [ ] T/A pose，左右对称；
- [ ] 骨骼命名规范；
- [ ] 权重归一化，限制 4 根骨骼；
- [ ] 抬臂/弯腰/蹲下没有明显破面；
- [ ] 动画首尾循环；
- [ ] 缩放应用，原点在脚底；
- [ ] 导出 `.glb` 后动画能在 Godot 播放。

---

## 8. 导出到 Godot

### 8.1 导出前检查清单

- [ ] 缩放已应用（`Ctrl+A` → `Scale`）；
- [ ] 旋转已应用（除需要保留的朝向）；
- [ ] 原点位置正确（角色脚底、道具底部中心）；
- [ ] 网格命名规范，无多余物体；
- [ ] 材质数尽量少，贴图路径正确；
- [ ] 法线朝外，无黑面；
- [ ] UV 已展开，贴图无缺失；
- [ ] 动画/NLA 已整理；
- [ ] 场景单位是米。

### 8.2 glTF 导出设置

`File > Export > glTF 2.0 (.glb/.gltf)`

| 选项 | 建议 | 说明 |
|---|---|---|
| Format | **glTF Binary (.glb)** | 单文件，贴图打包 |
| Include | **Selected Objects** | 只导出选中的资产 |
| Transform > +Y Up | ✅ | Blender Z-up → glTF Y-up |
| Data > Apply Modifiers | ✅ | 应用修改器 |
| Data > Normals | ✅ | 保留法线 |
| Data > Tangents | ✅ | 法线贴图需要 |
| Data > Materials | ✅ | 导出材质 |
| Data > Colors | 按需 | 顶点色 |
| Animation > Animation Mode | `NLA Tracks` 或 `Actions` | 多个动画 |
| Animation > Sampling | 1 | 每帧采样 |
| Compression > Draco | 可选 | 能减小体积，但增加导入复杂度 |
| Image > Format | Automatic | 自动选 PNG/JPEG |
| Image > Quality | 90 | JPEG 质量 |
| Remember Export Settings | ✅ | 下次复用 |

> 如果 Godot 里模型太大/太小，先检查 Blender 的 Unit Scale 和导出时的 Scale；不要用 Godot 的根节点缩放去“硬凑”。

> **角色导出**：不要手动 Apply `Armature` 修改器；保留它，glTF 导出器会自动处理蒙皮和骨骼。

### 8.3 Godot 导入设置

1. 把 `.glb` 拖进 Godot 的 `FileSystem`；
2. 选中文件，打开 `Import` 面板；
3. 常用设置：

| 设置 | 建议 |
|---|---|
| Root Type | `Node3D` |
| Meshes > Ensure Tangents | 没有切线时开启 |
| Meshes > Generate LODs | ✅（Godot 4.x，位置随版本略有差异） |
| Meshes > Create Shadow Meshes | ✅ |
| Materials > Extraction Mode | 按需（Keep/Extract） |
| Animation > Import | 有动画时开启 |
| Nodes > Use Node Type Suffixes | ✅ |

4. 点 `Reimport`；
5. 双击 `.glb` 打开 `Advanced Import Settings`，可以逐个网格调整 LOD、碰撞、材质。

### 8.4 碰撞：用命名后缀自动生成

Godot 支持在 Blender 物体名里加后缀，导入时自动处理（`-`、`_`、`$` 都行，大小写不敏感）：

| 后缀 | 效果 | 适用 |
|---|---|---|
| `-col` | 生成三角形网格碰撞（Concave） | 关卡几何、静态环境 |
| `-convcol` | 生成凸包碰撞（Convex） | 简单道具、动态物体 |
| `-colonly` | 只生成碰撞，不显示网格 | 隐藏碰撞体 |
| `-convcolonly` | 只生成凸包碰撞 | 隐藏碰撞体 |
| `-noimp` | 导入时跳过该节点 | 删除建模用的灯光/参考物 |

**例子**：Blender 里把物体命名为 `StoneLantern-convcol`，导入 Godot 后会自动生成一个带凸包碰撞的 `StaticBody3D`。

> 复杂凹形道具用 `-col` 可能性能较差；能用凸包就用 `-convcol`。角色/动态物体通常用 `CollisionShape3D` + 胶囊/胶囊体，不建议直接用网格碰撞。

### 8.5 命名与目录规范

```
assets/
├─ characters/
│  └─ hero/
│     ├─ hero.blend
│     ├─ hero.glb
│     └─ textures/
│        ├─ T_Hero_BaseColor.png
│        ├─ T_Hero_Normal.png
│        └─ T_Hero_ORM.png
├─ props/
│  └─ stone_lantern/
│     ├─ stone_lantern.blend
│     ├─ stone_lantern.glb
│     └─ textures/
└─ shared/
   └─ materials/
```

- 物体名用 ASCII，避免空格和中文（Godot 支持，但跨工具容易出问题）；
- 前缀：`SM_` 静态网格、`SK_` 骨骼网格、`M_` 材质、`T_` 贴图；
- 一个资产一个文件夹，源文件和导出文件放一起；
- `.blend` 永远保留，方便以后改。

### 8.6 在 Godot 里搭一个展示场景

1. 新建 `Node3D` 场景；
2. 添加 `WorldEnvironment`，创建 `Environment`，设置天空；
3. 添加 `DirectionalLight3D`，开启阴影；
4. 添加 `Camera3D`，调整位置；
5. 把 `.glb` 拖进场景；
6. 添加 `MeshInstance3D` 或直接用导入的场景；
7. 运行，检查比例、材质、阴影、朝向。

**快速检查清单**：

- [ ] 模型高度符合预期（和 1.8 米的人模对比）；
- [ ] 正面朝向 -Z；
- [ ] 贴图没有丢失/发紫；
- [ ] 法线贴图方向正确；
- [ ] 透明材质正常；
- [ ] 碰撞能挡住角色；
- [ ] LOD 在远处生效；
- [ ] 动画能播放。

### 8.7 常见导入问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 模型全黑 | 没有材质/贴图、法线朝内、灯光太暗 | 检查材质、`Shift+N`、加灯 |
| 模型发紫/粉 | 贴图路径丢失 | 重新链接贴图/打包 |
| 太大/太小 | 单位/缩放不一致 | Blender 里缩放并应用 |
| 躺着/背对 | 轴向不对 | 检查 `+Y Up` 和 Blender 朝向 |
| 透明边缘发黑 | Alpha 混合/预乘 | 用 `Alpha Scissor`，检查贴图 |
| 动画不播放 | 未导出动画/NLA 未 push down | 检查导出设置和 AnimationPlayer |
| 骨骼扭曲 | 权重/缩放/rest pose | 应用缩放、修权重 |
| 黑斑/闪烁 | 重叠面/法线/z-fighting | 删重叠面、重算法线 |
| 法线贴图反了 | 绿色通道方向 | 翻转 G 通道 |
| 材质重复太多 | 每个部件一个材质 | 合并材质/图集 |
| 移动端卡 | 面数/材质/贴图/骨骼太多 | 减面、合并材质、降贴图 |

---

## 9. 实战：混元 3D 模型到 Godot 道具

我们用一个**石灯**做完整流程。你可以换成宝箱、路牌、木桶。

### 9.0 生成

1. 准备一张正面图：单物体、白底、均匀光、1024×1024；
2. 在混元 3D（或其他工具）选 **图生 3D**；
3. 提示词：`stone lantern, game asset, low-poly, PBR, single object, no base, no background`；
4. 如果平台有选项：低模、对称、PBR、无底座；
5. 生成 4～8 个候选，选剪影最好的；
6. 导出 **GLB**，贴图 2K 以内。

### 9.1 导入与检查（5 分钟）

1. `File > Import > glTF 2.0`，选 `stone_lantern.glb`；
2. `N` 面板看尺寸：目标高度 1.5～2 米；
3. 如果尺寸是 150～200，`S` → `0.01` → `Ctrl+A` → `Scale`；
4. 正视图确认正面朝 -Y；
5. `Z` → Material Preview 看贴图；
6. 看 Statistics：记下三角面数。

### 9.2 清理（10 分钟）

1. `Tab` → `A` → `M` → `By Distance`，阈值 `0.0001`；
2. `Shift+N` 重算法线；
3. `Mesh > Clean Up > Delete Loose`；
4. `Select > All by Trait > Non Manifold`，补洞/删边；
5. `Select > All by Trait > Interior Faces`，删除；
6. `P` → `By Loose Parts`，删除底座/地面/碎片；
7. 选中所有需要的部件，`Ctrl+J` 合并；
8. 打开 Face Orientation，确认没有红色面。

### 9.3 减面（10 分钟）

1. 先看 Statistics 里的原始三角面数；
2. 加 `Decimate` 修改器，Mode `Collapse`；
3. Ratio 按目标反推：原始 100k 面 → 目标 5k，Ratio 约 `0.05`；原始 20k 面 → 目标 5k，Ratio 约 `0.25`；
4. 目标：**3,000～8,000 三角面**（PC 小道具）；
5. 观察剪影，破面就调高 Ratio；
6. Apply；
7. 加 `Weighted Normal` 修改器，改善硬表面光照；
8. 如果减面后太丑，改用 QuadriFlow 或手动重拓扑。

### 9.4 UV（10 分钟）

> **先做决定**：保留 AI 原 UV，还是重新展开？
> - 原 UV 没有大面积重叠/拉伸 → **保留**，只做排布；
> - 必须重新展开 → 先按 [5.7](#57-重新-uv-后原贴图怎么办) 把旧贴图烘焙到新 UV，否则第 9.5 步的贴图会错位。

1. **要重做 UV 时**：`Tab` → `A` → `U` → `Smart UV Project`；保留原 UV 则直接跳到第 3 步；
2. Angle Limit `66°`，Island Margin `0.02`；
3. 打开 `UV Editing` 工作区，`A` → `UV > Pack Islands`；
4. `Ctrl+A` → `Average Island Scale`；
5. `UV > Select Overlap`，确认没有重叠；
6. 贴 Checker 检查拉伸；
7. 接缝尽量藏在底部/背面。

### 9.5 材质（10 分钟）

1. 打开 `Shading` 工作区；
2. 选 Principled BSDF，`Ctrl+Shift+T` 自动接贴图；
3. 检查色彩空间：
   - Base Color：sRGB；
   - Normal/Roughness/Metallic/AO：Non-Color；
4. 如果只有一张颜色图：
   - 接 Base Color；
   - Roughness 设 0.8；
   - Metallic 设 0；
   - 用 `Bump` 从颜色图生成微弱凹凸；
5. 材质命名 `M_StoneLantern`；
6. 确认没有多余材质槽。

### 9.6 原点与命名（3 分钟）

1. `Tab` 回 Object Mode；
2. `Ctrl+A` → `Scale`；
3. 进入 Edit Mode，选中**底部中心**的一个顶点（或底边中点）；
   - 如果模型底部正好在 `Z=0` 且居中，也可以 `Shift+S > Cursor to World Origin`；
4. `Shift+S` → `Cursor to Selected`；
5. 回 Object Mode，`Object > Set Origin > Origin to 3D Cursor`；
6. 物体命名 `StoneLantern-convcol`（如果要自动碰撞）；
7. 放到 Collection `Props`。

### 9.7 导出（3 分钟）

1. 只选中石灯；
2. `File > Export > glTF 2.0`；
3. Format `GLB`；
4. Include `Selected Objects`；
5. `+Y Up` ✅；
6. `Apply Modifiers` ✅；
7. `Tangents` ✅；
8. 导出 `stone_lantern.glb`。

### 9.8 Godot 验证（5 分钟）

1. 拖入 `assets/props/stone_lantern/`；
2. Import 面板：
   - `Generate LODs` ✅；
   - `Create Shadow Meshes` ✅；
   - `Ensure Tangents` 按需；
3. Reimport；
4. 拖进 3D 场景；
5. 添加 `Camera3D`、`DirectionalLight3D`、`WorldEnvironment`；
6. 运行，检查：
   - 高度约 1.5～2 米；
   - 正面朝 -Z；
   - 贴图正常；
   - 碰撞能挡住角色；
   - 阴影正常。

### 9.9 验收

- [ ] 3k～8k 三角面；
- [ ] 1 个材质、1～2 张 2K 贴图；
- [ ] UV 无重叠、无明显拉伸；
- [ ] 法线朝外、无黑面；
- [ ] 原点在底部中心；
- [ ] 缩放 1,1,1；
- [ ] 有碰撞；
- [ ] Godot 里比例/朝向正确；
- [ ] 总耗时 45～60 分钟（第一次可以 2 小时）。

---

## 10. 21 天训练计划

每天 **60～90 分钟**。不要只看教程，**每天必须动手产出东西**。

### 第 1 周：Blender 基础肌肉记忆

| 天 | 任务 | 产出 |
|---|---|---|
| D1 | 界面、导航、选择、G/R/S、视图切换 | 用 5 个基本体摆一个小场景 |
| D2 | Edit Mode：挤出、内插、倒角、环切、镜像 | 一个带倒角的箱子/桌子 |
| D3 | 修改器：Decimate、Mirror、Solidify、Bevel、Boolean | 一个石灯/路牌 |
| D4 | UV：接缝、Unwrap、Smart UV、Pack Islands | 给 D3 的模型展开 UV + Checker |
| D5 | 材质：Principled BSDF、贴图、色彩空间 | 给 D3 的模型接 PBR 材质 |
| D6 | 灯光、相机、渲染、导出 | 渲染一张静帧 + 导出 GLB |
| D7 | 限时复刻：30 分钟做一个简单道具 | 一个完整可导出道具 |

**每日 10 分钟热身（照着做）**：

| 时间 | 动作 |
|---|---|
| 0～2 分钟 | 新建场景，随机选 3 个物体，用 `小键盘 1/3/7`、`小键盘 .`、`小键盘 /`、`Home` 快速定位 |
| 2～4 分钟 | 对物体做 `G/R/S` + `X/Y/Z` + 数字输入，再用 `Alt+G/R/S` 复位 |
| 4～7 分钟 | Edit Mode：`E` / `I` / `Ctrl+B` / `Ctrl+R` / `K` / `M` 各做 3 次 |
| 7～10 分钟 | 给一个物体 `Smart UV Project` + Checker + Principled 材质 |

> 每周复盘：哪个操作还在找菜单？把它记下来，下周每天只练那一个。

### 第 2 周：AI 资产管线

| 天 | 任务 | 产出 |
|---|---|---|
| D8 | 用混元 3D 生成 4 个模型，按 2.5 清单验收 | 4 个候选 + 验收记录 |
| D9 | 导入、清理五连、分离删除 | 一个干净的网格 |
| D10 | Decimate / QuadriFlow / 手动重拓扑 | 预算内的低模 |
| D11 | UV 展开 + 排布 + Checker 检查 | 规范 UV |
| D12 | 材质 + 烘焙法线/AO | 一套 PBR 贴图 |
| D13 | 导出 glTF + Godot 导入 + 碰撞/LOD | Godot 里能跑的道具 |
| D14 | 限时：3 个道具完整管线 | 3 个可用的游戏道具 |

### 第 3 周：角色、动画、整合

| 天 | 任务 | 产出 |
|---|---|---|
| D15 | 角色比例、T/A pose、关节环线 | 一个可绑定的角色低模 |
| D16 | Armature、自动权重、Weight Paint | 能摆姿势的角色 |
| D17 | Mixamo 自动绑定 + 下载动画 | 带 Idle/Walk 的角色 |
| D18 | 动画循环、NLA、root motion、导出 | 多动画 GLB |
| D19 | Godot 角色场景、AnimationTree | 能走能 idle 的角色 |
| D20 | 综合：3 个道具 + 1 个角色 + 灯光 | 一个小场景 |
| D21 | 复盘、整理作品、制定下一步 | 作品集/下一步计划 |

### 练习题库

- 10 分钟：箱子、杯子、盘子、路牌、木桶；
- 30 分钟：石灯、宝箱、武器、椅子、栅栏；
- 60 分钟：AI 模型清理 + UV + 材质 + 导出；
- 90 分钟：角色低模 + Mixamo + Godot 动画。

### 如何判断自己“熟练”了

- 不用想就能完成视图导航和变换；
- 看到破面/黑斑能立刻定位是法线、重叠面还是 UV；
- 拿到 AI 模型，30 分钟内能判断“能不能用、怎么修”；
- 能预估一个资产的面数、贴图、材质和工时；
- 导出 Godot 一次成功，不需要反复试错。

---

## 11. 常见问题 FAQ

**Q1：学 Blender 还是 Maya/3ds Max？**
独立开发/小团队优先 Blender：免费、开源、更新快、社区大、glTF 支持好。

**Q2：需要学雕刻（Sculpt）吗？**
不是必须。AI 已经能给你高模，你的重点应放在**清理、重拓扑、UV、材质、导出**。想做风格化角色再学雕刻。

**Q3：需要学绑骨吗？**
先用 Mixamo 跑通，再学 Rigify。大部分独立游戏的角色动画可以靠 Mixamo + 少量手动修。

**Q4：面数多少才合适？**
看平台和资产类型，参考 [1.8 性能预算](#18-性能预算先定目标再动手)。不要盲目追求低面数，剪影和 UV 更重要。

**Q5：为什么模型在 Godot 里是黑的/紫的？**
黑色：没有材质/贴图、法线朝内、灯光太暗。紫色/粉色：贴图路径丢失。先检查材质和贴图，再检查法线。

**Q6：为什么模型巨大/极小？**
Blender 和 AI 工具的单位不一致。在 Blender 里缩放到现实尺寸，`Ctrl+A` → `Scale`，再导出。

**Q7：为什么模型朝向不对？**
Blender 是 Z-up、-Y 前；Godot 是 Y-up、-Z 前。导出勾选 `+Y Up`，并确保 Blender 里正面朝 -Y。

**Q8：为什么动画不播放？**
检查：导出时是否勾选动画、NLA 是否 push down、Godot 里是否有 `AnimationPlayer`、动画是否被正确导入。

**Q9：为什么透明材质边缘发黑？**
Alpha Blend 的排序/预乘问题。优先用 `Alpha Scissor`，或检查贴图的 Alpha 通道和预乘设置。

**Q10：法线贴图看起来反了怎么办？**
翻转绿色通道（G）。Blender 用 OpenGL 风格（+Y），部分工具用 DirectX 风格（-Y）。

**Q11：AI 模型能直接商用吗？**
看工具的服务条款和输入图授权；AI 生成物版权在不同地区规则不同；上架平台可能要求披露。保留生成记录，必要时咨询专业人士。

**Q12：一定要重拓扑吗？**
静态道具如果面数可接受、剪影没问题，可以只 Decimate；角色、需要变形的资产、主角道具建议手动重拓扑。

**Q13：UV 拉伸怎么办？**
重新标记接缝、Unwrap、Pack Islands、Average Island Scale；确保缩放已应用；用 Checker 检查。

**Q14：骨骼绑定后模型扭曲？**
应用缩放、检查权重归一化、限制每顶点 4 根骨骼、检查 rest pose 和骨架位置。

**Q15：Godot 里没有碰撞？**
用命名后缀 `-col`/`-convcol`，或在 Godot 里手动加 `StaticBody3D` + `CollisionShape3D`。

**Q16：导入后材质很多怎么办？**
合并材质、用图集、把多个小物件合并成一个网格（如果不需要单独交互）。

**Q17：模型有黑斑/闪烁？**
重叠面、法线错误、z-fighting、AO 烘焙问题。删重叠面、`Shift+N`、检查 UV。

**Q18：如何减面又不破坏剪影？**
先倒角硬边，再用 Decimate；关键轮廓手动加线；用 Weighted Normal 改善光照；必要时手动重拓扑。

**Q19：多久能学会？**
2 周能跑通管线，1～3 个月能比较熟练；之后靠项目驱动，不要一直看教程。

**Q20：需要数位板吗？**
建模/UV/材质用鼠标键盘就够；雕刻和手绘贴图才需要数位板。

**Q21：AI 模型能不能不经过 Blender 直接拖进 Godot？**
可以，但要先确认面数、尺度、朝向、UV、材质和碰撞。多数 AI 模型面数偏高、没有碰撞、材质数多，直接进引擎容易比例不对或性能差；Blender 主要就是用来修这些。

---

## 12. 速查卡

### 12.1 最常用的快捷键

| 快捷键 | 作用 | 快捷键 | 作用 |
|---|---|---|---|
| `中键拖动` | 旋转视角 | `Shift+中键` | 平移 |
| `滚轮` | 缩放 | `小键盘 1/3/7` | 正/右/顶 |
| `小键盘 .` | 聚焦 | `Home` | 全览 |
| `Tab` | Object/Edit | `1/2/3` | 点/边/面 |
| `G/R/S` | 移动/旋转/缩放 | `X/Y/Z` | 轴约束 |
| `E` | 挤出 | `I` | 内插 |
| `Ctrl+B` | 倒角 | `Ctrl+R` | 环切 |
| `M` | 合并 | `Shift+N` | 法线朝外 |
| `Ctrl+A` | 应用 | `Shift+D` | 复制 |
| `P` | 分离 | `Ctrl+J` | 合并 |
| `U` | UV 展开 | `F3` | 搜索命令 |

### 12.2 导出设置速查

```
Format: GLB
Include: Selected Objects
Transform: +Y Up ✅
Data: Apply Modifiers ✅, Tangents ✅, Normals ✅
Animation: NLA Tracks（多动画）
Images: Automatic
```

### 12.3 资产验收清单

- [ ] 单位/缩放/原点正确；
- [ ] 朝向 -Y（Blender）/ -Z（Godot）；
- [ ] 面数在预算内；
- [ ] 无非流形/内部面/重叠面；
- [ ] 法线朝外；
- [ ] UV 无重叠/无明显拉伸；
- [ ] 材质数受控，贴图色彩空间正确；
- [ ] 骨骼权重归一化（角色）；
- [ ] 动画循环/命名正确；
- [ ] 碰撞/LOD 已配置；
- [ ] Godot 里比例/材质/阴影正常。

### 12.4 常用菜单路径

| 操作 | 路径 |
|---|---|
| 应用缩放 | `Object > Apply > Scale` |
| 设置原点 | `Object > Set Origin > Origin to Geometry / 3D Cursor` |
| 重算法线 | `Mesh > Normals > Recalculate Outside` |
| 删除孤立点 | `Mesh > Clean Up > Delete Loose` |
| 选择非流形 | `Select > All by Trait > Non Manifold` |
| 选择内部面 | `Select > All by Trait > Interior Faces` |
| 填充洞 | `Mesh > Clean Up > Fill Holes`（或 F3 搜索） |
| 四边形重拓扑 | F3 搜索 `QuadriFlow Remesh` |
| 体素重拓扑 | F3 搜索 `Voxel Remesh` |
| 烘焙 | `Render Properties > Bake` |
| 导出 glTF | `File > Export > glTF 2.0` |

---

## 13. 资源与继续学习

### 官方文档

- [Blender Manual](https://docs.blender.org/manual/en/latest/)：最权威，遇到问题先查这里；
- [Blender 中文手册](https://docs.blender.org/manual/zh-hans/latest/)：中文翻译；
- [Godot 3D 导入文档](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)；
- [glTF 2.0 规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)。

### 教程（按顺序看）

1. **Blender 官方 Fundamentals**：界面、建模、材质、动画的基础；
2. **Blender Guru 的 Donut 教程**：经典入门，虽然长，但能建立完整心智模型；
3. **Grant Abbitt 的 “Get Good at Blender”**：短练习，适合每天跟做；
4. **Godot 官方 3D 教程**：把资产用起来；
5. 遇到具体问题：Blender Stack Exchange、r/blenderhelp、YouTube 搜索具体操作。

### 免费资产/工具

- [Poly Haven](https://polyhaven.com/)：CC0 的 HDRI、贴图、模型；
- [Mixamo](https://www.mixamo.com/)：免费人形骨骼和动画（Adobe 账号）；
- [ambientCG](https://ambientcg.com/)：CC0 PBR 贴图；
- [Kenney](https://kenney.nl/)：CC0 游戏资产；
- [Material Maker](https://www.materialmaker.org/)：开源程序化材质；
- [ArmorPaint](https://armorpaint.org/)：开源贴图绘制；
- [Krita](https://krita.org/) / [GIMP](https://www.gimp.org/)：修贴图。

### 学习原则

- **项目驱动**：不要为了学而学，拿一个具体资产做完整管线；
- **限时练习**：30 分钟做一个道具，逼自己用快捷键；
- **拆解优秀资产**：下载免费低模，检查它的拓扑、UV、材质；
- **记录问题**：建立一个“踩坑清单”，下次避免；
- **不要追求完美**：独立游戏里，“够用且能上线”比“技术上完美”重要。

---

## 附录 A. 术语中英对照

| 中文 | 英文 | 中文 | 英文 |
|---|---|---|---|
| 顶点 | Vertex | 边 | Edge |
| 面 | Face | 网格 | Mesh |
| 拓扑 | Topology | 流形 | Manifold |
| 非流形 | Non-manifold | 法线 | Normal |
| UV 展开 | UV Unwrap | 接缝 | Seam |
| UV 岛 | UV Island | 纹素密度 | Texel Density |
| 材质 | Material | 贴图 | Texture |
| 法线贴图 | Normal Map | 切线空间 | Tangent Space |
| 基于物理的渲染 | PBR | 纹素 | Texel |
| 光照贴图 | Lightmap | 顶点色 | Vertex Color |
| 基础色 | Base Color | 金属度 | Metallic |
| 粗糙度 | Roughness | 环境光遮蔽 | AO |
| 自发光 | Emission | 透明度 | Alpha |
| 骨骼 | Armature / Bone | 蒙皮 | Skinning |
| 权重 | Weight | 绑定 | Rigging |
| 关键帧 | Keyframe | 曲线编辑器 | Graph Editor |
| 摄影表 | Dope Sheet | 非线性动画 | NLA |
| 根运动 | Root Motion | 重拓扑 | Retopology |
| 减面 | Decimate | 烘焙 | Bake |
| 原点 | Origin | 变换 | Transform |
| 应用缩放 | Apply Scale | 修改器 | Modifier |
| 挤出 | Extrude | 内插 | Inset |
| 倒角 | Bevel | 环切 | Loop Cut |
| 切割 | Knife | 桥接 | Bridge |
| 镜像 | Mirror | 吸附 | Snap |
| 收缩包裹 | Shrinkwrap | 数据传递 | Data Transfer |
| 细节层级 | LOD | 绘制调用 | Draw Call |
| 遮挡剔除 | Occlusion Culling | 公告板 | Billboard |
| 碰撞 | Collision | 图集 | Atlas |
| 压缩 | Compression | 正交 | Orthographic |
| 透视 | Perspective | 平滑着色 | Shade Smooth |
| 自动平滑 | Auto Smooth | 三角面 | Triangle |
| 四边面 | Quad | 多边形 | N-gon |

---

## 附录 B. 资产规格模板

复制到你的资产文件夹里，每次做新资产先填表：

```markdown
# 资产规格：<名称>

- 类型：静态道具 / 角色 / 环境 / 武器
- 目标平台：PC / 移动端 / Web
- 引擎：Godot 4.x
- 风格：写实 / 风格化 / 低模

## 几何
- 三角面：
- 顶点数：
- 材质数：
- 网格数：
- 是否流形：
- 法线朝向：
- 缩放是否应用：

## UV / 贴图
- UV 通道：
- 是否有重叠：
- 贴图尺寸：
- 贴图通道：BaseColor / Normal / Roughness / Metallic / AO / Emission / Alpha
- 色彩空间是否正确：

## 骨骼 / 动画
- 骨骼数：
- 每顶点最大影响：
- 动画剪辑：Idle / Walk / Run / Attack / ...
- 是否循环：
- 是否有 root motion：

## 导出 / 引擎
- 导出格式：GLB
- 朝向：-Z（Godot）
- 原点：底部中心 / 脚底
- 碰撞：-col / -convcol / 手动
- LOD：有 / 无
- 导入设置：

## 验收
- [ ] Godot 中比例正确
- [ ] 材质/贴图正常
- [ ] 动画正常
- [ ] 碰撞正常
- [ ] 性能在预算内
```

---

> **最后一句**：3D 和 Blender 是**手艺**，不是知识。看十篇教程不如完整做一遍“AI 生成 → 清理 → UV → 材质 → 导出 → Godot 跑起来”。从今天开始，先做那个石灯。
