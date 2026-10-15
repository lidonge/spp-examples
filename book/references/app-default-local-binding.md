# APP 域内服务默认绑定

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

域内只定义一个 `local` scope 时，SPP 声明的原子服务和场景自动归入该 scope，继承输入、输出 header。不再逐项罗列普通服务名称。

```app
scope {
    local(in requestContext, out responseContext) {
        duplicate key(Buyer.membershipNumber)
            facts(agreement.quantity) reserveShopPet;
    }
}
```

显式绑定优先：服务已出现在 local/remote scope 中时，保留其声明，不再自动绑定。同一域有多个 local scope，尚未显式绑定的服务会报告默认配置有歧义，必须明确选择；不会按服务名称、声明顺序或参与者猜测配置。没有 local scope 时保持原有显式配置行为。旧的实体自动生成服务维持原有绑定，不扩大其对外暴露。

本域 scope 默认继承调用方式及 header；标准仓储及跨域参与者绑定另由下述默认规则生成。复杂查询、量子资源、防重、定制跨域目标及 web expose 仍显式配置。默认绑定不会增加业务事务或自动暴露 HTTP 接口。

Petstore 四个域已删除普通服务的重复列表及标准主键查询、普通持久化声明，保留有定制含义的配置。生成期完成默认绑定后，统一参与既有部署、header、事务、幂等和物理实现校验。

界面防重与远程请求幂等已分离，参见[请求协议](app-call-idempotency-and-duplicate-guard.md)。

## 默认仓储与角色补全（本轮实施）

标准单参与者 `atomic query` 根据 APP 表主键生成原地查询，失败只改变确认状态。查询角色后，依据 `take` 与 `Reference ... from` 的所属域调用实体提供方补全事实；不直接跨域访问表，也不依据 find/describe 前缀猜测。显式 repository 或 bind 优先。

普通持久化采用明确操作：`atomic insert` 创建、`atomic update` 修改、`atomic delete` 删除。insert/delete 在生成模型中仍属于更新服务。默认绑定依据参与者表主键和 PHY 默认仓储的持久化资源策略；不得按函数名判断插入。编号策略仍可单独在 APP 声明。

复杂查询保留按买家列订单、按在售条件列商品两例。跨域服务依据 Reference 所属域、操作类别和参与者类型及集合维度自动绑定，要求唯一候选，不依赖函数名。需要选择不同外域查询服务时保留简洁 bind，参数转换由显式 take 决定；找不到唯一实体查询提供方时报告歧义，不任意选择。

APP 可以新增不属于 SPP 属性的技术主键：

```app
table SHOP_MERCHANTS(Merchant) {
    // APP 新增主键供生成的 CRUD 定位记录；Merchant 在 SPP 中没有此字段。
    primarykey notnull String merchantRowId;
}
```

它是角色记录增删改查所使用的技术身份，不等于业务凭证号。生成代码及运行时通过 APP 身份映射管理和使用该主键；SPP 参与者不定义它，业务调用不显式传递它。本样例商店只有一个经营角色，仍明确采用 singleton 查询定位；标准插入/更新复用这一唯一 APP 身份约定，不再重复 persist；多商家部署需要 APP 身份映射，不得把 singleton 推广为一般角色查询规则。

验收只运行生成及编译，不运行回归测试，不连接数据库。

PHY 默认仓储集中声明普通持久化使用的资源与提交实现，而非在 APP 每个服务重复声明：

```phy
repository shopRecords {
    adapter jdbcObjectRepository;
    config default = true;
    config persistenceMode = "quantum";
    config persistenceResource = "shopRecordsResource";
    // datasource 等其他物理配置省略。
}
```

本演示继承已有物理量子协调资源以与量子成交共同提交；普通 insert/update 本身没有量子运算或量子属性边界。该实现选择不改变 SPP 的 transaction 一致性要求。

自动角色补全沿显式 take 递归到根角色或实体，而不是按同名字段交集复制；有自身表先查角色，无自身表的角色视图直接查询扮演者。跨域根实体使用所属域的唯一主键查询服务，集合逐个补全；缺少主键提供方、多个候选或循环扮演时报错。主键未提供或未命中时查询确认失败，不改用非主键筛选。

外域定制查询采用 `bind importCatalogue to product.listCatalogue;`，参数只能以同一跨域参与者身份或显式 take 对应。本地非主键查询仍直接由 APP repository 实现，无需 bind；完整规范和示例见[参与者查询与跨域角色绑定](participant-query-binding.md)。旧带 facts 的 bind 保留已有工程兼容。
