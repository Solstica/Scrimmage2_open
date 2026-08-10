# AI / Agent 强制协作规则

本文件适用于所有支持仓库级指令的 AI 编程/写作代理。

## 开始任务前

1. 先读 `README.md`、`docs/RESOURCE_MAP.md`、`config/modules.json`。
2. 必须运行 `python scripts/workflow.py start <module-key>`。
3. 必须读取当前模块 `work/tasks/<module-key>.md`，以其中实时待办为工作入口。
4. 文件位置只以资源地图和配置为准；先自行查找固定路径，不要求协作者重复说明已经固定的资源位置。

## 修改边界

- 一个任务只修改一个责任域。
- 当前模块唯一正文源位于其 `modules/.../paper/`。
- `paper/` 仅由 `feature/paper-shell` 修改；章节分支不得编辑全文入口。
- 跨问共享内核只进入 `shared/`，由 `feature/shared` 维护。
- 不新建第二套全文 TeX、第二套模块树或 `final2/真的final/论文汇总` 等目录。
- 不使用 `git push --force`、`git reset --hard` 处理协作冲突。

## 待办与检查

- 实际工作出现新任务、阻塞、风险或待复核项时，实时写入当前模块任务文件，不只留在聊天里。
- 需要人工判断的事项写为 `NEEDS_REVIEW` / `需要复核`；检查可由管理员或指定复核成员完成，不绑定固定角色。
- 正文关键结果只能来自 `FROZEN + CHECKED` 的结果登记。

## 结束任务前

1. 更新当前模块任务文件；
2. 运行 `python scripts/workflow.py finish <module-key>`；
3. 检查 `git diff` 与越界修改；
4. 汇报修改、结果位置、未完成待办、需要复核项。
