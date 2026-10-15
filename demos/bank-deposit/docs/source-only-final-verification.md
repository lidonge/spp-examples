> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 纯源重构最终验证

2026-10-09完成 `mvn -pl :xbod-deposit-demo -am clean verify`，日志 `/tmp/spp-source-only-final-clean-validation.log`，耗时15分19秒，BUILD SUCCESS。

- 主/测试/其他源目录手写Java均为0；14原主类、21原测试族及嵌套class不存在，JAR不含旧银行主类。
- 从空target生成并编译4207个Java文件。业务、事务、案例、断言和中文报告内容来自SPP；APP绑定查询更新/部署/验收控制，PHY绑定BigDecimal及共同JDBC/量子资源。
- 945项公共JUnit通过：lang303、appframe537、generator105，零失败/错误/跳过。银行已无手写JUnit，86个APP入口独立执行，86通过、0失败。
- 五组两独立JVM验收通过：冲正身份与后续交易、待授权续接、现金报告、完整存款报告、实际冲正报告。每阶段从空参与者查询文件数据库，保持打开只限单JVM，下一JVM重新打开；60秒时限不变。
- 96份JSON与96份Markdown状态均PASS，位于target/spp-examples/evidence。存款resume：十案例、六实际成交48分录、五未执行候选、2300/版本3/积数2200、拒绝EN432/E1043、精确本金0.001和逐案例请求/日期/授权/来源；重放当前2200/版本2而返回原700/版本1。
- 冲正resume：四实际冲正32反向分录、20量子日志且差额和0；首笔冲正及重放/重复拒绝保持14行，现金1700/版本4/积数2200，退款2；普通/不良/小数债务恢复原分量、保留当前积数，后续存款保持。
- 完整回归还覆盖实际并发、快照/凭证篡改、版本竞争、四JDBC提交点、未知结果查询、分录中途失败、审计不可用、精确量子存储及六种Saga恢复。具体入口责任见source-example-coverage.md，事务源码为92/93/98/99b/99zv。
- 公共Java/模板搜索未发现银行旧类或KSADEP0/GSA01102/EN432/F0554硬编码；没有把银行业务挪入框架。公共扩展及语义测试见重构记录。

最终报告：`target/spp-examples/evidence/depositCompleteReportResumeExampleRun.json`及.md，`depositActualReversalReportResumeExampleRun.json`及.md。这是已确认范围的SPP纯源重构验收，不是生产银行替代或原COBOL黄金等价；报告productionReplacementVerified=false的范围含义保持。

需求P1–P4、完整事务/恢复、全部手写实现责任、启动/存储/报告及文档迁移均已完成；核对表见acceptance-audit.md，实施和对比见implementation-path.md、spp-vs-cobol-java.md。
