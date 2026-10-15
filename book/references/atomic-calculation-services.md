# 原子服务的数学计算、逻辑规则与数字实现

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 已确定的业务边界

业务原子服务保留 `query / calculate / check / update` 四类职责。数学计算和逻辑计算是 `calculate` 的两种实现能力；`check` 使用计算得到的条件判断业务要求是否满足。创建、取消、付款、通知和状态转换均可归入广义更新，不新增服务类别。

原子服务定义时约定参与者。场景由参与者及其数据构成，执行组共享这些参与者数据；串行组和并行组组织执行关系。集合可以作为原子服务参与者，集合算法也可以由 APP 实现，不要求把算法循环暴露到场景中。

纯业务判断、数学关系和结果赋值可以直接写在 `.spp` 原子服务实现体中；包含数据访问、外部调用等技术依赖的实现仍可放在 APP。业务实现不暴露 Java 类、方法、机器位宽、数据库和通信。业务日期、授权级别、业务渠道等事实即使从报文取得，也不应因此被删掉；其获取方式属于 APP/PHY。

## 服务体语法

声明式接口保持兼容；`calculate` 和 `check` 可以将结尾分号替换为实现体：

```spp
domain settlement;
Role Amount {
    double principal;
    double rate;
    double charge;
    boolean exempt;
    boolean permitted;
}
atomic calculate calculateCharge(Amount amount) {
    amount.charge = roundHalfUp(amount.principal * amount.rate, 2);
    if (amount.exempt) {
        amount.charge = 0;
    } else {
        amount.charge = max(amount.charge, 5);
    }
    amount.permitted = amount.principal > 0 && amount.charge <= amount.principal;
}
atomic check checkCharge(Amount amount) {
    require(amount.permitted, "费用条件不满足");
}
```

支持参与者属性赋值、`+= -= *= /= %=`、括号、正负号、`+ - * / %`、比较、`! && ||`、条件表达式 `条件 ? 值1 : 值2`、嵌套 `if / else` 和 `require`。表达式不得含赋值、自增、自减或技术位运算。函数是明确的业务数学操作，不是任意 Java 方法调用。

两个 `String` 可以用 `+` 拼接业务标识，例如 `request.id = prefix + "-CASH"`；拼接结果仍是 `String`，可继续与字符串拼接。此规则不隐式转换数字或其他参与者类型：`prefix + amount` 和字符串减法会被语义检查拒绝。

逻辑规则按书写顺序执行，读取执行到该位置时的参与者数据；多个 `if` 块可以依次生效。`else` 只属于最近且尚未匹配的 `if`。布尔逻辑和条件表达式保持短路求值。这是确定性规则计算，不引入规则优先级、议程、自动反复触发或外部规则引擎。

实现体用于 `calculate / check`；量子更新服务在SPP定义加减，调用者通过bounds语法约定成交上下限，生成代码自动校验。服务内check保留旧代码兼容，新示例不写死范围。计算与普通校验不能同时拥有SPP和APP实现；已有SPP更新动作的量子服务禁止APP再次定义动作；旧版仅声明约束的服务仍兼容APP动作，演示迁移为完整SPP业务定义。查询只有参与者入口，通过APP/PHY绑定原地补全，无业务返回值。

## Java 风格分支与循环

业务计算直接采用 Java 的 `if/else`、传统 `switch/case/default`、`while`、基本 `for` 和增强 `for`。原 `when/otherwise` 语法移除，既有业务源必须迁移到 `if/else`。

```spp
atomic calculate sumLines(Purchase purchase, OrderLine[] lines) {
    purchase.gross = 0;
    for (OrderLine item : lines) {
        item.amount = roundHalfUp(item.unitPrice * item.quantity, 2);
        purchase.gross += item.amount;
    }
    for (int i = 0, j = 3; i < j; i++, j--) {
        if (i == 1) continue;
        purchase.gross += i;
    }
    int n = 0;
    while (n < 3) {
        ++n;
        if (n == 2) break;
        purchase.gross += 1;
    }
    switch (purchase.gross) {
        case 0: purchase.discount = 0; break;
        default: purchase.discount = min(purchase.gross, 5);
    }
}
```

- 单条语句可省略花括号，支持 `else if`；`else` 绑定最近的未匹配 `if`。
- `switch` 只求值选择表达式一次。使用冒号分支，允许空分支、多个标签与中间位置的 `default`；没有 `break` 时继续执行后续分支。数字按业务数值比较，不借用物理表示的 Java `switch` 限制；字符串、字符和枚举也可作为选择值。枚举标签可使用业务枚举项名或其声明的字符串值。
- `while` 和基本 `for` 每次先判断条件；`for` 的初始化只执行一次，`continue` 后仍执行更新。省略条件表示持续执行，退出由业务条件和 `break` 表达。
- `break` 退出最近的循环或 `switch`，`continue` 进入最近循环的下一轮；不在对应作用域内时编译诊断。增强 `for` 按一维集合顺序逐项执行，不自动并行。
- 局部变量按块作用域解析，不成为参与者、服务参数或 OpenAPI 属性；基本 `for` 的局部变量仅在该循环内可见。局部数字声明同样是默认实现提示，PHY 类型默认绑定同时作用于它们。赋值和独立的 `++/--` 通过数字适配生成，避免 Java 原始数字运算绕开精确计算契约。
- `check` 可用局部变量计算并作 `require` 校验，但不能修改参与者属性，包括局部别名或集合元素的属性。

这里复用 Java 控制语句的写法及控制流程，数学表达式沿用 SPP 业务语义。支持的值表达式仍限于业务属性、常量、数学/逻辑运算和已声明的数学函数；不引入任意 Java 方法调用、对象构造、异常处理、带标签跳转或表达式中的赋值/自增副作用。`switch` 当前采用冒号形式，未引入箭头或模式匹配分支；局部变量类型使用现有 SPP 类型声明。

生成器以一次求值加分支索引的 Java `switch` 实现业务选择，保留穿透和跳转语义；不会把数字选择强制转换成 `int`。增强 `for` 的数字元素通过 PHY 转换契约绑定局部值。无法精确表示的结果仍由 PHY 明确失败；业务舍入必须写在表达式中。

## 舍入是业务运算

业务作者明确选择操作及小数位数：

| 函数 | 语义 |
| --- | --- |
| `roundHalfUp(value, places)` | 舍入到指定位数，正中间向远离零方向取值 |
| `roundHalfEven(value, places)` | 舍入到指定位数，正中间取末位偶数 |
| `roundDown(value, places)` | 向零截断到指定位数 |
| `roundUp(value, places)` | 向远离零方向取到指定位数 |
| `floor(value)` | 向负无穷取整 |
| `ceil(value)` | 向正无穷取整 |
| `abs(value)`、`min(a,b)`、`max(a,b)` | 绝对值及最小／最大值 |

小数位数是业务要求，不是配置机器精度。没有这些操作时，PHY 不得自行舍入。内置十进制实现支持在明确舍入边界内直接对除法舍入，例如 `roundHalfUp(a / b, 2)`；未给出舍入规则的除法仍按所选表示的精确能力执行。

## PHY 数字类型

不增加显式 `number`。现有数字声明保留默认实现提示，业务运算不依赖其机器范围。字段绑定优先于类型默认绑定：

```spp
domain settlement;
phy {
    numeric double as BigDecimal;
    numeric Amount.principal as com.example.Money using com.example.MoneyAdapter;
}
```

SPP 提供常见类型适配。自定义类型通过可选的 `NumericAdapter<T>` 契约扩展，适配器类由 PHY 选择；业务作者仍使用相同表达式。契约覆盖常量构造、四则运算、余数、取负、比较和明确舍入。跨表示转换由物理适配契约承接；无法表达或无法无损转换时明确失败。

适配器必须实现 `free.servpp.service.numeric.NumericAdapter<T>`，提供公开无参构造方法，并保持线程安全。运行时按适配器类缓存实例。默认 `convert` 在同一适配器内保留原值，跨适配器时使用可选的十进制桥接；自定义表示可以覆盖转换，也可以不提供十进制编码。`divideRounded` 默认先除后舍入，无法表示中间除法的适配器需要实现该物理操作；内置十进制适配器直接执行明确舍入的除法。类型与适配器的 Java 泛型契约由生成代码的 Java 编译检查。

不要求找到一种适用于所有业务的精确类型，也不要求每位用户编写运算实现。`BigDecimal` 只是内置选择之一；用户可选用符合其业务的类型。自定义适配器兑现自身表示与运算能力，并处理其物理限制。

## BOC 来源与验收

真实来源位于 `boc/ONLSOURCE/AGD187`、`AGDQ187`、`AGDQ180` 和 `boc/SOURCE/MBD820`、`MBDQGP`。本次提炼验证的核心关系包括：

- MBD820 的总额相等校验、面额整数倍校验及余额增加（`CHECK-INPUT`、`CHECK-DENOM-MULTIPLE`、`MBX820U`）。
- MBDQGP 的用户组许可判断和按条件累计（`F01-CHECK-BUSS-USERGRP`、`F13-SUMUP-PAYIN-REC`）。
- AGD187 的创建／修改／取消条件，以及 AGDQ187 的无需重新计算时跳过局部处理。

验收包含语法和语义诊断、默认及 PHY 重定义数字类型、布尔短路、嵌套规则、显式舍入、自定义适配器、生成 Java 编译执行、APP 兼容和相关回归。这里验证提炼后的业务关系，不宣称完成全部 BOC 程序转换。

普通check成功继续，失败结束所在block，缺省不回滚；guard校验只决定其包围范围是否执行。显式`checkXXX,breakTransction;`失败撤销当前事务。SPP不支持业务异常处理。`require`只用于普通check内部，不是calculate可调用的校验。详见[执行语义](spp-participant-execution.md)。

## 实现状态

已实现业务原子服务实现体、数学和布尔表达式、确定性条件规则、显式舍入、内置数字表示、PHY 自定义适配器、OpenAPI Java 类型配置及物理目录元数据。calculate/check的SPP与APP双重实现明确拒绝；量子更新动作已支持在SPP内声明，成交约束由事务框架在动作完成后执行；APP不应承载演示业务公式。服务业务返回和SPP异常写法需要迁移。

历史验证结果（不证明本轮参与者语义改动）：

- `mvn -pl credit-commerce -am test`：1105 项测试，0 失败、0 错误、1 项既有跳过；日志 `/tmp/spplang-calculation-regression.log`。
- 完整回归后补充字符标志和枚举值边界，并收窄对象比较以保留既有对象身份语义；最终 `mvn -pl generator -am test`：语言 249、运行库 445、生成器 85 项，全部通过；日志 `/tmp/spplang-calculation-final-verification.log`。这些收尾改动未重新运行电商集成测试。
- 生成的完整自定义数字服务通过 Java 编译并执行，分数表示直接保留 `1/3`；内置十进制、任意长度整数、混合表示、短路、嵌套规则、字符标志、显式舍入及表示失败都有执行验证。

业务计算体支持标量属性、声明的数学函数和 Java 风格控制语句；集合可在业务服务中遍历计算，也可交给 APP 实现。现已加入场景级校验作用域；没有自动规则议程或任意Java内嵌语法。自定义类型的跨表示转换和传输编解码仍由明确的 APP/PHY 契约承担。

控制语句扩展验收（2026-10-06）：

- `mvn -pl business-showcase -am clean test` 通过；补充括号/条件表达式的枚举选择类型后，`mvn -pl business-showcase -am test` 再次通过：语言 254、运行库 445、生成器 91、展示项目 24，共 814 项，0 失败、0 错误、0 跳过。
- 最终回归日志：`/tmp/spp-controls-final-edge-regression.log`；干净构建日志：`/tmp/spp-controls-final-regression.log`。
- `mvn -pl business-showcase exec:java -Dexec.args='--domain all'`：15 个案例全部通过；X06 验证 Java 控制流程，D01 使用业务层集合循环，X05 保留 36 组传统 Java 等价输入。日志：`/tmp/spp-controls-cli.log`。

## 本轮参与者语义

入口只允许角色、实体、合约或引用模型；默认实例名采用角色名，保留显式别名。calculate可通过`priceLine(line);`或唯一自动绑定调用另一个calculate，不调用其他种类服务，循环计算调用图报错。校验先在场景中执行，再调用计算服务，数学函数继续由语言和PHY表示契约实现。

Petstore的quoteOrder调用priceLine计算每行金额，服务直接修改OrderLine.amount，没有业务返回。量子payOrderFunds只声明钱包与商家资金加减，调用处bounds选择范围；执行SPP生成动作、提供方量子记录、自动范围校验、事务提交，越界进入绑定事务撤销路径。非量子资格仍由场景调用共享check。

本轮只生成、编译生产及测试源码，未执行回归，不能沿用上述历史测试作为当前运行证明。

## 调用者决定量子范围

```spp
payOrderFunds(customer, merchant, agreement) bounds {
    customer.wallet: [0, null];
    merchant.cash: [0, null];
};
```

bounds须在显式事务中修饰量子update调用，目标为实际传入参与者的量子属性；闭区间上下限在调用前求值，null禁用对应方向检查。负下限可表达透支，不改变共用服务。集合逐成员检查，越界自动撤销绑定事务，普通check语义不变。具体规范见[量子调用范围](quantum-call-bounds.md)。
