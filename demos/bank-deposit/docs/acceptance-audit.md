> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 纯源语言最终验收核对

状态：最终clean verify及逐项产物核查通过，全部手写Java为0，945项公共JUnit与86源入口均通过。详见[最终验证](source-only-final-verification.md)。

本次范围依据[需求](requirements-and-functions.md)、[语言约束](source-language-only.md)和AGENTS.md：一般现金、普通/呆账透支偿还、小数数学案例及对应现金冲正，包含P1–P4、恢复和原验收责任。生产银行替代与本次重构完成不是同一范围。

| 要求 | 权威证据位置 | 最终验收条件 |
|---|---|---|
| 业务仅SPP、部署APP、物理PHY | src/main/spp全部源；cboddeposit.app/phy；源目录Java清单 | 主/测试/启动/仓储/辅助均无手写Java，生成Java仅在target |
| 完整事务边界和模式 | 92 commitCashDepositRecords、93 commitCashReversalRecords；98/99b身份和审计边界；99zv Saga | 账户、成交、八分录、关联、审计及量子值共同提交，源码能直接读出模式 |
| P1数字及分量 | 00内核、99p/99pa/99pb、99y；PHY numeric double as BigDecimal | 普通先息后本、呆账先本、冻结/授权、本金边界、小数及余额关系独立断言通过 |
| P2共享业务规则 | 20/30/40/50/60；99o/99q/99r/99s/99t/99u/99v/99x | 日期、分档、受理、拒绝、警示、授权重验、收费及银行资格通过 |
| P3端到端存入 | 96/97/98；99d/e/f/h/i/zh及完整报告 | 现金、债务和小数从查询到实际持久更新；六成交48分录；待授权及重放不重复更新 |
| P4原成交驱动现金冲正 | 70/90/99/99b；99j/k/l/w/zu及实际报告 | XBOD同/跨日与隔夜Mode2；原金额/退费/分录驱动；保持后续存款与当前积数 |
| 原证据与计划复核 | 91/93提交内锁定查询；99ze/zf/zg/zu/zx | 原凭证篡改、过期版本、同版本快照篡改及身份重用拒绝，无部分写入 |
| 并发及身份 | 99zi/zo/zx及APP屏障 | 实际两路竞争到达，唯一更新及真实回滚/查询恢复，不以顺序调用代替 |
| 事务失败与审计 | 99n/zl/zm/zq/zr/zs；99c/zb | 四真实JDBC提交点、未知结果查询、分录中途失败、审计不可用及原异常保留 |
| 量子保障 | 95、99zp/zpa、native journal/value查询 | 完整事务失败无量子残留，账户隔离、错误原值拒绝、极小金额精确保存、差额守恒 |
| Saga业务恢复 | 99zv六根入口，APP compensate、PHY saga | 成功、已提交后失败、无成交、资格拒绝、重试和完成记录失败分别有真实查询证据 |
| 报告及跨JVM | 99zya/b/c/d/da/e/f；APP五个restart组 | 两个新JVM、空参与者、文件库持久查询；十案例六成交五未执行候选；四实际冲正32反向分录20量子行；逐案例输入/授权/来源和实际重放返回 |
| 全部原责任迁移 | source-example-coverage.md及source-report-migration.md | 原14主类、21测试族与嵌套class全部不存在；不把银行Java挪入框架/模板 |
| 干净生成与回归 | 本轮Maven终态、surefire XML、APP86汇总及证据JSON/MD | 从空target生成编译，945公共JUnit与86入口无失败/跳过；逐项检查实际产物 |
| 文档与对比 | requirements、implementation-path、decisions、source-map、spp-vs-cobol-java | 分层、实施、语法缺口与通用补齐能力、比较收益/成本及验收证据同步 |

## 能力边界

只证明已选路径及明确fixture：原COBOL未执行、银行黄金/真实ART费率未取得；日元和PIC截断差异保留，不能声称全产品或逐位等价。跨库量子部署、生产灾难恢复、跨进程Saga自动扫描、转账/托收及开户生命周期反交易不在已确认第一批范围。

报告的productionReplacementVerified=false表达生产替代范围，不能解读为本次纯源重构Goal状态。普通/不良/小数候选没有提交；实际现金冲正是另一个新业务交易，Saga恢复不等同于量子技术回滚。

此前阶段失败、修正与构建记录见[历史验收](acceptance-history.md)，具体源责任及原始日志见[覆盖责任](source-example-coverage.md)和[重构记录](source-only-refactoring.md)。
