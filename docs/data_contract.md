# 数据契约

## 输入字段

### 必填字段

- `ticket_id`：工单主键
- `desc_clean`：主投诉文本
- `resolution_cause_clean`：处理依据或原因补充
- `biz_type`：原始一级业务分类，仅作参考
- `biz_subtype`：原始二级业务分类，仅作参考

### 可选字段

- `accepted_date`
- `accepted_time`
- `repeat_flag`
- `repeat_ticket_id`
- `customer_opinion`
- `customer_opinion_subtype`

## 主要输出

### `issues.parquet`

- `ticket_id`
- `issue_id`
- `issue_text`
- `evidence_text`
- `source_field`
- `issue_order`

### `issue_facts.parquet`

- `issue_id`
- `biz_object`
- `product_name`
- `card_type`
- `process_stage`
- `problem_type`
- `system_name`
- `channel_name`
- `fee_type`
- `contract_type`
- `activity_name`
- `third_party`
- `extra_facts_json`

### `working_types.parquet`

- `working_type_id`
- `auto_title`
- `keywords`
- `cluster_size`
- `status`
- `representative_issue_ids`

### `issue_assignments.parquet`

- `issue_id`
- `ticket_id`
- `assigned_type_id`
- `type_level`
- `display_name`
- `score`
- `assignment_reason`
- `evidence_text`

