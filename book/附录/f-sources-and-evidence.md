# 附录 F 资料来源与验证证据

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

本附录提供概念、源码、执行与性能资料的查阅入口。书中概念作为同一个体系阐述，跨文档仍需统一的问题单独维护在 [编辑工作记录](../编辑工作/known-issues.md)，不进入正文的叙述线索。

## F1 理论与方法资料

| 资料 | 可查阅内容 |
| --- | --- |
| S++ 概念与应用 (maintainer reference: `../../../spp/docs/cn/concept.md`) | 服务模型、分解组合、量子服务、多态、业务技术分离与性能模型 |
| S++ 建模案例 (maintainer reference: `../../../spp/docs/cn/modeling.md`) | 商店参与者、身份、业务约定与存储组织 |
| 场景组合设计 (maintainer reference: `../../scenario/docs/Composit.docx`) | 职责分类、依赖分组与组合调度 |
| 应用框架设计 (maintainer reference: `../../lang/doc/ApplicationFrame.docx`) | 调度环境、技术处理与事务组织 |

相邻 spp 仓库资料需要单独取得。独立克隆本仓库时，指向该仓库的相对链接需在同级目录备齐资料后使用。

## F2 语言与工程规范

| 内容 | 资料 |
| --- | --- |
| 模型意义及参与关系 | [业务模型边界](../references/spp-business-model-boundary.md) |
| 查询、身份与控制范围 | [参与者执行](../references/spp-participant-execution.md) |
| 业务计算与规则 | [原子计算](../references/atomic-calculation-services.md) |
| 数值表示与业务舍入 | [数值语义](../references/numeric-physical-semantics.md) |
| 量子成交范围 | [量子调用范围](../references/quantum-call-bounds.md) |
| 事实归属、提交及恢复 | [事务与存储](../references/transaction-storage-v1.md) |
| 多环境资源与部署 | [环境与物理配置](../references/deployment-environments-and-physical-defaults.md) |

Petstore 代码统计保留 F7 所列的独立基线；本次银行案例与新增能力核对以主线 `0fafa21d` 为基线。规范说明目标与约束，源码说明表达与实现，运行记录提供特定路径的证据。单项资料不能独自代替全部层次。

## F3 Petstore 功能验证

[2026 年 10 月 13 日 APP 技术服务验证](../references/app-technical-services.md)记录完整生成与回归 1,123 项通过：语言 362、运行框架 617、生成器 105、Petstore 39，失败、错误、跳过均为零。覆盖匹配和编译检查、调用阶段、技术访问拒绝、观察失败隔离、并发和幂等重放；远程代理使用可控传输验证，未进行真实跨 JVM 验收。[Petstore 样例](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/technical-services.md)展示商店全服务日志拦截。该能力来自主线 `65c766fc`；本书此次引用已有测试记录。

[2026 年 10 月 13 日失败处理验证](../references/spp-transaction-failure-handling.md)记录 develop 完整生成链路回归 1,104 项通过：语言 356、运行框架 607、生成器 105、Petstore 36，失败、错误和跳过均为零。[预约专项说明](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/reservation-failure-handling.md)说明真实 fail 样例的库存不足、普通保存失败与幂等重放结果。框架专项另验证真实 JDBC 量子成交后的自动反交易先于 fail 执行；本轮 Petstore 使用 LOCAL，不代表已经验收真实分布式 TCC 或外部量子服务。本书此次引用已有记录，没有重新运行测试。

[2026 年 10 月 12 日最终回归记录](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/regression-2026-10-12-conserved-transfers.md)报告：develop 联合回归共 1080 项，分别为 lang 340、appframe 581、generator 105、appframe-seata 20、Petstore 34，失败、错误和跳过均为零。

同一记录报告 develop 完整 Chrome 流程，以及 testing 三 JVM、四个隔离文件数据库的完整网页与商店重启验证。停机后核对资金来源与去向合计、按商品核对库存与供应来源、按交易核对流水增减合计。

这些是仓库已有验证记录，编写书稿时没有重新运行对应业务测试。记录中的临时日志路径用于追踪当次证据，独立环境需按记录重新执行才能取得新的运行结果。

[已知问题](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/known-issues.md)记录初始化重试的实现边界，以及分库零记录技术恢复的已实现范围；具体机制与验证见 [分库零记录技术恢复](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/petstore/docs/quantum-opening-recovery.md)。功能回归没有提供附录 C 所定义的串并行性能基准。

## F4 某银行存款案例验证

当前某银行存款案例已完成对齐新语法与运行协议的重构。生产源位于[案例目录](../../demos/bank-deposit/src/main/spp/cboddeposit)，只使用 SPP、APP、PHY，没有手写生产 Java。SPP 不使用 `try/catch/throw`；生成的 Java 与运行时内部仍可用异常处理承接技术故障。历史源仅保留作规则对照，不能作为当前可执行示例。

本节以主线 `0fafa21d` 为当前案例检查基线，引用仓库中已有记录，本次书稿修改没有重新运行银行业务测试。[最新验证记录](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/latest-refactoring-verification.md)按批次保存命令、结果及适用范围：

|验证批次|结果|涵盖范围|
|---|---|---|
|2026 年 10 月 13 日 clean develop 联合回归|1,226 项，零失败、零错误、零跳过|语言 366、运行框架 628、生成器 107、某银行案例 86、Petstore 39；包含内部收款户、历史快照及已加入的故障与并发测试|
|随后 testing 银行全量回归|86 项，零失败、零错误、2 项跳过|本 JVM 内独立量子与普通 H2 数据源；跳过两个 LOCAL 专属提交故障测试|
|独立现金冲正试算专项|develop、testing 各 2 项通过|试算不写入，正式冲正保留后来存入；缺原成交拒绝无副作用|
|中文工作台专项|两环境后端专项及浏览器流程通过|精确小数显示、负数拒绝、试算、冲正、回执查询与移动布局；具体范围见[工作台验收](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/web-workbench.md)|

testing 的分库证据不能直接扩大为真实网络分布式部署、XA、Seata AT 或 TCC 的完整验收。独立 JVM 重启与成交确认后强制退出，覆盖各自规定的持久化路径，不能代替提交中断或未知成交的自动查证。后续专项也不能直接累计成一次未执行过的全量联合回归。

[完整性审计](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/completion-audit.md)说明已落实的场景、存储、事务与技术能力。[86 个历史入口核对台账](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/legacy-entry-migration.md)逐项列出证据、差异及未迁移部分；86 个历史入口与上述 86 项 JUnit 测试是不同统计，不能因数字相同而认为已经逐项等价。

[已知问题](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/known-issues-latest.md)仍保留普通 Saga 已提交阶段恢复、待授权持久化与跨进程续办、未知成交自动确认、全调用持久化审计等边界。当前分库失败可以自动恢复量子资金，并可能留下普通已提交事实；系统明确报告 `RECOVERY_REQUIRED`、`handled=false`，不声称全回滚。

[来源映射](https://github.com/lidonge/spp-examples/blob/93d4b68831f1812794e173fd943a77e3be21517a/demos/bank-deposit/docs/source-map.md)提供当前能力目录和源程序规则定位。源码推导、业务数学预期、演示输入、生成执行对照、原 COBOL 实测与银行确认结果代表不同证据。案例成功不能扩大为全部银行政策或原系统输出等价。

## F5 QService 资料

相邻 qservice 仓库的 SPP 边界契约 (maintainer reference: `../../../qservice/docs/spp-qservice-boundary-contract.md`)与量子服务设计 (maintainer reference: `../../../qservice/docs/qservice-early-design.md`)描述逻辑命令、持久身份、状态查询和恢复。

该项目的集成产物和测试路径有自己的基线。使用其中一种后端时，需要核对真正接入的协议与执行能力，不能把独立项目的全部验证结论直接扩展到任意部署。

## F6 证据怎样使用

解析说明表达被接受，编译说明产物通过相应静态检查，运行说明所测路径，故障与重启验证进一步覆盖特定失败条件。性能证据还需要明确资源和工作负载。

阅读结论时，可先找到它对应的参与者、行为和配置，再查看输入、预期、实际结果与失败范围。保持这些信息关联，概念论证才能与可复查的工程实践连接。


## F7 Petstore 代码量统计

2026 年 10 月 13 日，以本书工作分支 `5b9b182c` 的 Petstore 源码进行统计。该次书稿修改未改变案例源码。从本工作区原先不存在的生成 Java 目录完成 develop 生成，避免将其他版本遗留文件计入。命令在仓库根目录执行：

```bash
mvn -pl :petstore-demo -am package -DskipTests -Dspp.environment=develop
```

统计输入为 `demos/petstore/src/main/spp/` 下的 `.spp`、`.enum`、`.app`、`.phy`，输出为 `demos/petstore/target/generated-sources/openapi/src/main/java/` 下的 `.java`。不计测试、网页、资源文件、构建脚本、生成器和公共运行框架依赖的代码；Java 数字包含 S++ 生成器及 OpenAPI 生成器的输出。复现时使用干净生成目录，源码或工具版本变化后应重新统计。

|文件类别|文件数|物理行数，含空行与注释|去除空行与注释后的行数|
|---|---:|---:|---:|
|SPP|63|1,104|999|
|枚举|2|25|18|
|APP|4|126|117|
|PHY|4|222|214|
|输入合计|73|1,477|1,348|
|生成 Java|962|131,107|100,151|

生成 Java 中，模型目录占 64,431 行，服务目录占 21,031 行，接口与处理目录占 14,535 行，映射及配置占 154 行。这说明模型和请求响应展开占较大比例，不能将每一行都解释为需要人工设计的新业务逻辑。

以下脚本按物理行计数，去除行注释、块注释与空行，保留字符串中的注释符号及独立括号行。它适用于本次源码，不是所有语言结构的通用代码分析器：

```python
from pathlib import Path
import re

pattern = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
)

def code_lines(source):
    def remove_comment(match):
        token = match.group()
        if token.startswith(("//", "/*")):
            return "\n" * token.count("\n")
        return token
    source = pattern.sub(remove_comment, source)
    return sum(bool(line.strip()) for line in source.splitlines())

source_root = Path("demos/petstore/src/main/spp")
java_root = Path("demos/petstore/target/generated-sources/openapi/src/main/java")
for suffix in (".spp", ".enum", ".app", ".phy", ".java"):
    root = java_root if suffix == ".java" else source_root
    files = sorted(root.rglob("*" + suffix))
    sources = [path.read_text(encoding="utf-8") for path in files]
    print(suffix, len(files),
          sum(len(source.splitlines()) for source in sources),
          sum(code_lines(source) for source in sources))
```

SPP 中一行可以包含多个声明或调用，Java 的模板格式、访问方法和请求响应类型又会扩展物理行数。因此这是一组明确版本下的源码规模统计，不是语言表达能力、生产率或性能的统一比例。准确测量手写 Java 的规模，还需要具有同等业务范围、技术能力和验收条件的独立实现。以下只给出按职责拆分的工程估算。

### 使用常见 Java 框架的估算

假设采用 Spring Boot＋MyBatis＋Lombok，复用框架与已有通用组件，不为每个内部服务额外建立一套独立远程接口，也不手写访问方法。Lombok 可以生成访问方法等模型重复代码，MyBatis 提供 SQL 映射，Spring 提供声明式事务支持；这些已有能力在估算中视为依赖，不计入项目手写代码。参考 [Lombok Data](https://projectlombok.org/features/Data)、[MyBatis Mapper](https://mybatis.org/mybatis-3/sqlmap-xml.html) 和 [Spring 声明式事务](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)。这些文档说明框架能力，下面的行数是本书的工程判断，并非文档提供的基准。

|需要维护的内容|估算行数|估算理由|
|业务模型、DTO、枚举|1,000～2,000|四个域的参与者与请求结果，复用模型，使用 Lombok|
|入口、参数转换与对象映射|1,000～2,000|34 个场景的入口及边界适配|
|场景编排、计算与资格校验|3,000～5,000|每个场景约 90～150 行，包含共享规则及依赖组织|
|存储接口、SQL、映射与表结构|2,000～4,000|普通事实、成交快照、版本条件和查询关联|
|守恒交易、幂等与失败恢复接入|2,000～5,000|双边变化、范围控制、原请求确认与阶段恢复|
|域调用、环境配置与技术错误处理|1,000～2,000|本地与远程调用适配、资源与环境选择|
|合计|10,000～20,000|项目 Java、SQL／Mapper 和必要配置的合计|

各行按主要职责分配，避免重复计入。例如业务拒绝规则计入场景与校验，远程超时确认计入恢复与技术处理。估算没有加入第五篇提出、但案例尚未完整实现的通用缓存裁剪、全套安全治理等扩展需求，也不包含公共框架本身的开发。

若只做常规单体商店，采用本地事务、合并部分模型、减少跨域适配，并把恢复缩减为本地回滚，项目可能约为 6,000～10,000 行。但这一较小范围没有覆盖多域部署及其结果确认与恢复职责，应单独列出，不能直接作为相同能力的比较。

已有账务、幂等与协调中间件越完善，需要手写的代码越少；反之，自行开发通用恢复设施会超出上述范围。行数还受格式影响，SPP 当前有多条语句写在一行的情况。因此“一万到两万行”只用于解释项目维护规模，不能推导精确的生产率倍数或开发工时。

## F9 某银行案例的 COBOL 与 S++ 代码量

2026 年 10 月 14 日，以本仓库 `92ed491b` 的案例源码和来源文档为统计基线。原 COBOL 与 COPYBOOK 从本地银行来源目录读取，没有改动，也没有复制原源码到本书。该目录需单独取得；统计文件清单与数字保存在本附录的[统计结果](统计资料/bank-code-count.json)中。

### 来源范围与去重

“直接定位分析”口径选取来源文档中有程序文件名或具体行号定位的 9 个 COBOL 程序。这里的“定位分析”表示已有源码追踪依据，不表示整份程序的所有分支都已迁移：

|程序|来源职责|物理行数|去除空行与注释后的行数|
|---|---|---:|---:|
|GSA01102|一般存入前台受理|2,325|1,820|
|KSADEP0|存款核心、偿还分配及冲正|4,197|3,508|
|CSAQRY1|账户资格与受理检查|2,654|1,867|
|KSAFEE0|收费入口|384|310|
|CSAFEE0|收费规则|415|331|
|CCMDAT1|日历与天数|2,856|2,563|
|CSAPRD2|存款及协议积数|483|315|
|CSAPRD4|透支积数|237|154|
|GCCBAAR|账务规则接入与配置来源分析|605|542|
|合计|9 个程序|14,156|11,410|

从上述程序的有效 `COPY` 语句追踪，直接引用 135 个 COPYBOOK，再加入嵌套引用新增的 26 个，共 161 个。共享 COPYBOOK 按实际文件去重，同一文件被多个程序或多次引用只计一次；不会按调用次数或展开次数重复累计。

更宽的“全部相关”口径选取来源文档明确提及、且在原源码目录中实际存在的程序，共 22 个。它包含调度、查询、配置等相关程序，尚未递归扩展为全部 `CALL` 依赖图，不能称为整套银行系统的代码量。

|来源范围|COBOL 程序数|去重 COPYBOOK 数|程序物理行数|COPYBOOK 物理行数|合计物理行数|合计去除空行与注释后的行数|
|---|---:|---:|---:|---:|---:|---:|
|直接定位分析|9|161|14,156|23,488|37,644|22,589|
|文档提及的全部相关程序|22|192|20,626|24,961|45,587|28,358|

逐文件清单分别见[直接来源清单](统计资料/bank-direct-source-files.csv)与[全部相关来源清单](统计资料/bank-related-source-files.csv)。清单只保存文件位置与行数，不包含银行源码内容。

### 当前 S++ 源码

仅统计案例生产源目录中的 SPP、枚举、APP、PHY，不统计历史资料、Java 测试、测试输入、网页、构建脚本、生成 Java 或公共编译器与运行框架。

|源码类别|文件数|物理行数，含空行与注释|去除空行与注释后的行数|
|---|---:|---:|---:|
|SPP|34|1,037|973|
|业务枚举|1|6|6|
|APP|2|48|48|
|PHY|2|38|38|
|合计|39|1,129|1,065|

SPP 与枚举合计 979 行，表示当前需要维护的业务模型、服务、场景和有限取值；APP、PHY 再增加 86 行。当前有多条 S++ 语句写在同一物理行，因此不能将行数比例直接当成算法复杂度、工作量或生产率比例。

### 计数与复现

物理行数按文件原始换行计数。COBOL 去除空行与注释后的行数按固定格式处理：排除第 7 列为 `*` 或 `/` 的注释行，在第 8～72 列取有效内容，移除 `*>` 后的行内注释，再计非空行；不把序号列及右侧标识区当作代码。该计数仍包含数据定义、`COPY` 指令、过程与控制声明，不是业务语句数。

COPYBOOK 使用同一规则。SPP、枚举、APP、PHY 去除 `//` 与 `/* … */` 注释，保留字符串中的注释符号，计剩余非空物理行。统计没有把 COPYBOOK 展开到每个程序中重复累计。

[复现脚本](统计资料/count-bank-code.py)接受原 COBOL 根目录作为参数，可在仓库根目录执行：

```bash
python3 book/附录/统计资料/count-bank-code.py /path/to/original/cobol-root \
  --output-dir /tmp/bank-demo-code-count
```

根目录中应具有原程序与 COPYBOOK 的分类目录。脚本输出两份来源清单和汇总 JSON；源码或来源文档变化后，选取范围与结果也可能变化，应重新统计并标明版本。当前两种来源范围均没有未解析或歧义的 COPYBOOK 引用。

### 比较结论的范围

以上来源规模与当前实现规模可用于解释表达的集中程度，不能证明所有来源代码已经完成等价转换。9 个或 22 个来源程序的全部内容包含更多交易方式、共享配置及未迁移分支；S++ 案例只覆盖已明确实现和验证的业务路径。

角色与服务模型集中表达这些路径中的规则、参与关系与执行边界，工具提供大量重复实现，APP、PHY 接入存储与运行能力。案例仍依赖公共框架，科目及外部事实仍有演示配置，授权续办和普通 Saga 恢复等边界见 F4。不能把来源全部行数与案例行数的商，写成无条件的压缩倍数或完整替代结论。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](e-language-and-build.md)
