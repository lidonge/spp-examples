# 多域本地服务绑定

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

业务场景与部署分离。消费方声明服务意图，APP把无业务实现的query/update/calculate绑定同类别提供方原子服务；不能绑定场景，也不能在普通原子业务中互调。提供方是真实SPP域，不是Mock。

本域服务自动继承唯一的 `local` scope 及其 header，不再重复罗列普通服务名。显式配置优先，多个 local scope 对未绑定服务产生歧义时编译报错。标准主键仓储与唯一外部参与者服务自动生成；复杂查询、量子资源、防重及定制跨域目标仍显式配置，见[APP 默认本地绑定](../../../book/references/app-default-local-binding.md)。

```spp
Reference Person from customer.Person { String name; String email; String address; }
```

Reference可来源于实体、角色或合约，编译期核对提供方及字段类型。旧无from形式兼容，多域例明确来源；导入量子事实不产生第二份所有权。

跨域定制查询只声明目标，参数由参与者身份或显式扮演关系决定：

```spp
Reference CatalogProduct from product.CatalogProduct {
    String sku; String name; String category; String description; boolean active;
}
take Goods as CatalogProduct { mapsame; }
```

```app
bind importCatalogue to product.listCatalogue;
```

产品域的 `listCatalogue(CatalogProduct selection, CatalogProduct[] products)` 在本域 APP 中用 repository 声明在售条件；消费域的 `importCatalogue(Goods selection, Goods[] goods)` 用上面的 take 对应参数。编译器核对参与者身份、参数数量及集合维度，调用生成的扮演映射；同名字段不能替代 take。集合依据提供方 APP 主键匹配，入口实例、已有成员及集合容器保持稳定。旧 positional facts/identity 块仅保留兼容，不再用于本演示。

默认查询依据 APP 主键唯一定位，未命中或主键事实未补全时确认失败，不退回按其他字段搜索。角色有自身表时先查角色，再沿 take 递归查询扮演者；无自身表的角色视图直接沿 take 查询。跨域根实体通过所属域的主键服务读取，按生成映射补全角色。例如 `Cart → Buyer → customer.Person`、`StockLine → Goods → product.Product`。不会把角色售价或钱包当作外部实体属性复制。

本域非主键查询直接由 repository 实现，不另写 bind。Petstore 的在售商品、买家订单和产品目录筛选是这些样例；复杂 SQL/XML 方言尚未新增。参见[参与者查询规范](../../../book/references/participant-query-binding.md)。

目录位于META-INF/spp/domains/域名，服务限定名如inventory.reserveInventory；应用清单聚合各域PHY、DDL、角色、常量、网页入口。提供方量子服务记录逐元素变化，消费入口不重复记账。bounds由场景调用者约定，随调用投影传入量子提供方，由具体成交实现控制范围。

通用承载合并兼容资源，冲突拒绝。相同JVM/schema不足以保证共同提交，PHY必须配置共同后端/事务资源及连接作用域。现阶段存储业务类型重名冲突拒绝，没有自动重命名表/类型映射。

本轮只有生成编译与静态证据，未验证运行共同提交、回滚或页面。参见[域边界](domain-boundaries.md)与[实施记录](implementation-path.md)。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。

默认角色查询改为沿 take 递归读取根实体，客户域补充 PERSON_REGISTRY 和 findPerson，产品域补充 PRODUCT_FACTS 和 findProduct。客户登记和目录建立会生成本域根实体及角色记录的持久化；本地角色的普通更新不会自动写入外域实体。跨域资料更新仍明确调用客户域服务，沿查询基线保存。库存 Reference 服务按参与者的规范域身份和操作类别自动匹配唯一提供方；目录导入、文案本地化及库存初始化保留定制目标绑定；主体登记、更新及查询通过 Reference 和显式 take 自动解析内置 CRUD，不再声明本地代理或默认 bind。不能把新增客户主体和新增买家角色当成同一写入。

SHOP_MERCHANTS 展示 APP 新增 merchantRowId 技术主键，生成的 CRUD 使用该主键定位角色记录，SPP 不定义或显式操作该字段。Merchant 只有 Person 一个扮演者，新增主键列的值沿用 Person 的 customerNumber；findMerchant 与 insertMerchant 都默认生成，无需显式 repository 声明。列表订单及在售商品保留复杂 repository 样例，产品域目录筛选也保留非主键条件查询。
