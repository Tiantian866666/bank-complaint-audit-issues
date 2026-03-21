# 工作类到正式类的评审流程

## 目标

尽量不让人工逐条看工单，而是在“问题簇”层面做少量确认。

## 推荐流程

1. 先跑 `full-run`，生成 `WorkingType` 和下钻报表。
2. 审计人员优先看 `category_summary.xlsx`，确认哪些簇代表稳定问题。
3. 对需要沉淀的簇，在 `reviewed_working_types.csv` 中填写：
   - `working_type_id`
   - `action`
   - `canonical_name`
   - `merge_target`
   - `notes`
4. 运行 `audit-issues promote`，把选中的工作类提升为正式类。
5. 下一批数据先对齐正式类，再自动发现新的工作类。

## action 建议取值

- `promote`：提升为新正式类
- `merge`：并入已有正式类
- `ignore`：保留为临时问题簇，不进入正式类

