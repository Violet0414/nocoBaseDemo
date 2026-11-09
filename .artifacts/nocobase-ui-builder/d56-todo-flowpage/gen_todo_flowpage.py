# 生成「工作台待办（新）」flowPage 蓝本：jsBlock 版审批台
# 两种模式：
#   STUB=1 python3 gen_todo_flowpage.py  → 占位代码（无 API 调用，用于通过 apply-blueprint 建页）
#   python3 gen_todo_flowpage.py         → 完整审批台代码（建页后 SQL 直改进 flowModels 用）
import json, pathlib, os

CODE = r'''
const { Card, List, Button, Tag, Empty, Typography, Space, message, Popconfirm } = ctx.libs.antd;

const ENABLED_WF = [396745412444160, 396743055048704, 396746379231232, 396799131385856];
const WF_TITLE = {
  396745412444160: '请假审批',
  396743055048704: '缴费审核',
  396746379231232: '退学审批',
  396799131385856: '报名审核',
};
const FALLBACK_ACTIONS = {
  396745412444160: [{key:'approve',title:'通过',values:{status:'approved'}},{key:'reject',title:'驳回',values:{status:'rejected'}}],
  396743055048704: [{key:'pass',title:'审核通过',values:{status:'approved'}},{key:'deny',title:'拒绝',values:{status:'rejected'}}],
  396746379231232: [{key:'approve',title:'通过',values:{status:'approved'}},{key:'reject',title:'驳回',values:{status:'rejected'}}],
  396799131385856: [{key:'pass',title:'审核通过',values:{status:'approved'}},{key:'deny',title:'拒绝',values:{status:'rejected'}}],
};

async function getNodeActions(nodeId, workflowId) {
  try {
    const n = (await ctx.api.request({ url: 'flow_nodes:get', params: { filterByTk: nodeId } }))?.data?.data;
    const forms = (n?.config?.forms) || {};
    const formKey = Object.keys(forms)[0] || 'review';
    const actions = (forms[formKey]?.actions) || FALLBACK_ACTIONS[workflowId] || [];
    return { formKey, actions };
  } catch (e) {
    return { formKey: 'review', actions: FALLBACK_ACTIONS[workflowId] || [] };
  }
}

async function loadTasks() {
  const res = await ctx.api.resource('workflowManualTasks').listMine({ pageSize: 100, filter: JSON.stringify({ status: 0 }) });
  const rows = res?.data?.data || [];
  const mine = rows.filter(t => ENABLED_WF.includes(t.workflowId));
  const nodeCache = {};
  for (const nid of [...new Set(mine.map(t => t.nodeId))]) {
    const t0 = mine.find(t => t.nodeId === nid);
    nodeCache[nid] = await getNodeActions(nid, t0.workflowId);
  }
  return mine.map(t => ({ ...t, ...nodeCache[t.nodeId] }));
}

async function submit(task, action) {
  try {
    await ctx.api.resource('workflowManualTasks').submit({ filterByTk: task.id, values: { result: { [task.formKey]: { ...(action.values || {}) }, _: action.key } } });
    message.success('已提交：' + action.title);
    await draw();
  } catch (e) {
    const msg = e?.response?.data?.errors?.[0]?.message || e.message || String(e);
    message.error('提交失败：' + msg);
  }
}

async function draw() {
  ctx.render(<Card size="small"><Typography.Text>待办加载中…</Typography.Text></Card>);
  let tasks = [];
  let err = null;
  try { tasks = await loadTasks(); } catch (e) { err = e?.message || String(e); }
  if (err) {
    ctx.render(<Card size="small"><Empty description={'加载失败：' + err} /></Card>);
    return;
  }
  ctx.render(
    <Card size="small" title={'待办任务（' + tasks.length + '）'}>
      {tasks.length === 0 ? (
        <Empty description="暂无待办任务" />
      ) : (
        <List
          dataSource={tasks}
          renderItem={(t) => (
            <List.Item
              actions={(t.actions || []).map(a => (
                <Popconfirm key={a.key} title={'确认「' + a.title + '」？'} onConfirm={() => submit(t, a)}>
                  <Button size="small" type={a.values && a.values.status === 'rejected' ? 'default' : 'primary'} danger={a.values && a.values.status === 'rejected'}>
                    {a.title}
                  </Button>
                </Popconfirm>
              ))}
            >
              <List.Item.Meta
                title={<Space><Tag color="blue">{WF_TITLE[t.workflowId] || ('流程#' + t.workflowId)}</Tag><Typography.Text strong>{t.title}</Typography.Text></Space>}
                description={'创建于 ' + String(t.createdAt || '').replace('T', ' ').slice(0, 19)}
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
}

await draw();
'''

CODE_STUB = r'''
const { Card, Typography } = ctx.libs.antd;
ctx.render(<Card size="small"><Typography.Text>审批台模块加载中…（占位）</Typography.Text></Card>);
'''

mode = os.environ.get("STUB")
if mode == "1":
    bp_code = CODE_STUB
    out_name = "d56-todo-flowpage-stub.json"
else:
    bp_code = CODE
    out_name = "d56-todo-flowpage.json"

bp = {
    "version": "1",
    "mode": "create",
    "navigation": {
        "layoutUid": "admin-layout-model",
        "group": {"routeId": 396734888738816},
        "item": {"title": "工作台待办", "icon": "CarryOutOutlined"},
    },
    "page": {"title": "工作台待办"},
    "tabs": [
        {
            "key": "main",
            "title": "待办任务",
            "blocks": [
                {
                    "key": "todoJsBlock",
                    "type": "jsBlock",
                    "settings": {"code": bp_code},
                }
            ],
        }
    ],
}

out = pathlib.Path(__file__).parent / out_name
out.write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
print("written", out)
