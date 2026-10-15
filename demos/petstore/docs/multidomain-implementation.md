# 多域 Petstore 需求与实施路径

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

本轮实现业务模型和真实多域服务部署声明。业务只在SPP，应用部署在APP，数字表示和资源保障在PHY；生产Java全部生成。用户要求只生成、编译和静态审查，保留旧数据库；完整Goal完成后直接本地提交。

## 需求与实现

|需求|实现产物|
|---|---|
|主体和产品独立域|customer拥有Person，product拥有Product；消费方Reference注明来源|
|角色表达真实业务身份|Person→Buyer/Merchant、Product→Goods、Buyer→Cart、Goods→StockLine/CartLine/OrderLine|
|角色特有事实|take中增加Merchant.shopName/tradingName/cash；整体扮演映射保留Goods或Buyer关系|
|整数逐商品库存|quantum int available/reserved/sold；各业务数量缺省为int；删除StockBook及汇总状态|
|明确场景与合约|入口实际参与者、原地补全，无返回对象、无场景调用；默认参与者名和显式别名并存|
|真实多域集中部署|APP部署customer/product/inventory/petshop；通用本地服务容器按域分派原子服务|
|共同事务|PHY同后端/同schema/共同资源与连接；SPP显式transaction默认REQUIRED|
|调用者量子策略|bounds闭区间，nullable上下限，由量子成交实现自动控制边界并撤销绑定事务|
|常量和国际化|SPP具名常量，APP语言，PHY常量翻译；商品文案中英文|
|页面与自动验收源码|前端组合独立场景，Java测试只准备输入/断言/故障；不补写业务|

域归属和源码见[域边界](domain-boundaries.md)，量子调用语法见[调用范围](quantum-caller-limits.md)。本例没有复杂多实体组合、跨库强一致或远程部署验收；继承概念兼容不等于新增实体继承语法。

## 已完成的实施阶段

1. 明确主体/产品实体归属，去掉Operator/Shop包装，角色和合约关系直接引用参与者；APP保留技术键、版本、防重及外键投影。
2. 完善take角色特有属性、整体参与者映射、外部实体/角色/合约Reference及编译检查。
3. 建立真实客户、产品、库存、销售域，APP明确本地绑定；按域生成模型、服务、角色、存储、常量和部署目录。
4. 迁移整数数量与逐商品量子资源；集合查询按身份补全，普通事实读保护、版本保护与逐元素量子记录；不以整簿固定总量代替逐商品守恒。
5. 保留一键注册跨域共同更新。同期迁移购物、付款、履约、取消和退货，调用处声明bounds，服务体只描述加减；APP没有业务公式。
6. 同步中文网页、测试输入和比较文档，从隔离旧产物后的目录生成编译，静态核对类型、调用链和资源声明。

## 生成编译和验收边界

```bash
mvn -pl :petstore-demo -am test-compile -DskipTests
node --check demos/petstore/src/main/resources/web/app.js
git diff --check
```

最终编译证据见[实施记录](implementation-path.md)。只隔离target中的生成源及生产/测试类，未clean、删除或迁移数据库，未启动服务。编译可证明生成类型和调用关系一致，不能证明事务故障、并发、防重、重启或浏览器行为。历史运行记录属于旧模型。

恢复回归后应验收完整生命周期、多商品并发、跨域写入失败共同撤销、上下限为负/null/动态表达式、逐元素越界及恢复。重新运行须选择独立数据库，原数据升级另定方案。

## 与Java的比较

Java模块、接口、组合对象和事务容器也能实现同样架构。SPP把域归属、扮演、参与者、公式及事务意图写成可检查声明，减少表示代码；生成器与通用运行时承担事实投影、集合身份、版本和资源合并成本。角色是否符合业务仍需人工判断。详细比较见[spp-vs-java](spp-vs-java.md)。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。
