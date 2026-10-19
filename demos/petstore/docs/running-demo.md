# 构建与运行

需要JDK17、Maven及项目依赖。仓库根目录：

```bash
mvn -pl :petstore-demo -am package -DskipTests
./demos/petstore/run-demo.sh web
```

网页默认http://127.0.0.1:8086。允许局域网访问：

```bash
SPP_WEB_HOST=0.0.0.0 ./demos/petstore/run-demo.sh web
```

SPP_WEB_PORT可改端口。已完成构建时可设置SPP_DEMO_SKIP_BUILD=1跳过重复构建。网页脚本默认构建生产代码和测试代码，但跳过测试执行。

脚本运行公共GeneratedWebServer，加载APP web目录、PHY资源和生成服务。默认持久化数据库在demos/petstore/target/petstore；重启保留数据，mvn clean会删除该目录。SPP_PETSTORE_JDBC_URL可指定其他H2地址。

APP 的 `web start` 自动执行客户域、产品域和商店初始化，首次提供商户、四件商品及对应库存、供应和结算记录；已有记录不会在重启时重复灌入。页面上预填的客户资料不是已注册账号，购物客户仍须点击 Register 注册。账户余额和可售库存初始为零，充值、入库步骤见下文。

局域网 HTTP 下浏览器可能不提供 `crypto.randomUUID()`，网页以 `crypto.getRandomValues()` 生成请求流水号。修改页面脚本后可用 Ctrl+F5 刷新缓存。

## Java验收

以下命令会实际执行测试，仅在需要回归时使用：

```bash
./demos/petstore/run-demo.sh examples
./demos/petstore/run-demo.sh examples happyPathExample quantumLedgerExample
mvn -pl :petstore-demo -am test -Dtest=PetstoreScenarioTest -Dsurefire.failIfNoSpecifiedTests=false
```

examples保留为脚本命令名称，内部已改为JUnit，不执行APP examples或GeneratedExampleRunner。28个测试方法位于src/test/java；默认独立内存数据库，不操作网页数据库。持久化重启测试启动两个独立子JVM并使用专用临时文件数据库。

生产生成Java、SQL/OpenAPI与目录仍在target；测试编译结果在target/test-classes，JUnit执行报告在target/surefire-reports。旧target/spp-examples/evidence是历史APP验收证据，不代表当前测试结果。覆盖与测试边界见[Java验收](java-tests.md)。

浏览器请求流水号回归可运行 `node --test demos/petstore/src/test/browser/RequestIdTest.cjs`。安装 Playwright 并准备独立测试数据库后，`SPP_DEMO_URL=http://<局域网IP>:8089 node demos/petstore/src/test/browser/PetstoreLanCartRegression.cjs` 验证 HTTP 兼容、注册、充值、入库、添加两个不同商品及下单；该流程会写入测试客户和订单，不应指向正在手工使用的数据库。

## 当前需求与设计核对方式

本轮执行test-compile -DskipTests：编译生产源码和Java测试，但不执行任何回归、HTTP业务或浏览器流程。生成成功及测试编译成功均不代表运行验收通过。其他模块中的旧嵌套场景尚未迁移。

## 新模型与旧数据

当前模型移除了通用命令、技术业务字段及集合包装，修改了键、外键投影和聚合快照。原 target/petstore 数据库已保留，未自动迁移。运行新版请指定独立数据库，例如 SPP_PETSTORE_JDBC_URL='jdbc:h2:file:/tmp/spp-petstore-new-model'；不要用 clean 清除旧数据，也不要把旧快照直接当成新模型验收。本文运行命令未在本轮执行。

新演示库启动后余额和库存均为零：先注册买家，再点击“第三方结算充值”（示例金额 5000），点击“从供应来源入库”（示例每商品 10）。注册、充值、入库为独立场景，后两者有明确的负向来源账户，守恒入账；重新启动不自动重复充值或入库。
