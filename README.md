# Godot 游戏开发学习笔记

本目录以 Godot 官方教程为主线，配有中文讲解、GDScript 与 C# 示例，以及回合制 Roguelike 进阶内容。

## 学习内容

| 目录 | 内容 |
|---|---|
| [godot/](./godot/README.md) | 跟随 Godot 官方《Your first 2D game》教程，逐章学习并完成 Dodge the Creeps |
| [godot/DodgeTheCreeps/](./godot/DodgeTheCreeps/) | Dodge the Creeps **C# 版**成品项目 |
| [godot/DodgeTheCreepsGD/](./godot/DodgeTheCreepsGD/) | Dodge the Creeps **GDScript 版**成品项目（含难度递增，可导出 Web） |
| [GDScript 类型系统与进阶](./godot/GDScript-类型系统与进阶.md) | 面向有经验程序员的类型系统、`Variant` 边界、性能与工程实践 |
| [Godot 环境、工具与生态指南](./godot/环境与工具生态.md) | 了解语言路线、编辑器、辅助工具、社区框架和插件；软件由你自行选择安装 |
| [godot/附录-回合制Roguelike/](./godot/附录-回合制Roguelike/README-原Roguelike主线.md) | 进阶内容：Autoload、棋盘生成、回合制移动、动画与游戏流程 |
| [godot/素材/](./godot/素材/) | 教程用的素材（图片、音频、字体），做 01 章时复制到项目里 |

## 建议顺序

1. 阅读 [Godot 教程总览](./godot/README.md)，按 00–07 章完成官方入门教程。
2. 需要对照成品时，看本仓库的 [C# 版](./godot/DodgeTheCreeps/) 或 [GDScript 版](./godot/DodgeTheCreepsGD/)；也可以看官方仓库的 [GDScript 版](https://github.com/godotengine/godot-demo-projects/tree/master/2d/dodge_the_creeps) / [C# 版](https://github.com/godotengine/godot-demo-projects/tree/master/mono/dodge_the_creeps) 源码。
3. 完成主线后，再学习[回合制 Roguelike 附录](./godot/附录-回合制Roguelike/README-原Roguelike主线.md)，或尝试 [GDScript 版 README 里列出的更难官方示例](./godot/DodgeTheCreepsGD/README.md#下一步更难的官方示例)。
