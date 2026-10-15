# SPP 参与者构造与日历计算

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

参与者构造仅限原子服务。场景必须明确声明所需参与者，允许入口提供有限属性，由原子服务补全；场景不能直接构造参与者，SPP不提供异常捕获语法。见[场景参与者约束](spp-scenario-participants.md)。

业务原子服务可以构造已声明的角色、实体、合约及引用模型，用于工作上下文或业务记录：

```spp
Role DateParts { int encoded; int year; }
Contract Work { DateParts date; }
atomic calculate prepare(Work work) {
    work.date = new DateParts();
    work.date.encoded = 20240229;
}
atomic check checkDate(DateParts date) {
}
atomic calculate deriveYear(DateParts date) { date.year = dateYear(date.encoded); }
Scenario serial describeDate(Work work) {
    prepare(work); checkDate(work.date); deriveYear(work.date);
}
```

`new Type()` 只接受当前业务域已声明的数据类型，不允许任意 Java 类、服务类或枚举；赋值和局部变量初始化必须保持声明对象类型一致。构造产生空模型，字段初值与必需事实仍由业务显式赋值或校验。需要已有事实的独立快照时使用 `copy(value)`。支持一维对象集合初始化，例如 `new Line[] { new Line(), new Line() }` 或 `new Line[] {}`。元素必须是同类型标量对象或 null；不能混入其他类型、数字或嵌套集合。局部变量可写为 `Line[] lines = new Line[] {};`，并可通过已有 for 遍历。集合创建不自动构造额外元素，也不替业务推断元素数量。目前不支持指定长度分配、带参数构造或在场景条件中构造对象。

基础日历函数接受整数形式的公历 `YYYYMMDD`：

| 函数 | 结果 |
|---|---|
| `isGregorianDate(value)` | 是否为有效日期；无效日期返回 false |
| `dateYear(value)` | 年 |
| `dateMonth(value)` | 月 |
| `dateDay(value)` | 日 |
| `dateEpochDay(value)` | 从 1970-01-01 起的日数，支持负值 |

日历解析支持公元 1 至 9999 年，拒绝小数、越界值及不存在的日期。拆分函数对无效值报 `INVALID_CALENDAR_DATE`，空值报 `MISSING_CALENDAR_DATE`。支持 Gregorian 闰年规则。银行允许的年份范围、跨日冲正资格、业务年天数、计息及舍入并不由基础函数决定，应在 SPP 服务中另行表达。

函数结果通过统一数字表达式生成链路适配 PHY 的数字类型，不要求业务编写 Java 数字转换。生成模型中的数字属性可以显式与 null 比较以校验缺失值；数字常量及原始数字参数不因此取得可空语义。

可选集合在生成模型中用 List 保存，在服务参数中按业务数组声明传递；生成器处理两者转换并保留 null。对集合是否必需以及何时允许空值，由业务服务决定。
