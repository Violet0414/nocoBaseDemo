-- C1 收尾：jsBlock 72hgyrjlwza 的 ENABLED_WF/WF_TITLE/FALLBACK_ACTIONS 补 4 条流新 revision id
-- 备份先行：backups/flowmodels_jsblock_wf_20261110.txt（脚本生成）
UPDATE "flowModels"
SET options = replace(replace(replace(replace(replace(
  options::text,
  'ENABLED_WF = [',
  'ENABLED_WF = [396908352176128, 396908373147648, 396908392022016, 396908412993536, '
),
  '396816229400576: ''请假审批'',',
  '396816229400576: ''请假审批'', 396908352176128: ''请假审批'','
),
  '396816562847744: ''退学审批'',',
  '396816562847744: ''退学审批'', 396908373147648: ''退学审批'','
),
  '396799131385856: ''报名审核'',',
  '396799131385856: ''报名审核'', 396908392022016: ''报名审核'','
)::jsonb,
  options
WHERE uid = '72hgyrjlwza';

-- 缴费/报名的 FALLBACK_ACTIONS 形态是 [pass/deny]，请假/退学是 [approve/reject]；新 id 映射追加：
UPDATE "flowModels"
SET options = replace(options::text,
  '396743055048704: [{key:''pass'',title:''审核通过'',values:{status:''approved''}},{key:''deny'',title:''拒绝'',values:{status:''rejected''}],',
  '396743055048704: [{key:''pass'',title:''审核通过'',values:{status:''approved''}},{key:''deny'',title:''拒绝'',values:{status:''rejected''}],396908412993536: [{key:''pass'',title:''审核通过'',values:{status:''approved''}},{key:''deny'',title:''拒绝'',values:{status:''rejected''}],'
)::jsonb
WHERE uid = '72hgyrjlwza';
