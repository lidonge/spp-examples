# 参与者内置增删改查服务

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

实体、角色及有存储映射的合约的标准增删改查由运行时提供，不要求在 SPP 重复声明空的原子服务。场景仍显式声明参与者、校验和事务边界。

| 操作 | 服务名 | 业务效果 |
| --- | --- | --- |
| 主键查询 | `find` + 类型名 | 原地补全参与者及其扮演者事实，设置 identified |
| 新增 | `insert` + 类型名 | 保存当前参与者自身的事实 |
| 修改 | `update` + 类型名 | 更新当前参与者自身的事实 |
| 删除 | `delete` + 类型名 | 删除当前参与者自身的存储记录 |

例如，已有 `Buyer` 和 `Cart` 模型，场景可直接写 `findBuyer;`、`insertCart(cart);`，不写 `atomic query findBuyer(Buyer);` 等重复声明。没有参数时按参与者类型唯一绑定；有多个同类型实例时显式传参。集合沿用同一个服务名，如 `insertCartLine(cart.lines);`，逐元素执行标准操作；`findCartLine(lines)` 补全已提供身份的元素，不代表任意条件检索全部明细。

编译器建立内置服务签名并生成 APP/PHY 到通用运行时仓储的技术桥接。单个参与者与集合共存时使用内部实现区分，SPP 调用不增加后缀。标准服务不返回替换参与者，实例身份保持不变。角色查询按扮演关系补全；普通写入不级联保存扮演者或子参与者。

跨域标准 CRUD 也无需声明代理：已有 `Reference Person from customer.Person` 和 `take Buyer as Person` 时，场景直接调用 `insertPerson(customer)`、`updatePerson(customer)`。服务名明确本次维护的是 Person；Buyer 通过已定义的扮演关系提供参与者事实，生成代码调用客户域服务并回填原 Buyer。`insertBuyer(customer)`、`updateBuyer(customer)` 则独立维护商店域的角色表，不隐式维护 Person。

同域的显式 take 适用相同规则。无参数调用先寻找唯一的同类型参与者；没有同类型参与者时才寻找唯一的可扮演者，存在多个候选必须显式传参。只有明确身份或唯一显式 take 才允许适配，不按相似字段推测关系；仍有域提供方或映射歧义时编译报错。APP 显式绑定只用于定制。

APP 定义表、主键、默认事务模式、业务编号及必要的定制绑定；PHY 决定物理存储与实现机制。缺少或有歧义的存储、参与者、域提供方仍是编译错误。内置 CRUD 不解除单表写入、量子属性归属、乐观保障及事务策略校验。

复杂查询、非主键查询、业务计算、业务校验及量子变更仍显式定义。既有显式服务声明继续兼容，其明确约定优先于内置推导；不凭服务名覆盖用户提供的业务实现。

Petstore 使用本规范移除标准 CRUD 声明，保留复杂查询、跨角色定制服务与业务原子服务。只做生成、编译及静态核对，本轮不执行回归测试。

实施核对：`mvn -pl :petstore-demo -am clean test-compile -DskipTests` 及最终增量编译通过。静态核对确认实体更新使用运行时仓储，明细集合使用集合签名，外域提供方具备单参与者与集合查询入口，纯视图角色查询补全实体。新增编译器用例源码已编译，未执行；未启动应用或修改数据库。最终编译日志为 `/tmp/spp-implicit-crud-final-compile.log`。

整体检查补充：删除主体登记、主体更新及经营者主体查询的三条 SPP 代理声明和三条默认 APP bind；通过 Reference/take 自动生成对应客户域调用。重新 clean 生成与编译通过，静态确认 Person 与 Buyer 分别持久化、旧代理生成文件已移除、源码没有重复标准 CRUD 声明。同步修订文档中的旧代理绑定、NESTED 支持和跨模式共同提交说明。新增扮演适配、禁止按相似字段适配及多候选歧义用例源码，只编译未执行。此次最终日志为 `/tmp/spp-crud-overall-final-compile.log`。


## 查询条件参与者和自动业务编号

标准单条查询仍按 APP 主键自动生成。关联集合查询可在 SPP 直接标出条件参与者：

```spp
atomic query listOrders(key Buyer, ShopOrder[]);
Scenario serial readShopOrders(Buyer key, ShopOrder[] orders) { listOrders; }
```

`key` 修饰参与者，不是基本属性参数。上述查询以 Buyer 的 APP 主键作为条件，补全订单集合；参与者仍由调用方提供，服务原地补全集合。第一版自动推导要求一个标记的单体条件参与者、一个结果集合、唯一的 APP 外键关联和唯一默认仓储。多个关联或复杂筛选在 APP 显式实现查询，不按字段名称猜测关系。`key` 仍可作为普通实例名。

业务编号策略属于 APP 表定义：

```app
 table SHOP_ORDERS(ShopOrder) {
     primarykey(ShopOrder.orderNumber);
     auto ShopOrder.orderNumber prefix "ORDER";
     foreignkey(ShopOrder.buyer) references Buyer;
 }
```

`auto` 针对已声明业务含义的字符串属性，只在插入前为空时生成并回填传入参与者，已有编号保持不变，修改和删除不生成编号。默认实现是前缀加 UUID；不表示连续序号。集合插入逐元素处理。声明须放在属性自身的存储表，不能通过角色表替扮演者编号。原 scope 中的 `number(...)` 保留兼容，Petstore 不再重复使用。

单扮演者角色的 APP 新增主键：当角色有一个扮演者，扮演者具有一个已在 APP 确定的主键，并通过 takeall/mapsame 提供该身份属性时，默认 CRUD 可将该值映射到角色表新增的唯一主键列。例如 Merchant 的 customerNumber 来源于客户域 Person，APP 的 merchantRowId 存储该值；SPP 不声明 merchantRowId，APP 不重复声明 findMerchant/insertMerchant 的 repository。跨域主键信息从原域 APP 读取，不猜测字段顺序。查询前需提供扮演者身份，查不到时参与者未确认。该规则沿用扮演者身份，不生成新的独立业务身份。

## APP-only 主键的已有存储身份

无法由业务属性或完整扮演者主键推导的 APP-only 主键，仍属于存储身份。默认 find 服务使用框架保存的参与者存储身份进行主键查询，默认普通更新和删除也使用该身份；SPP 不增加 id 字段，不按业务属性相似度猜测记录。生成规则中的 `@storageIdentity` 是内部元数据标记，不是 SPP 语法或业务属性。

只有已通过读取或创建记录建立了存储身份的参与者，才能沿此路径再次查询或修改。没有身份的默认查询保留入口实例及其事实，标记为未确认；没有身份的更新明确拒绝。若首次定位需要会员号、电话号码等非主键条件，仍由 APP 显式实现相应查询，由读取结果建立身份。该规则不新增 APP 外部技术身份输入协议，也不为任意类型的 APP-only 主键自动生成插入值；新记录的主键仍需已有 APP 编号或扮演者映射机制。

多个扮演者的键完整映射到角色 APP 主键时，继续按扮演者组合身份查询和写入角色表；只有不能完整推导的存储身份才使用框架元数据。显式声明的业务查询不会因其未配置的主键而被改成其他查询，原有诊断和显式非主键查询约定继续适用。

## 技术启动初始化

APP `web.start` 在服务就绪前执行数据库种子准备。框架用专用技术初始化上下文执行这些生成服务：普通插入改为仅缺失时插入，量子初值在其配置的数据源事务中仅缺失时补齐，不覆盖已有余额或库存。不同数据源不承诺共同提交；失败时不发布 readiness，保留已完成种子步骤供重试，不执行业务反交易/补偿。该上下文不用于网页业务请求，正常业务 insert 仍要求原有事务资源协调与重复插入校验。

此机制不提供通用旧库修复，也不把带量子属性的新建业务交易自动视为技术初始化。Petstore 的具体未验证范围见 [known issues](../../demos/petstore/docs/known-issues.md)。

建立零量子事实与非零入账分开：同库零事实随本地角色事务共同提交；分库先在角色事务内写入技术待办，提交确认后再 missing-only 建立量子零记录。回滚不发送远端创建，失败待办在启动、查询或技术 API 中重放，不产生交易流水、不覆盖已有成交值，不让 SPP 拆分开户或编写业务补偿。此机制提供持久技术恢复，不声称分库瞬时原子提交；非零资金和库存变化仍由显式双边量子服务完成。

## 可扩展组合角色的独立身份

Role 的参与者成员声明内在组合；每条 take 将其显式来源与内在成员联合，多条 take 形成备选方案。重复的参与者整体映射不再必需。新角色表不写主键时自动配置 APP-only String roleId；显式 `identity independent;` 禁用单扮演者主键复用，插入生成独立 UUID，后续 find/update/delete 使用查询元数据中的稳定身份。旧的显式业务/组合键继续兼容，但不是新增可扩展角色的缺省身份。

`performers inline;` 与 `performers in 表名;` 分别选择同表和独立关系表，扮演者主键只作为关联。非主键业务定位仍显式定义 APP 查询，不凭扮演者当前组合猜测角色主键。详见[角色组合与存储](role-composition-and-storage.md)。
