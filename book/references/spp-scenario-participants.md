# 场景参与者的声明与补全

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

场景和服务入口只声明参与者，不能接收客户编号、金额等独立基本属性。入口可以只有有限事实，查询及其他原子服务补全属性。Buyer/Seller 是具体业务角色，不靠两个 Customer 的变量名区分业务身份。

实例名可省略：Buyer 等价于 Buyer Buyer，表达式可写 Buyer.membershipNumber 或 if(Buyer)。显式别名仍允许。无参数调用 findBuyer; 按参与者类型及集合维度唯一绑定，缺失或歧义报错；显式传参可选择同类实例或集合。

场景只能引用已声明入口及其属性，不能构造或隐式引入参与者。参与者及集合元素只由原子服务创建；动态订单明细在原子计算中形成。

## 原地查询与保存

入口实例保持不变。服务没有业务返回，不能将查询结果赋值给入口。例如付款场景中的 Buyer customer 已携带会员号：

```spp
findBuyer(customer);
identify(customer),breakTransction;
```

查询原地补全 customer。if(customer) 检查语言内部确认状态，identify(customer) 是内置确认校验。未找到保留入口并取消确认，不以 null 表示未找到；技术失败由 APP/PHY 处理。

保存只接收当前参与者，例如 atomic update saveCustomer(Buyer);。技术 before/changed 快照、主键和版本属于 APP/PHY。业务成交明细及金额快照有业务意义，可保留。直接参与者关系不以外键字符串代替，APP 可投影外键。

## 集合与计算

场景可直接声明 Goods[] products 或 ShopOrder[] orders。生成接口采用可变 List，原子查询或计算替换集合内容、保留入口容器。直接 Java 调用须传可变集合，无匹配为空集；锁定及 optional 查询只支持标量。内部参与者集合属性仍可由原子构造数组并更新。

场景只能调用原子服务；普通原子服务不互调，calculate 仅调用 calculate，不调用 check/query/update/Scenario。资格在场景显式 check。普通对象赋值传递事实，不建立业务指针；copy 表达独立事实副本。标量入口禁止重赋值。

SPP 无 try/catch/throw，技术异常不作业务条件。check 范围和事务撤销见 [参与者执行](spp-participant-execution.md)，实体/角色/合约及平台边界见 [业务模型](spp-business-model-boundary.md)。

## 检查边界

编译器检查入口类型、引用、唯一绑定、调用/构造范围、量子约束；未使用参与者给出 SPP_UNUSED_PARTICIPANT 告警。更新场景必须有 Contract，明显技术字段未说明业务含义时拒绝。它不证明合约的业务含义或跨服务属性完整性。本轮只生成并编译，不运行回归。

## 合约内部的默认参与者名

合约中可写 `Buyer;`，等价于 `Buyer Buyer;`；例如 `Contract ReturnRequestAgreement { Buyer; ShopOrder; String reason; Receipt; }`。表达式通过 `ReturnRequestAgreement.Buyer` 引用该当事人。实体、外部引用、角色及合约字段支持默认类型名；基本属性和枚举属性仍须显式命名。重复默认名拒绝，需用别名区分。同一维度集合可省略别名，但多个同类集合应显式命名。

Petstore 的清空购物车和申请退货同时展示合约内部及场景入口默认名称，其余场景保留显式别名作为对照。实现及生成 JSON 默认名称保持一致。

## 量子调用范围

量子调用者在显式transaction中用`bounds { 参与者.量子属性: [下限, 上限]; }`选择成交范围，生成代码传递范围，量子成交实现负责拒绝越界交易并撤销绑定事务；null禁用对应方向，集合逐成员检查。校验不作为传统服务参数，也不由量子服务写死。普通check失败的block控制约定保持原样。参见[量子调用范围](quantum-call-bounds.md)。
