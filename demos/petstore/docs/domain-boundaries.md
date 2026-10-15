# Petstore 独立业务域与集中部署

> 2026-10-11 事务及存储规则更新：以下此前的共同提交、自动扮演者保存及 CustomerSubject 描述属于历史设计；当前规则见[实施约定](../../../book/references/transaction-storage-v1.md)。当前 APP 选择 AT 普通更新，量子先独立成交，不同模式通过 Saga 恢复，REQUIRED 不改变这一点。Person/Product 由原域显式维护。

|域|拥有的业务事实|跨域协作|
|---|---|---|
|customer|Person（自然人或组织）、RegisteredSubject主体视图，主体登记和资料|销售域通过真实登记、查询及保存原子服务补全主体事实|
|product|Product、CatalogProduct，产品目录和产品文案|销售域导入目录、补全文案，不直接读取产品表|
|inventory|StockLine 角色、InventoryOpeningAgreement，逐商品库存|销售域绑定查询、保存及量子库存服务|
|petshop|Goods、Buyer、Merchant、Cart、CartLine、OrderLine、Receipt及订单场景合约|组织选购、成交、付款和履约，显式声明参与者及事务|

客户域和产品域拥有实体；库存域只有外部Reference、角色和合约，展示业务域不必有实体。订单和购物车在销售域中按角色及合约建模。没有Operator、Shop实体包装和StockBook汇总状态。StockLine.available/reserved/sold为quantum int，CartLine和OrderLine数量为int；这些是number的缺省表示，PHY可全局替换或局部覆盖。

Person扮演Buyer和Merchant。Merchant在take中增加商号、店名和收款金额。Goods由Product扮演；Goods扮演OrderLine、StockLine，Goods与Buyer共同扮演CartLine，Buyer扮演Cart。`Goods goods = Goods;`表示保留整个扮演参与者关系，不是复制一个技术编号。简单角色可与实体继承概念兼容；本轮没有引入实体继承新语法，也没有复杂多实体组合演示。

一键注册在商店注册场景的事务中登记客户主体，再开立买家角色、购物车和回执。编译器通过 Reference 与 take 自动绑定客户域标准原子服务，不调用客户域场景。客户登记号与会员号是不同业务凭证。资料修改先查询提供方，保留该提供方的平台基线，随后保存主体与买家事实。

APP声明customer、product、inventory、petshop集中部署在同一JVM。各域配置目录隔离，服务按域限定名注册；简洁 bind 只选择提供方服务，参数根据跨域参与者身份或 take 转换；保持入口参与者实例。集合按提供方 APP 主键匹配，库存使用 `goods.sku`。查询确认状态和平台基线随调用上下文管理。

PHY选择相同shopDatabase JDBC后端、数据库/schema和共同资源。承载合并兼容资源配置，共用DataSource及事务连接作用域；同JVM或同schema本身不代表共同提交。库存量子记录由提供方负责，消费入口不重复记录；调用处以bounds选择成交范围。

源码、通用生成链路、网页和Java测试输入已同步。本轮只重新生成并编译，没有启动服务或执行回归；共同提交、撤销、并发和恢复仍需运行验收。旧数据库保留，未自动迁移。见[实施与证据](multidomain-implementation.md)。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。


默认查询递归链为 Cart → Buyer → customer.Person，以及 StockLine → Goods → product.Product；各级角色和实体分别使用所属域 APP 主键。客户域 PERSON_REGISTRY、产品域 PRODUCT_FACTS 是根实体表，PRODUCT_CATALOGUE 是目录角色表；RegisteredSubject仅是Person视图，不另建存储表。登记客户和创建目录同时生成本域根实体持久化；消费域角色更新不能隐含写入客户或产品域。查询事实按 take 补全，不靠相同字段名推断。旧数据库未补写根实体记录，已有数据需要迁移或在独立新库重建；本轮不操作现有库。见[查询规范](../../../book/references/participant-query-binding.md)。
