# 中文存款工作台

界面在 `src/main/resources/web/`，由现有 GeneratedWebServer 作为静态资源提供。后端仍全部由 SPP/APP/PHY 生成，无手写 Java 业务或 Java HTTP 控制器。

## 演示步骤

1. 设置客户账号、现金结算账号、业务日期。首次使用新数据库，在“账户开立”中先建立银行内部户，再开立客户账户。
2. “现金存入”输入金额并提交。界面显示客户及资金对方余额、存入回执、八槽分录，并记住原存入回执号。
3. “现金冲正”先试算，再确认正式冲正。修改顶部业务日期可测试跨日；Mode2 开关仅作为场景输入，规则仍由服务判断。
4. “账务查询”按账号查询资金，按回执号查询真实持久化的存入/冲正合约与分录。最近回执列表只保存在本浏览器，不代表服务器交易全集；点击回执会恢复对应客户、现金结算和银行内部账户，业务日期保持当前选择。
5. “高级测试”选择场景生成完整参与者 JSON，按需修改业务参数，点击“执行 JSON 请求”。常规按钮不会使用这个编辑器中的改动。

业务拒绝保留后端错误码。fail 返回的失败、恢复状态不会显示为成交成功。通信中断时显示“结果未确认”，页面不会自动重试更新；应先核对账务。失败请求不展示输入中的零值或候选分录为已确认余额/成交；通信失败会清除上一笔结果。办理中账号、表单和 JSON 暂时不可编辑，防止请求与显示上下文错配。页面不计算资金、费用、利息或补偿，不实现校验业务规则。

## 与 OpenAPI 的关系

这是定制的中文工作台，不是通用 OpenAPI UI 生成器。`templates.json` 是输入骨架，从编译输出 OpenAPI 的属性类型及枚举、SPP 场景的参与者声明生成；布局、表单、动作和结果展示为手工编写。金额输入使用字符串，响应数字以原始十进制文本保留，避免浏览器浮点运算修改金额。

变更参与者后，先运行 Maven 生成，再刷新输入骨架（需要 PyYAML）：

```bash
python3 demos/bank-deposit/tools/web-templates.py
```

表单中的柜员、授权、协议和科目是可见的演示输入，沿用验收样例，不代表生产环境可信外部事实。没有在前端新增偿还、收费或冲正算法。

## 服务入口

APP 显式暴露开户、存入、试算、冲正及查询场景。新增 `readDepositAccount` 查询账户资格、积数和资金账户，`readCashDeposit` 查询原成交及分录；两者只有查询和校验，没有事务或更新。默认原子 CRUD 仍不直接暴露 HTTP。

## 启动

```bash
./demos/bank-deposit/run-demo.sh web
```

默认地址 http://127.0.0.1:8089/ ，数据保存到 `target/xbod-deposit` H2 文件。`mvn clean` 会删除 target 下的演示数据库；需要长期保留可用 SPP_XBOD_JDBC_URL 指向其他路径。

局域网演示：

```bash
SPP_WEB_HOST=0.0.0.0 ./demos/bank-deposit/run-demo.sh web
```

分库演示使用 `SPP_ENVIRONMENT=testing`。已有构建可加 `SPP_DEMO_SKIP_BUILD=1`。数据源、端口等继续使用 run-demo.sh 现有环境变量。页面没有登录功能，按演示服务使用。

## 验证

`XbodHttpTest` 核对静态首页、APP 暴露的账户查询、界面防重、冲正和默认原子服务不可访问。`tools/web-acceptance.cjs` 使用 Playwright 驱动真实浏览器，从全新账号开始完成开户、精确小数存入、负数拒绝、试算、正式冲正、回执查询、页面刷新及手机布局，断言无浏览器脚本错误。

```bash
# Playwright 需安装于当前 Node 环境；DEMO_URL 指向隔离测试服务。
DEMO_URL=http://127.0.0.1:18089 node demos/bank-deposit/tools/web-acceptance.cjs
```

脚本使用独立账号但会写入真实演示交易，宜连接临时测试库。默认 Chrome 路径 `/usr/bin/google-chrome`，可用 CHROME_BIN 修改。

2026-10-13 实际验证：develop/testing 的 XbodHttpTest + XbodReversalPreviewTest 各 3 项通过；两环境的 Playwright 完整浏览器流程均通过，包含金额 100.005 的原样显示、负数存入拒绝后余额保持、试算无写入、正式冲正归零、服务端回执查询及 390px 移动布局。日志 `/tmp/xbod-web-tests.log` 与 `/tmp/xbod-web-testing-tests.log`。

后续交互验收：develop 的浏览器全流程追加通过历史回执账户恢复、高级 JSON 缺原成交拒绝、处理中表单冻结、技术网络中断后状态待确认及结果清理；无浏览器脚本错误。记录 `/tmp/xbod-ui-followup-browser.log`。未重复运行已通过的后台回归，新增变更仅涉及页面交互。
