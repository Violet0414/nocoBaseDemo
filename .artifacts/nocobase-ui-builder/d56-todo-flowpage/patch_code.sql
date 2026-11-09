UPDATE "flowModels" SET options = jsonb_set(options::jsonb, ARRAY['stepParams','jsSettings','runJs','code'], to_jsonb('
const { Card, List, Button, Tag, Empty, Typography, Space, message, Popconfirm } = ctx.libs.antd;

const ENABLED_WF = [396745412444160, 396743055048704, 396746379231232, 396799131385856];
const WF_TITLE = {
  396745412444160: ''请假审批'',
  396743055048704: ''缴费审核'',
  396746379231232: ''退学审批'',
  396799131385856: ''报名审核'',
};
const FALLBACK_ACTIONS = {
  396745412444160: [{key:''approve'',title:''通过'',values:{status:''approved''}},{key:''reject'',title:''驳回'',values:{status:''rejected''}}],
  396743055048704: [{key:''pass'',title:''审核通过'',values:{status:''approved''}},{key:''deny'',title:''拒绝'',values:{status:''rejected''}}],
  396746379231232: [{key:''approve'',title:''通过'',values:{status:''approved''}},{key:''reject'',title:''驳回'',values:{status:''rejected''}}],
  396799131385856: [{key:''pass'',title:''审核通过'',values:{status:''approved''}},{key:''deny'',title:''拒绝'',values:{status:''rejected''}}],
};

async function getNodeActions(nodeId, workflowId) {
  try {
    const n = (await ctx.api.request({ url: ''flow_nodes:get'', params: { filterByTk: nodeId } }))?.data?.data;
    const forms = (n?.config?.forms) || {};
    const formKey = Object.keys(forms)[0] || ''review'';
    const actions = (forms[formKey]?.actions) || FALLBACK_ACTIONS[workflowId] || [];
    return { formKey, actions };
  } catch (e) {
    return { formKey: ''review'', actions: FALLBACK_ACTIONS[workflowId] || [] };
  }
}

async function loadTasks() {
  const res = await ctx.api.resource(''workflowManualTasks'').listMine({ pageSize: 100, filter: JSON.stringify({ status: 0 }) });
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
    await ctx.api.resource(''workflowManualTasks'').submit({ filterByTk: task.id, values: { result: { [task.formKey]: { ...(action.values || {}) }, _: action.key } } });
    message.success(''已提交：'' + action.title);
    await draw();
  } catch (e) {
    const msg = e?.response?.data?.errors?.[0]?.message || e.message || String(e);
    message.error(''提交失败：'' + msg);
  }
}

async function draw() {
  ctx.render(<Card size="small"><Typography.Text>待办加载中…</Typography.Text></Card>);
  let tasks = [];
  let err = null;
  try { tasks = await loadTasks(); } catch (e) { err = e?.message || String(e); }
  if (err) {
    ctx.render(<Card size="small"><Empty description={''加载失败：'' + err} /></Card>);
    return;
  }
  ctx.render(
    <Card size="small" title={''待办任务（'' + tasks.length + ''）''}>
      {tasks.length === 0 ? (
        <Empty description="暂无待办任务" />
      ) : (
        <List
          dataSource={tasks}
          renderItem={(t) => (
            <List.Item
              actions={(t.actions || []).map(a => (
                <Popconfirm key={a.key} title={''确认「'' + a.title + ''」？''} onConfirm={() => submit(t, a)}>
                  <Button size="small" type={a.values && a.values.status === ''rejected'' ? ''default'' : ''primary''} danger={a.values && a.values.status === ''rejected''}>
                    {a.title}
                  </Button>
                </Popconfirm>
              ))}
            >
              <List.Item.Meta
                title={<Space><Tag color="blue">{WF_TITLE[t.workflowId] || (''流程#'' + t.workflowId)}</Tag><Typography.Text strong>{t.title}</Typography.Text></Space>}
                description={''创建于 '' + String(t.createdAt || '''').replace(''T'', '' '').slice(0, 19)}
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
}

await draw();
'::text))::json WHERE uid = '72hgyrjlwza';