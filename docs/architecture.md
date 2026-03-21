# 架构设计

## 分层目标

工程按“数据接入 -> issue 拆解 -> 术语发现 -> 属性抽取 -> 表示学习 -> 问题发现 -> 类型分配 -> 报表输出”分层，避免脚本堆积为单文件流水线。

## 核心对象

- `Ticket`：清洗后的原子工单记录
- `Issue`：从工单中拆出来的一个问题单元
- `IssueFacts`：从 issue 中抽出的结构化事实
- `WorkingType`：本次运行自动发现的问题簇
- `CanonicalType`：跨地区跨年份复用的正式问题类型
- `IssueAssignment`：issue 到类型的分配结果

## 数据流

1. `ingest` 读取配置指定的数据源，统一落到 Parquet。
2. `issue_split` 以 `desc_clean` 为主，把工单拆成多个 `IssueRecord`。
3. `term_mining` 在 issue 级文本上自动挖掘卡种、活动、系统、费用、合同等术语。
4. `extraction` 用规则和术语表抽事实，不固定只有 4 段属性。
5. `representation` 生成稀疏和稠密两类特征。
6. `discovery` 使用 UMAP + HDBSCAN 或回退算法自动形成 `WorkingType`。
7. `assignment` 优先对齐 `CanonicalType`，否则落到 `WorkingType` 或 singleton working type。
8. `reporting` 输出面向审计人员的汇总表、下钻表和 Markdown 摘要。

## 为什么 issue 是最小单位

因为一笔投诉经常同时包含多个问题。例如一条工单既可能包括“合同金额争议”，又包含“办理解押拖延”。如果直接对整笔工单做单标签分类，会把多个审计问题糊在一起。

## 为什么分 WorkingType 和 CanonicalType

- `WorkingType` 解决“先发现问题”的需求，不要求事先定义全量类别。
- `CanonicalType` 解决“跨数据集复用”的需求，让已经稳定的问题类型沉淀下来。

这保证工程能兼顾开放问题空间和长期复用。

