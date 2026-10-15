# APP 仓储声明

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

SPP 声明业务参与者、资格及 transaction 一致性边界；APP 绑定查询和更新、表投影及平台元数据；PHY 选择仓储和物理保障。仓储写入加入调用者事务，不另开边界或自行提交。

## 原地查询与单参与者保存

```spp
atomic query findBuyer(Buyer);
atomic update saveBuyer(Buyer);
```

```app
repository(argument(0, Buyer.membershipNumber), Buyer)
    using records optional findBuyer;
quantum resource(recordsResource)
    persist(update, argument(0, Buyer.membershipNumber))
    compareVersion(platform(0, Buyer.version)) advanceVersion saveBuyer;
```

示例省略 domain、表、资源和场景声明。场景在显式事务内查询、确认、计算后保存。查询补全同一入口实例，无业务返回；保存只传当前参与者。框架记录查询时事实与平台列作为内部基线，拒绝缺失基线、身份变化或版本冲突，不临时读取最新版本覆盖并发结果。成功保存刷新基线，撤销恢复内部元数据。

## 关系、平台列与定位

```app
tables contracts {
    table SHOP_ORDERS(ShopOrder) {
        primarykey(ShopOrder.orderNumber);
        foreignkey(ShopOrder.buyer) references Buyer;
        notnull long version;
    }
}
```

ShopOrder 在 SPP 直接包含 Buyer。APP 将其业务身份投影为外键，模型外 version 只在物理表与框架元数据中，不进入 SPP 或 JSON。角色/实体/合约均可有自己的表声明；表声明本身不意味着每次角色操作自动保存所有扮演实体。

- argument(index, Type.property)：实际参与者的业务事实。
- 单扮演者角色可以沿用扮演者主键的值，并存入 APP 新增主键列；默认 CRUD 自动推导。旧 singleton 格式仅保留解析兼容，不用于 Petstore。
- platform(index, Type.column)：比较声明在 APP、没有业务模型属性的整数版本列。
- 表内 `auto Type.businessNumber prefix "PREFIX";`：插入前为空的业务字符串编号自动分配并回填，非空值保留。默认前缀加 UUID，不是连续序号或请求防重键。旧 `number(argument(...), "PREFIX")` 仅保留兼容。

主键和外键可能展开同一业务关系，此时同一属性路径约束同一列，不生成重复列；不同属性的名称碰撞仍报错。身份相等按 APP 的直接业务身份，例如会员号，不要求所有可变事实相等。版本保护是原子比较更新，缺少仓储能力明确拒绝。

## 写入操作

|声明|行为|
|---|---|
|persist(insert, ...)|严格新增，存在则失败|
|persist(update, ...)|严格更新，缺失则失败|
|persist(upsert, ...)|明确选择新增或覆盖|
|persist(insertIfAbsent, ...)|缺失新增，存在保持；不意味着相同请求|
|persist(delete, ...)|严格删除，缺失则失败；不是自动冲正|

一个 persist 可用同一参数的多个属性组成键，也可对一维参与者集合逐条操作；集合中途失败由显式边界撤销。集合不支持单个 compareVersion；删除不支持现有更新版本语法，均明确拒绝。多个参数的写入必须共同加入调用者事务。

compareVersion(platform(...)) advanceVersion 在 APP 表中原子检查旧版本并递增；业务不维护版本。旧 compareVersion(argument(...)) 和双目标声明保留兼容，但技术 before/changed 不应作为新的 SPP 业务参与者。平台版本目前要求 advanceVersion，省略时运行层拒绝。

生成服务先验证事务/基线，执行实现，再写入。绑定需要同步本地 update；键字段、参数索引、类型、重复目标及版本列在编译阶段检查。没有守恒属性的 quantum resource(... ) persist(...) 绑定仅表示记录加入量子保障，不把技术记录号或版本伪装成守恒属性。

## 查询与集合

optional 单记录查询无匹配时保留入口并取消内部确认；业务用 if(参与者)/identify 检查，不用 null 或查询返回值。找到后原地补全并确认。技术连接/解码失败仍交 APP/PHY，不作为未找到处理。重复查询不需要构造新的入口对象。

for update 查询用于事务内标量锁定。optional 和锁定查询都不支持集合。普通集合查询无匹配为空集，可直接绑定一维入口，例如：

```spp
atomic query listOrders(key Buyer, ShopOrder[]);
```

```app
tables contracts {
    table SHOP_ORDERS(ShopOrder) {
        primarykey(ShopOrder.orderNumber);
        auto ShopOrder.orderNumber prefix "ORDER";
        foreignkey(ShopOrder.buyer) references Buyer;
    }
}
```

上例以买家参与者的 APP 主键查询关联订单；唯一外键关联和唯一默认仓储可自动推导，无须 repository。歧义或复杂条件须在 APP 显式实现查询。

参与者集合入口生成可变 List，补全集合内容、保留容器实例。普通属性集合也可作为查询目标；不能为集合或返回值虚构业务合约。直接 Java 调用须提供可变集合。

底层 repository 仍保留历史响应协议及属性筛选的兼容能力；标量属性筛选多匹配明确报 REPOSITORY_SCALAR_QUERY_AMBIGUOUS，不能任选一条。旧返回赋值语法已经撤销，不用于新的 SPP 源码。旧数据需要单独迁移。

## 共同资源和数字存储

PHY 将仓储、量子日志及防重存储显式绑定同一 localJdbc 后端，驱动、URL、账户等有效配置一致时复用 DataSource/连接，可看到本事务未提交的写入并共同提交/撤销。不同资源不自动合并；未加入事务写入失败。不能据此提供跨库强一致，也不能把 Saga 的业务补偿叫数据库回滚。

启用 appDdlTables 后可读取已存在的原生表记录，不必先写对象快照。PHY BigDecimal/BigInteger 通过精确十进制转换读取；BigInteger 只接受整数。APP 可将已选择精确数字表示的字段显式映射到 String(width) 存储列，业务与生成模型仍是数字。容量、列与数据升级由部署负责，不自动扩列。

Petstore 本轮只生成并编译生产/测试源码，未执行回归。新键、列、关系和聚合快照不自动兼容旧库，演示数据库已保留。完整业务建模规则见 [业务模型边界](spp-business-model-boundary.md)。
