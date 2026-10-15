# Conserved opening and transfer regression — 2026-10-12

本页记录资金/库存守恒回归时的实现状态；后续 KI-003 已由 [分库零记录技术恢复](quantum-opening-recovery.md) 完善，旧“残留零地址待处理”描述保留为当时的历史记录。

本轮 Goal 延续回归，先修正业务模型：开户零余额，库存零初值，第三方结算账户/库存供应来源也从零开始；独立充值及入库场景按双边增减守恒成交，来源 bounds 不设下限。没有手写业务 Java。

旧 KI-001 的描述归因不准确：原注册直接赋 5000、开店直接赋 10 库存，是业务模型混入非零入账。新模型用普通服务建立零参与者、量子服务转入非零余额/库存，不通过将注册伪装为技术启动初始化绕行。框架零事实建立采用 missing-only，不产生量子交易流水，已有值不覆盖；分库失败残留零地址的生命周期仍单独记录，不承诺开户跨库强原子性。

实施证据：SPP 新增 SettlementAccount、StockSupply、WalletFundingAgreement、StockReceiptAgreement、fundShopWallet/receiveShopStock。APP 定义主键及 web 暴露、防重；PHY 沿用既有统一量子系统。浏览器与 Java 测试组合独立生成场景，无自动注册赠款。编译器默认共享资源不再要求相同属性集合，推导守恒组与显式固定属性契约分开；显式冲突测试保留。

验收路径：develop 生成与全部 Petstore 场景（含零开户、来源负值及每笔流水守恒）、框架/语言/生成器/Seata 回归、中文网页；testing 重新生成，三个 JVM 独立数据库启动、完整网页及重启。所有测试使用隔离库，现有常驻演示服务与数据库不改动。未决问题登记 known issue 后继续独立验证，不 block。

当前状态：实现与 develop/testing 回归已完成；未决技术生命周期及补偿议题保留在 known issues，不阻塞本轮验收。

## 已取得证据

独立新测试 zeroOpeningAndExternalTransfersAreConserved 通过：零开户、零库存；独立充值后钱包 5000、结算来源 -5000；独立入库后可售 10、来源 -10；逐 transaction_id 汇总量子流水增减为零；非法充值/入库不改变成交事实。日志 `/tmp/spp-conserved-transfer-test.log`，BUILD SUCCESS。

采用现有跨域外观声明 `atomic update receiveInventory(...)` 自动绑定 inventory 域实际 `quantum update` 实现，避免将外观错误地声明为本域空量子实现。真实 develop Chrome 完整流程（显式零开户→充值→入库→购物/支付/履约/退款/取消/预约及英文目录）通过，pageErrors=[]，日志 `/tmp/spp-bootstrap-develop-8dq0k4hk/browser.log`，服务已停止。早期生成及第一次网页失败日志只作诊断，不作为通过证据。

联合回归 `mvn -fae -pl petstore-demo,appframe-seata -am test -Dspp.environment=develop` 最终 BUILD SUCCESS：lang 340、appframe 579、generator 105、appframe-seata 20、Petstore 34，共 1078 项全部通过，无失败/错误/跳过。日志 `/tmp/spp-conserved-reactor.log`。包含所有原场景及新增零开户/外部双边转入验收。

最新版 develop Chrome 网页再次通过，补充断言注册钱包 0、结算来源 -5000、各商品入库后可售 10、库存供应来源 -10，随后完成原购物/退款/预约流程，pageErrors=[]。日志 `/tmp/spp-bootstrap-develop-mhlx8i3_/browser.log`；测试服务已停止。

## testing 分库阶段

`mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=testing` BUILD SUCCESS，日志 `/tmp/spp-conserved-testing-package.log`，只表示生成/编译/打包。首次 testing 验证 `/tmp/spp-bootstrap-testing-ol4gdd43` 三 JVM 及重启全部就绪，零开户、结算充值及供应入库通过，已解除旧 KI-001；下单因 `Undefined repository property lineNumber on java.util.LinkedHashMap` 失败。停机后只读量子库证实钱包 5000、结算 -5000、现金 0；每商品所有库存及来源合计 0，每笔量子流水合计 0。证据 ledger-audit.log。

该下单错误是通用仓储访问器不支持 JSON 快照 Map，并非新的 SPP 业务规则：访问器现支持嵌套 Map 与省略的 nullable 字段，普通 Java 对象仍对不存在属性报错。新增 ObjectPropertyAccessTest 验证该行为，appframe 全套 580 项通过，日志 `/tmp/spp-conserved-map-appframe.log`。后续 testing 完整网页已通过，见下文。

第二次 testing 的编号 setter 错误进一步证明问题根因是跨域属性回填只用 raw List 类型，使 `ShopOrder.lines` 元素退化为 LinkedHashMap（develop 在入库更新前已经保存明细，testing 量子先执行使错误暴露）。LocalDomainServices 现依据 setter 泛型构造 JavaType 回填，量子延迟回填回调也使用相同类型。新增 LocalDomainCollectionFactsTest 通过，appframe 全套 581 项通过，日志 `/tmp/spp-conserved-generic-appframe.log`。没有给业务编号逻辑补上 Map setter 来绕过泛型错误。

最终 testing 实测目录 `/tmp/spp-bootstrap-testing-l5oqppgs`：customerService/productService/petstore 三个独立 JVM、四个隔离 H2 文件库（customer/product/shop/ledger）；完整 Chrome 网页通过（含来源余额与零开户断言），pageErrors=[]，商店停机再启动 readiness=true。全部测试进程已停止。旧 KI-001 已解决，无依赖步骤跳过；已有未决技术生命周期和补偿议题继续留在 known issues。

## 最终联合回归与守恒核对

最终联合回归（包含 Map 读取与泛型集合回填修复）`mvn -fae -pl petstore-demo,appframe-seata -am test -Dspp.environment=develop` BUILD SUCCESS：lang 340、appframe 581、generator 105、appframe-seata 20、Petstore 34，共 1080 项全部通过，失败/错误/跳过均为 0。日志 `/tmp/spp-conserved-final-reactor.log`。

testing 停机重启之后，以只读方式核对隔离量子库：钱包＋经营者现金＋第三方结算余额合计为 0；每个 SKU 的可售＋预留＋已售＋供应来源合计为 0；每个 transaction_id 的流水增减合计为 0。全部通过，证据 `/tmp/spp-bootstrap-testing-l5oqppgs/ledger-audit.log`。

最终 develop 生成产物再执行一次完整 Chrome 流程也通过，浏览器 exit=0，日志 `/tmp/spp-bootstrap-develop-14zgz50m/browser.log`；测试服务已停止。文档 worktree `docs/writing` 于最后验收前复制了当前 Markdown 快照，之后的回归记录仅更新主目录，以免覆盖用户文档编辑。
