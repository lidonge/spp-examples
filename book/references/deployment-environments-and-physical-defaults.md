# 环境部署、事务与物理缺省配置

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 需求与约定

同一份 SPP 业务模型支持不同客户与不同环境的部署。数字声明只给出 number 的缺省表示，不推导整数、机器范围等业务约束；量子属性在模型声明一次。不同团队维护的域通过统一部署协议协作，环境及量子系统身份不兼容时拒绝启动。

APP application 按 environment 定义本应用承载的域，未承载的域由远程服务提供。环境标识支持 develop/testing/UAT/production 和自定义名称；构建明确选择环境。PHY 提供各环境的真实资源配置。事务使用可读 mode/resource，LOCAL、XA、SEATA_AT 为显式选项；不指定时满足 LOCAL 条件用 LOCAL，否则以 SAGA 串接提交阶段。显式不可实现的策略不得静默降级。

|服务|存储|LOCAL|XA/SEATA_AT|自动|
|---|---|---|---|---|
|同 JVM|同数据库同 schema 同连接资源|允许|校验协调能力|LOCAL|
|同 JVM|多 schema/多数据库|拒绝|校验协调能力|SAGA|
|跨 JVM|同数据库同 schema|拒绝|校验协调能力|SAGA|
|跨 JVM|多 schema/多数据库|拒绝|校验协调能力|SAGA|

LOCAL 将量子与普通更新加入同一个数据库事务，量子不提前独立提交；仍执行上下限并回填本次结果。分布式量子服务按统一系统实现，类型、逻辑资源及真实协调身份须一致。XA/SEATA_AT 的资源必须支持对应协议并加入同一协调系统。独立提交的量子服务与普通阶段通过 Saga 恢复。业务补偿仍为待专门讨论项。

## 语法与优先级

```app
application petstore {
    environment develop {
        deploy customer; deploy product; deploy inventory; deploy petshop;
        transactions { mode: LOCAL; resource: shopRecordsResource; }
    }
    environment testing {
        deploy inventory; deploy petshop;
        quantum { system: UNIFIED_STORE; resource: shopLedger; }
        // 未选择普通策略时，跨域调用采用 SAGA。
    }
}
```

量子属性从模型自动收集，量子服务的修改字段从运算自动推导，不再要求 attribute/resource 属性清单。非 LOCAL 环境的量子配置选择 UNIFIED_STORE、UNIFIED_SERVICE 或 TCC，由 PHY 接入；缺少协议实现的部署明确拒绝。

```spp
Role Buyer { quantum BigDecimal(19, 2) wallet; }
```

```phy
phy {
    numeric {
        replace BigDecimal(9, 2) with BigDecimal(18, 2);
        replace short with double;
        override Buyer.wallet with BigDecimal(25, 2);
    }
    i18n { resources: "i18n/petshop/"; defaultLocale: "zh-CN"; }
}
```

数字规则按原始模型缺省规格匹配，不级联；局部覆盖优先，同层重叠冲突拒绝。precision/scale 约定最终表示及存储容量，不能隐含业务舍入；物理转换不能兑现时报告技术失败。语言资源使用 UTF-8 的 locale.properties；SPP 常量名与缺省值保留，未知名称报错，缺失翻译告警并使用缺省值，非字符串业务常量不翻译。

## 实施路径与对比

1. 增加环境模型、选择及部署元数据；校验参与域、事务资源与量子身份。
2. 提供可读事务语法，贯通生成元数据和 LOCAL 共同提交；保留历史语法兼容但新演示不使用。
3. 自动推导量子属性和服务资源，移除 Petstore 重复 APP 清单。
4. 增加模型数字规格、PHY 全局精确匹配及局部覆盖，贯通 Java/OpenAPI/存储规格。
5. 从 PHY 相对路径加载独立语言资源，生成常量目录并诊断。
6. 更新 Petstore 及使用说明，执行生成、生产/测试源码编译和静态检查，不运行回归。

传统方案依赖各域手工一致配置协调器、DTO 数字类型和文案加载；SPP 以统一环境声明和模型元数据生成，提前拒绝部署矛盾。代价是需要声明可核验的资源身份和实现能力；有配置声明不等于已接入分布式协调器，启动必须校验实际适配器。

实施状态以最终验证记录为准，不以语法可解析代替运行协议实现。


## 实现与核对记录

环境选择由构建参数`-Dspp.environment=develop`控制，默认develop；APP包含各环境部署域列表，PHY环境块只解析所选环境。每个环境可以提供完整独立后端参数，公共numeric/i18n配置放在块外。缺少某环境的真实提供方或仓储参数会明确报错，不使用develop参数兜底。Petstore的testing提供三应用及独立数据库配置：customerService、productService、petstore；运行前需要设置统一内部调用凭据。

编译器比对LOCAL部署及数据库/schema，检查XA/SEATA_AT协调后端和同一事务服务组，并将统一量子系统与JDBC集中库、quantumService或tccObjectStore适配器匹配。量子协调配置不一致会报错。部署启动接口`DeploymentContracts`重新解析运行时资源覆盖并比对加载域的环境、模式和量子系统身份；它校验配置，不宣称验证了外部协调器的实际可用性或远端进程运行状态。

Seata XA使用依赖中的`DataSourceProxyXA`，不使用AT代理替代；AT继续使用其undo log协议。Petstore develop保留通用量子账本适配器，但使用共同的本地连接事务，量子不再提前独立提交。

Petstore全部服务和场景使用默认参与者名与唯一自动调用。`Goods`和`Goods[]`按完整类型区分，SPP表达式保留集合记法，生成Java/API模型才使用`GoodsArray`。SPP/APP/PHY及枚举源码注释已按最新约定移除，说明集中在独立文档中；网页与Java测试仅同步技术输入映射。

正向核对为生成和生产/测试源码编译，包含appframe-seata；静态核对包括移除注释前后代码一致性、SPP无Java集合名称、网页JavaScript语法与git差异格式。testing三应用源码已完成生成与编译；这不代表已运行验证远程部署。未执行JUnit、网页、数据库或真实分布式事务回归，未提交上传。


## 远程部署接入与验证边界

PHY以`domainRoute customer { endpoint: "http://127.0.0.1:8087"; timeoutMillis: 5000; }`选择提供方进程；该路由对默认CRUD及角色→实体查询生效，不在SPP传技术地址。编译器校验提供方路由、端点、冲突及内部调用凭据配置。内部调用协议包含参与者事实、identified、普通修订标记及APP存储身份，成功后原地回填。远程更新以服务调用技术头登记请求结果，查询不登记；重放保留事实和修订证据。

testing拆为petstore（inventory/petshop）、customerService和productService三进程，选择相同UNIFIED_STORE量子系统；量子执行域在此默认示例中共置。首版远程域原子量子调用及事务内远程锁定查询（包括角色补全）缺少相应成交恢复／锁协议时编译报错，运行时也保留保护。XA/SEATA_AT跨进程普通更新通过Seata事务上下文载体衔接，部署契约比较实际事务服务组，运行时重查资源绑定及XA代理模式；真实协调器执行效果尚未验证。

内部部署契约端点`/spp/deployment`在初始化期间可读取，业务接口仅在初始化完成后开放。消费者启动时比对提供方契约并检查`/spp/readiness`；先启动提供方，再启动消费者。凭据放在PHY `config domainRpcToken`，运行时通过`SPP_DOMAIN_RPC_TOKEN`提供，所有协作进程相同。

只构建和编译testing：

```bash
mvn -pl :petstore-demo,appframe-seata -am test-compile -DskipTests -Dspp.environment=testing
```

需要实际演示时，在三个终端设置相同的`SPP_DOMAIN_RPC_TOKEN`，再分别运行（本轮未执行）：

```bash
SPP_ENVIRONMENT=testing SPP_DEMO_SKIP_BUILD=1 ./demos/petstore/run-demo.sh web customerService
SPP_ENVIRONMENT=testing SPP_DEMO_SKIP_BUILD=1 ./demos/petstore/run-demo.sh web productService
SPP_ENVIRONMENT=testing SPP_DEMO_SKIP_BUILD=1 ./demos/petstore/run-demo.sh web petstore
```

默认端口依次为8087、8088、8086。可通过`SPP_CUSTOMER_ENDPOINT`、`SPP_PRODUCT_ENDPOINT`及各JDBC变量调整地址；多主机部署必须将集中量子库的默认文件地址改为各进程可访问的同一数据库地址。开发环境仍用`./demos/petstore/run-demo.sh web`。

验证范围为生成、编译及静态检查；未运行JUnit、网页、数据库及外部分布式事务。业务补偿仍按事务设计中的未完成议题单独讨论。协议异常携带已有事务结果证据；网络中断或无法证明的结果标为UNKNOWN，不能凭通信失败推断已回滚。


## 最新静态验证记录

- testing生成及源码编译：`/tmp/spp-goal-acceptance-testing.log`，BUILD SUCCESS；三个应用目录采用SAGA及统一量子系统，并携带事务资源名。
- develop生成及源码编译：`/tmp/spp-goal-acceptance-develop.log`，BUILD SUCCESS；目录恢复单应用、四域同进程和LOCAL策略。
- SPP/APP/PHY/枚举源码注释已撤除，移除前后代码及字符串保持一致；SPP无Java内部Array名称。启动脚本、网页JavaScript和git差异格式静态检查通过。
- 新增的跨进程普通修订证据按参与者所属本地域标识来源，不能一律使用进程部署列表中的第一个域。

远程请求流水号加入场景内静态调用序号：不同调用位置独立计数，并行工作线程继承请求流水号，请求方身份使用环境及应用名而非部署域列表顺序，线程调度不会交换同服务不同调用的编号；序号不依赖源码行号、空白及注释。普通事务资源名按各应用的部署域保留，不被其他应用的配置覆盖。本轮要求按下方对应表核对；运行验收明确保留为未执行。远程服务节点的恢复不能凭HTTP失败推断；业务补偿方案仍为独立待讨论项。本轮没有运行服务、数据库或回归测试。


LOCAL资源核对同时包含连接账号及schema。JDBC连接按PHY选择schema并核验驱动返回值；驱动不支持或不能确认时明确失败。相同连接配置的本地后端共享数据源，不因后端名称不同拆成多个连接资源；不同schema／连接账号使用不同数据源，并拒绝宣称共同LOCAL提交。账号凭据不在部署诊断中输出。


## 需求与实现证据对应

|本轮要求|源码／生成证据|核对范围|
|---|---|---|
|按环境选择部署域与PHY参数|App.g4、AppCompiler环境walker、DeploymentEnvironmentPlanner；testing目录三个应用，develop目录一个应用|生成、编译及目录核对|
|统一量子系统类型、资源与协调身份|DeploymentEnvironmentPlanner、DeploymentContracts、DomainDeploymentManifest；启动核对远端契约|源码静态审查，协议源码编译|
|可读LOCAL/XA/SEATA_AT/SAGA配置|APP环境transactions mode/resource；LOCAL校验JVM及连接范围，XA/AT校验Seata组与资源能力|语法生成、验证器及实际XA代理类源码审查|
|默认事务策略与部署匹配|满足共同本地提交条件时LOCAL，其余SAGA；显式矛盾配置诊断|Planner及物理配置验证源码审查|
|量子属性及服务修改字段自动推导|SppDomain.inferQuantumBindings；testing目录自动包含Buyer.wallet、Merchant.cash及StockLine三个属性|模型、APP及生成目录核对|
|LOCAL量子与普通更新共同提交|SourceTransactionPlan、DefaultTransactionManager、共享JDBC数据源；develop付款服务模式为LOCAL|生成代码和资源／提交路径审查|
|schema实际选择及共同资源核对|DriverManagerJdbcDataSource选择并确认schema；相同本地连接配置复用数据源|源码审查及编译，未连接数据库|
|数字声明仅为模型缺省提示|SppParameter保留declaredNumericSpecification及physicalNumericSpecification；业务表达式统一数值生成|源码及OpenAPI默认／实际规格核对|
|全局替换、局部覆盖及precision/scale|NumericBinding、NumericJavaRenderer、DDLGenerator、ExactNumbers；Product.cost 9,2→18,2，Buyer.wallet→25,2|生成Java及OpenAPI规格核对|
|业务舍入与物理容量分离|ExactNumbers使用UNNECESSARY检查，业务roundHalfUp保留在计算中|生成计算代码及转换源码审查|
|按语言拆分常量资源|独立UTF-8 zh-CN/en-US properties，BaseHandler相对PHY读取；常量目录按locale生成|资源文件、加载／诊断源码及目录核对|
|默认参与者及集合表意|SPP使用Goods与Goods[]，调用可唯一匹配时省略参数；Java内部采用GoodsArray|源码审计及生成编译|
|源码可读性|移除SPP/APP/PHY/枚举源码注释，说明保留在独立文档|移除前后代码及字符串一致性核对|
|远程更新与并行调用重放身份|生成静态调用序号、独立出现次数；并行线程继承请求流水号；请求结果带修订证据|生成调用位置及框架源码审查|
|文档先行及传统方案比较|本文件需求、实施路径、对比；Petstore requirements／implementation-path同步|文档核对|
|生成编译静态验证、无回归运行|Maven test-compile -DskipTests；脚本／JS语法、JSON夹具及git差异检查|编译和静态检查；未执行JUnit、服务器或数据库|

这份对应表限定证据范围：编译和源码审查不代替外部分布式协调器、网络故障和数据库执行验收。用户本轮要求不运行回归测试，故未执行这些运行验收。

量子与普通存储能力分别校验：集中 JDBC 量子库及其 localJdbc 后端可与普通 XA／SEATA_AT 后端组合，按量子先提交、普通阶段随后执行的 Saga 计划生成。量子批处理／反交易能力只检查量子后端，不要求普通后端也为 localJdbc。第一版 REQUIRES_NEW 仍要求本地 JDBC 能力；原生协调器挂起／恢复未接入的组合编译报错。

第一版远程 XA 原子协议为每次调用建立独立分支。同一事务边界内重复更新同一远程参与者需要共享 XA 分支会话，当前编译报错；本地同一事务中的多次更新不受此限制。该限制不能用普通本地提交替代全局 XA。

最终核对记录：`/tmp/spp-goal-final-testing-compile.log` 和 `/tmp/spp-goal-final-develop-compile.log` 为两套环境的生成及源码编译日志；`/tmp/spp-goal-final-static-audit.json` 核对 develop 单应用、LOCAL 付款、缺省与覆盖数字规格、分语言常量和未执行回归的范围。追加的远程 XA 校验按 APP 实际持久化目标识别参与者，输入资料参数不被当作写入目标。
