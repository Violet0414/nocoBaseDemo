-- D75: 3 个 admin 排课入口页 iframe src 加 ?embed=1（main Portal embed 模式）
-- 搜索串含 JSON 转义引号 \"，用 dollar-quote 避开 shell/SQL 双层转义
UPDATE "flowModels" SET options = replace(options::text, $$x/main/schedule/board\"$$, $$x/main/schedule/board?embed=1\"$$)::json WHERE uid='s96hi0xk166';
UPDATE "flowModels" SET options = replace(options::text, $$x/main/schedule/week\"$$, $$x/main/schedule/week?embed=1\"$$)::json WHERE uid='ykhawbr91vm';
UPDATE "flowModels" SET options = replace(options::text, $$x/main/schedule/seats\"$$, $$x/main/schedule/seats?embed=1\"$$)::json WHERE uid='6nia4y84u97';
