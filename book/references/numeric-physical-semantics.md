# 数值业务语义与 PHY 实现

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

## 已确定的设计

SPP 业务计算描述理想数学运算，不承担机器位宽、类型转换、溢出、浮点误差或计算资源不足的问题。物理实现必须提供足够的表示能力与资源保证结果；无法兑现时必须报告物理实现失败，不能静默返回截断、溢出或舍入后的结果。

不增加显式 `number` 关键字。现有 `short`、`int`、`long`、`float`、`double`、`decimal` 声明在业务数值表达式中均属于抽象数值，同时提供未覆盖时的默认实现提示。业务约束不应从默认实现的机器范围推导。

具体数字表示的重定义属于 `.phy`。`.app` 继续组织应用语义及存储映射，不承接业务计算类型的重定义。计算表示与存储表示分别配置，数据库列类型不能隐式决定 Java 计算类型。

## 编译与生成

编译器保留表达式的操作数、运算符、优先级和赋值关系，先解析 PHY 数值绑定，再生成目标类型、运算、常量构造、操作数转换和结果转换。绑定不得修改原始业务类型或原始表达式。

例如业务表达式 `A = b * c + 5`，当参与字段绑定为 Java `BigDecimal` 时，可生成 `A = b.multiply(c).add(new BigDecimal("5"))`。只覆盖部分字段时，生成器仍必须解析整个表达式并检查赋值目标；不能仅按文本替换运算符。

数值比较按数值大小而非对象身份或十进制 scale 比较。缩窄到整数、浮点或有限存储表示时必须验证结果可精确表示。无效转换、非有限浮点数及无法精确完成的物理运算必须明确失败。

`BigDecimal` 是一种物理实现，不是业务数值语义本身。用户选择符合其业务的数字表示，不要求 SPP 提供适用于一切运算的通用精确类型。SPP 内置常见类型的运算适配，并提供可选的自定义适配器扩展；用户选择类型不意味着必须编写运算实现。禁止默认使用 MathContext 或舍入规则替代业务数学结果。明确的舍入、舍出、取整属于业务运算，语法和契约见[原子计算服务设计](atomic-calculation-services.md)。

## PHY 绑定与兼容

绑定应支持按默认数字类型及具体业务字段选择表示，字段绑定优先于类型默认绑定；原始 SPP 声明是无覆盖时的最后一级默认提示。Java 平台首先支持精确十进制表示与检查后的内置数字表示。

```spp
phy{
    numeric double as BigDecimal;
    numeric Account.balance as java.math.BigDecimal;
    numeric Account.quantity as long;
}
```

类型默认绑定适用于该类型的字段及服务参数，字段绑定使用 `业务类型.字段`。当前字段绑定支持标量；嵌套属性应绑定其声明类型的字段，例如 `Money.amount`，不能用某个对象访问路径改变共享声明。内置表示支持 `BigDecimal`（也可写 `java.math.BigDecimal` 或 `decimal`）、`BigInteger`（也可写全限定名）及 `short/int/long/float/double`。自定义表示使用 `numeric Money.amount as example.Money using example.MoneyAdapter;`，类型和适配器都必须使用全限定 Java 类名；没有适配器的未知表示明确拒绝。

内置 Java 数字表示使用精确十进制中间计算及检查后的目标转换。浮点物理表示采用 Java 标准最短十进制编码作为业务数值的读写约定；例如 `0.1d` 解码为十进制 `0.1`，写回时要求该编码往返不改变十进制值，不能直接用 IEEE 运算结果替代数学结果。`BigDecimal` 普通运算不使用舍入上下文。自定义适配器直接在所选类型上完成计算，并不强制先转成十进制；只有跨表示转换可能要求物理转换契约，默认十进制桥接不可用时明确失败。原始业务类型与运算元数据保持不变。

OpenAPI 的数字格式同步绑定：`BigDecimal` 使用无浮点 format 的 `number`；`BigInteger` 和自定义类型使用带有物理类型标记的 `number`，并保留 `x-spp-java-type`。生成器在 YAML 目录输出 `<domain>.numeric-codegen.json`，Java OpenAPI 生成步骤必须加载该配置以保持模型字段和服务接口的物理类型一致。Maven OpenAPI 插件使用 `configurationFile`，CLI 使用 `--config`。额度电商工程已接入该配置；没有扩展绑定时文件中的映射为空。

物理类型标记不等于 JSON 编解码实现。自定义类型的 JSON 编解码由 APP/PHY 提供；本次验证了 Java 模型类型映射、服务编译和执行，未提供适用于所有自定义数字类型的传输编码。

PHY 声明必须校验目标存在且属于数值，拒绝重复绑定和不支持的表示。绑定需要贯通生成模型、表达式和服务接口元数据，避免字段类型与计算代码不一致。

既有 profile 的兼容性必须以测试验证。旧生成路径的存在不代表机器溢出或误差符合新的业务语义；实现进度和暂未贯通的路径应明确记录，不可将局部支持宣称为全部完成。

## 验收

- 相同业务模型可在不同 PHY 配置下生成不同数值表示，业务声明保持原样。
- `A = b * c + 5`、混合数字类型、括号、负数、比较、复合赋值及除法都有生成与执行验证。
- 超过机器整数范围、十进制精确计算、无损转换和表示能力不足失败均有测试。
- 未知字段、非数值字段、重复绑定及不支持的实现均有诊断。
- 生成的 Java 能编译运行，现有语言与生成器测试通过。


## 模型缺省规格与PHY覆盖

SPP中的`short`、`int`、`BigDecimal(19, 2)`等均为number的缺省表示提示，不能从`int`自动推导业务整数约束。PHY支持`numeric { replace BigDecimal(9, 2) with BigDecimal(18, 2); override Buyer.wallet with BigDecimal(25, 2); }`。全局规则匹配原始模型规格，不级联；局部覆盖优先。精度和scale进入Java转换、OpenAPI元数据和DDL；转换使用精确表示检查，容量不足是技术失败，不能隐式舍入。业务舍入仍需明确计算。

详细语法与部署说明见[环境部署和物理缺省配置](deployment-environments-and-physical-defaults.md)。历史`numeric ... as ...`写法保持兼容，新Petstore不再采用全局double替换金额的写法。
