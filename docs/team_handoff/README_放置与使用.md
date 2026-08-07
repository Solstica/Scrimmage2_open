# 放置说明

建议把本目录整体复制到仓库：

```text
docs/team_handoff/
```

即：

```text
docs/team_handoff/00_当前版本总索引.md
docs/team_handoff/角色初始化/
docs/team_handoff/章节续作指南/
```

之后三个人每次给自己的 AI 第一条指令统一写：

> 先读取 `docs/team_handoff/00_当前版本总索引.md`、你的角色初始化文档、`fix/<角色>/todo/` 和本次目标章节续作指南。在复述当前 canonical branch、唯一正文源、冻结结果和禁止事项之前，不要修改任何文件。

## 文档优先级

发生冲突时按以下顺序判断：

1. `docs/team_handoff/00_当前版本总索引.md`
2. 对应 `角色初始化/*.md`
3. `fix/<角色>/todo/`
4. 对应 `章节续作指南/*.md`
5. `git fetch` 后的 canonical branch 当前文件
6. 历史 `AI_COLLABORATION_GUIDE.md` / `ARCHITECTURE.md` / 旧 README / 旧总稿

若第 6 类文档中仍有旧 80/20 数值或“禁止 fix”等旧规则，不得覆盖本阶段新规则。
