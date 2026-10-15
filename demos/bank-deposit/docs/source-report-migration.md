> 历史文档：本文件描述重构前的实现或验收，不代表当前源码与测试结果。现行方案见 [本轮重构](latest-petstore-refactoring.md)；旧源已移至 `legacy-source/`。

# 声明式业务证据与报告迁移

状态：通用证据导出已验证；现金聚合报告源已实现，正在编译及两JVM验证，完整银行聚合报告尚未完成。旧 DepositDemoReportTest 与 CashDepositReversalTest 的报告责任仍须保留。demo 不允许手写 Java 报告程序，也不允许把银行报告模板及公式移入公共框架。

## 分层

SPP 定义报告参与者、案例事实、独立预期和验收条件。案例的实际结果必须来自生成服务的执行及持久查询，不能由预期结果反填。APP/PHY 继续承担已有服务部署、数据库及故障配置。公共执行器仅导出执行结果、参与者事实及通用可读格式，不判断银行结果、不计算反交易、不生成银行专属报告内容。

原公共框架仅有控制台 PASS/FAIL；现已补齐并验证通用证据导出：每个已声明入口的参与者执行后事实、执行状态及错误事实生成 JSON 和 Markdown，文件目录由技术配置提供。中文标题、解释、业务状态及范围标志由 SPP 的 String 字段明确提供，不在框架 Java 中硬编码。

## 原存款报告责任

保持十组案例和六笔实际成交的独立证据：现金600及收费2；普通债务的利息30/催收息20；不良债务本金50；业务数学小数本金0.001；授权等待不更新，授权通过成交；原身份重放不再次更新；下一业务日日累计100、积数2200、最终余额2300；账户控制拒绝EN432和日期拒绝E1043。冻结、授权、积数与原银行资格事实均由持久查询独立检查。

五个金融与分录反向候选明确未执行，既不能与现金冲正混称，也不能假装其已成交。保留预期净余额1700、零/原收费2、分录总额602等独立事实。源报告明确 COBOL 未执行、生产银行配置未取得、未完成生产替代验证；该业务证据范围不等于 Codex 重构 Goal 的运行状态。

使用声明式两阶段 restart 入口让两个独立 JVM 关闭、重开文件数据库。恢复阶段独立查询原六笔成交及48条分录、现金账户版本3/余额2300/积数2200、原成交银行资格及重放审计，并读取持久报告事实。仅 JSON 导出成功或同一进程重建对象不替代此责任。

## 实际现金冲正报告责任

四笔实际现金冲正的原成交、后续业务、收费退款、账户增量、分录和持久量子日志单独列出，候选与实际执行在事实类型及状态中明确区分。原有现金、普通债务、不良债务、小数冲正源场景已执行；聚合报告须使用查询结果，并核对实际交易数和相应量子记录，不能用已有 PASS 字样当作报告证据。

## 实施及删除门槛

1. 为通用执行器的 JSON/Markdown 导出建立与银行无关的运行测试，核对精确数字、数组/嵌套参与者、失败记录及输出位置。
2. 编写报告角色与银行案例源场景、查询/持久绑定以及独立预期，复用已有 SPP 业务服务。
3. 执行两 JVM 文件数据库案例和四笔实际冲正报告，核对导出文件与实际查询。
4. 责任通过后删除两个旧报告测试及其依赖主Java；与其他迁移一起 clean verify，核查源文件和旧class均已消失。

这份设计不认定以上能力已经实现；最终证据需追加实际构建、入口、导出文件与查询结果。

公共导出器 ExampleEvidenceWriter 及三项非银行测试已编写，尚未编译测试，也未接入GeneratedExampleRunner。只采集@JsonProperty声明字段，排除运行辅助getter；JSON与Markdown读取均保持BigDecimal/BigInteger精度，附加失败事实用循环引用检测避免递归异常对象。银行81入口当前运行的插件JAR是在此代码写入前打包，不能把本轮银行运行结果记作导出器验证。

通用能力实现进展：导出器已接入GeneratedExampleRunner，技术配置spp.examples.evidenceDirectory启用导出，未配置时保持原执行行为。两个独立JVM各自导出事实，父进程以__restart后缀写整组结果，不覆盖阶段证据。导出器3项、运行器6项、场景物理参与者2项，共11项针对性JUnit全部通过，日志 /tmp/spp-source-scenario-evidence-runner-corrected-validation.log。首轮集成暴露父进程失败覆盖setup阶段文件，已修正并由失败第二阶段测试明确保护。银行POM配置target/spp-examples/evidence目录；尚未完成十案例/六交易/五未执行候选以及四笔实际冲正的银行聚合源报告，不据通用导出测试删除旧报告责任。

## 具体源实施布局

拟拆为四组较小文件：报告角色与独立预期；十个存款案例及六个成交查询；五个未执行候选及四笔实际现金冲正；重启恢复阶段的独立读回校验。案例使用固定槽角色数组，源原子服务复制每个案例的当时事实，避免后续交易改变早期报告；实际交易和分录另行通过查询填入，不能拿工作内存或预期值代替已成交证据。恢复阶段须从空参与者开始，用稳定报告身份读取持久报告，并重新查询六笔交易、原48分录与账户。

现金序列使用已有StoredPreparation fixture的日期语义：积数日初始化20261007，600和1500两笔同日不增加积数，次日100以此前2200余额积一天，最终版本3/余额2300/积数2200。授权等待插在第二笔实际成交之前，故等待保持第一笔版本1/700。原身份重放返回原成交700，同时当前账户保持版本2/2200。失败EN432与E1043各使用独立账户，保持版本0，不计入六笔实际成交。

五候选以600现金零/原收费两种，以及普通/不良/小数债务三种为基础，分别复制完整只读反向计划和原分录，不调用提交服务；同时查询原账户/关联/审计确认未更新。四笔实际冲正复用完整executeCashReversal，并独立查询交易、关联、分录、原及后续业务与量子日志；现金账户2300撤销600后1700、后续1500/100保留，三类债务恢复原分量且当前积数保持。六笔存款加四笔冲正共20条量子记录，不能用候选数推算成实际量子记录。

报告原始阶段和实际冲正阶段分别采用两阶段restart入口/独立文件数据库，以同时证明原报告2300账户与冲正后1700账户的持久事实；它们是不同阶段，不覆盖或混称同一时刻的状态。源SPP String字段提供中文标题、范围、未执行候选说明与预期净余额；生产替代验证标志保持false，并明确它不是Codex重构Goal状态。

以上为接下来的实施约定，尚未创建或执行这些聚合源文件，不据此删除剩余两份旧测试或13份主Java。

## 首批聚合源实现（待验证）

已新增 `cboddeposit-99zya-report-model.spp` 和 `cboddeposit-99zyb-report-cash-scenarios.spp`，APP显式绑定报告持久服务及两JVM入口。现金报告执行600、等待授权1500、授权成交、原身份重放、次日100；独立查询三笔成交、24条分录与审计；复制两个未执行反向候选。报告保存为源Role，恢复阶段从空参与者读取后重新查询三笔业务，并用源 `sameFacts` 与持久报告核对。保存报告自身的事务边界显式写在SPP的 `transaction quantum` 中。中文标题和生产验证范围标志均在SPP定义。

此批尚未编译或运行，且仅覆盖现金报告部分；普通/不良/小数债务、拒绝案例、完整六成交48分录、五候选和四实际冲正20量子记录仍需后续扩展。旧两测试及13主Java保持待迁移状态，不据代码存在宣称责任通过。

现金报告首轮编译失败：原子check直接调用另一个check不符合现有语法。已将复用服务调用移至恢复Scenario，未扩展语法或写银行Java绕行。修正构建日志 `/tmp/spp-source-cash-report-corrected-validation.log`；实际运行结果仍待验证。

## 完整报告源已接入（待编译验证）

新增99zyc模型、99zyd十案例、99zye四实际冲正、99zyf跨JVM恢复四个文件，APP绑定两组新的文件数据库重启入口。普通债务、不良债务和业务小数使用同支行零手续费配置，保留30/20、50和0.001的独立预期。拒绝案例分别实际执行EN432和E1043并读取零成交、零分录、版本0及一笔Rejected审计。源报告汇总现金三笔与债务三笔为六成交48条分录；五个未执行候选按类型分别保留，实际现金冲正使用独立交易及证据。

存款报告要求读取12条已提交量子日志；实际冲正报告要求20条、差额和为0、四账户及四清算对手的持久值。现金冲正后1700/版本4，保留2200积数、后续1500和100交易，债务冲正恢复原分量并保留已成交后的积数。SPP明确报告保存的quantum边界；所有成交、冲正、查询与校验复用源服务，未添加银行Java。

两组新入口尚未编译运行；当前日志spp-source-cash-report-corrected-validation对应较早84入口生成版本，不含这两个完整报告入口。当前APP源码共86入口，不能把源码计数当成已通过入口数。

首批现金报告独立验证通过：GeneratedExampleRunner选择depositCashReportSetupExampleRun，两个新JVM完成setup/resume，日志 `/tmp/spp-cash-report-selected-restart-validation.log`。JSON精确读回和中文Markdown核查通过（证据目录 `/tmp/spp-source-cash-report-evidence`）；三成交、24分录、当前2300/版本3/积数2200、两候选未执行及借方600/602均匹配。此验证使用84入口生成版；完整86入口仍待下一轮编译。进一步把银行资格、首笔F0554及三个收费2/2.5/2的独立预期加入源校验，尚未执行增强版。


84入口增量验证完成：日志 `/tmp/spp-source-cash-report-corrected-validation.log`，`mvn -pl :xbod-deposit-demo -am verify -Dmaven.test.skip=true` 成功，84源入口全部通过（含新增现金报告两JVM组）。此命令跳过JUnit及测试编译，不能替代此前948项/83入口的clean证据。现金报告增强校验与两个完整报告入口之后接入，当前86源码的package生成正在运行 `/tmp/spp-source-complete-report-generation.log`，未认定86入口已通过。

86源码package成功：日志 `/tmp/spp-source-complete-report-generation.log`，4212个Java文件完成编译；本次跳过JUnit且package不运行APP入口。增强现金报告、完整存款报告及实际冲正报告的三个独立JVM组已启动选择执行，日志 `/tmp/spp-source-complete-report-selected-validation.log`、导出目录 `/tmp/spp-source-complete-report-evidence`，终态结果尚待确认。

## 完整报告首轮运行与通用注册修正

三个报告组首轮为1通过/2失败：增强现金组通过，完整存款与实际冲正组均stage0超过公共执行器固定60秒，阶段日志为空，不能记为业务通过。日志 `/tmp/spp-source-complete-report-selected-validation.log`。独立诊断进程实际线程栈显示LocalGeneratedServiceRuntime批量remember每项后全目录幂等刷新，形成重复元数据遍历；另一个栈反映诊断文件数据库放在/tmp大目录导致H2反复目录扫描，该诊断进程已终止，不当作正式重启证据。

公共注册现改为整批记忆后统一刷新，单项注册仍即时刷新；未改银行规则、SPP边界、报告断言或60秒时限。非银行BulkGeneratedServiceRegistrationTest通过，八服务批量仅八次元数据读取，单项替换后仍刷新。日志 `/tmp/spp-bulk-registration-validation.log`。完整框架回归及三个真实文件数据库组正在重新运行，分别为 `/tmp/spp-bulk-registration-framework-validation.log` 和 `/tmp/spp-source-complete-report-fast-validation.log`；新结果尚未确认，旧银行Java保留待迁移。

## 完整存款报告责任已替代

通用注册修正后，增强现金与完整存款报告的两个独立JVM组均通过。框架537项JUnit零失败零跳过。完整报告resume导出的JSON/中文Markdown额外核对十案例、六实际成交48分录、五未执行候选、30/20与50与0.001分配、EN432/E1043拒绝版本0、现金2300/版本3/积数2200及12真实量子行均通过。证据 `/tmp/spp-source-complete-report-fast-evidence/depositCompleteReportResumeExampleRun.json` 与同名.md，运行日志 `/tmp/spp-source-complete-report-fast-validation.log`。据此删除DepositDemoReportTest；当前13主Java、1测试Java（三项CashDepositReversalTest）仍待迁移。

实际冲正报告首轮失败为 `REPOSITORY_SCALAR_QUERY_AMBIGUOUS`，已定位新fixture把冲正重放attemptId取成SOURCE-REPORT-CASH-REPLAY，和同一报告的存款重放身份相同。两笔不同trade审计真实存在，单身份查询因歧义拒绝；未放宽查询或断言。已将冲正重放身份改为SOURCE-REPORT-CASH-REVERSAL-REPLAY，须经源再生成及实际执行确认，尚不据此删除最后冲正测试和银行主实现。

## 最终报告逐案例来源门槛（源码已补，待生成执行）

按requirements-and-functions的逐案例证据要求，现金报告新增实际等待/授权/重放命令，以及重放时的当前账户2200/版本2和实际返回原账户700/版本1。完整案例新增request、businessDay、authorizationLevel、sourceProgram、sourceParagraph、expectedOrigin，SPP在实际执行点复制事实，并要求十个案例全部有输入和来源；小数案例明确使用业务数学预期，其余源码推导加demo配置，不声称银行黄金或COBOL执行。

这些增强是在unique-attempt的86源生成已读取源模型后加入，当前package验证的是修正身份的前一生成版本；须在删除旧Java后的最终clean verify中重新生成执行增强版本。此文不以代码存在当作验证通过。

## 冲正报告真实持久证据与文件库生命周期

修正身份后默认文件库报告再次超时；保持同一源生成版及全部断言，把H2文件数据库在单个JVM内保持打开，两个独立进程分别执行APP声明的stage0/stage1后成功。日志spp-report-phase-runtime及spp-report-phase-resume-runtime，用时17.64/9.90秒；各进程结束后文件库由JVM关闭，下一个进程重新打开。导出JSON/中文Markdown核对四实际冲正、32反向分录、20量子记录、六存款后一次冲正及重放/重复拒绝保持14行、现金1700/版本4/积数2200、退款2和三债务恢复均通过。目录 `/tmp/spp-report-phase-evidence`。

公共ExampleProcesses仅为默认生成的H2文件URL附加DB_CLOSE_DELAY=-1，普通JDBC连接仍正常关闭，JVM结束前关闭数据库；用户提供URL保持原样。60秒阶段时限与业务断言不变。通用GeneratedExampleRunnerTest六项通过，包含不同进程PID、空参与者及实际持久读回，证明保持打开不会跨JVM保留内存状态或阻止下一阶段打开。正式默认父执行器冲正组正在再次验证 `/tmp/spp-report-default-lifetime-runtime.log`，最终clean还必须覆盖逐案例来源增强。


2026-10-09最终迁移门槛：默认父执行器现金冲正报告两新JVM组通过，日志 `/tmp/spp-report-default-lifetime-runtime.log`；同生成版本的JSON/Markdown已核对四实际冲正、32反向分录、20量子行和现金1700/版本4/积数2200。最后13主Java和1测试Java已删除，源目录Java当前全部为0。逐案例请求/授权/来源与实际重放返回增强已补SPP，尚需当前clean重新生成验证；`/tmp/spp-source-only-final-clean-validation.log` 正在执行，最终Goal尚未完成。


## 最终状态（2026-10-09）

本次纯源重构已完成：手写Java主0/测试0，旧14主类及21测试族无残留class，干净生成编译及945项公共JUnit、86个APP入口全部通过。五个两JVM组、逐案例输入/授权/来源增强、六成交48分录五候选及四冲正32反向分录20量子行全部核对。完整权威证据见[最终验证](source-only-final-verification.md)，当前状态以该记录为准，前文保留阶段历史及范围限制。
