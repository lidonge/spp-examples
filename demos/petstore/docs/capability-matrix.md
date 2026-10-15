# 能力与验收矩阵

本表区分源码展示与运行验收。本轮只生成、编译及静态检查；[历史记录](acceptance-audit.md)不证明当前模型。

|能力|当前源码|业务用途及边界|
|---|---|---|
|实体与真实域|customer.spp、product.spp|Person和Product生命周期独立；inventory可无实体|
|角色和take|00-model、inventory.spp|角色新增经营事实，Goods/Buyer整体扮演关系；复杂组合未在本例展示|
|场景合约及关系|各scene文件与ShopOrder|每动作独立，订单含Buyer、明细含Goods，无技术ID路由|
|默认参与者名|清空车、申请退货|合约Buyer;和入口Buyer，无参唯一绑定；其他场景保留别名|
|稳定实例与集合|query、单参与者save、StockLine[]|原地补全，按业务身份匹配，原子创建动态明细|
|数学与逻辑|20-pricing、05-checks|统一公式、业务舍入、if/for、calculate组合；无规则议程|
|显式校验|各场景check|缺省失败退出block，breakTransction明确撤销，guard只跳过内部|
|量子服务|inventory及资金更新、调用处bounds|实际加减，逐商品守恒；上下限由调用者选择并自动检查|
|事务和资源|transaction、各PHY|默认REQUIRED；同JVM服务和共同JDBC连接配置|
|平台元数据|APP表/版本/防重/编号|技术信息不进SPP，查询基线及原子版本保护|
|数字表示|模型BigDecimal规格，PHY精确匹配替换与字段覆盖|精确检查物理容量，业务舍入显式，业务不写表示方法链|
|国际化|product常量、APP/PHY语言|按常量名翻译商品文案，凭证和数字不随语言改变|
|多域部署|APP application/bind|真实提供方、域限定本地容器，不Mock或跨域读表|
|页面及测试隔离|web、src/test/java|前端组合场景；三份Java测试源码只编译|

本例场景为serial。前端并行读取不是SPP parallel展示，也不是一致快照。REQUIRES_NEW/NESTED为通用语法，本例默认REQUIRED；Saga/TCC、跨库、远程部署和生产授权未被本例验证。[能力缺口](language-gaps.md)记录限制，[实施路径](multidomain-implementation.md)记录当前完成范围。

本轮补充：普通参与者的事务内查询自动生成锁定；混合参与者也修改普通属性时锁定，只有量子变化时不加锁。库存findStockLine不锁定量子事实，lockStock已移除；addCartItem资格查询移出写事务。量子属性逻辑统一归量子域，数据库/TCC/专用量子服务由APP选择、PHY接入，不能把共同JDBC示例当作所有模式的运行证据。参见[事务读取与量子域](../../../book/references/spp-transaction-reads.md)。

本轮四域30个场景（22个变更、8个只读）已按可靠乐观基线缩小事务：普通查询、校验与计算在事务前，事务内原子条件写入；只读准入不成为提交条件，量子成交不推进普通修订标记。预约展示两个顺序事务，预占失败保留已受理合约；付款展示嵌套REQUIRED逻辑边界；非LOCAL策略下量子阶段先成交，跨模式失败采用Saga恢复；本轮develop使用LOCAL共同提交量子与普通更新。详见[事务审计](transaction-boundary-audit.md)和[实施计划](transaction-evolution-plan.md)。
