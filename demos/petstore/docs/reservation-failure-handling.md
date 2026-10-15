# 预约受理后的失败业务处置

预约先提交受理申请，再尝试量子库存预占。申请数量超过可用库存时，第二个事务失败，申请仍保留。库存撤销由框架及选定量子实现负责；SPP 的 fail 块重新查询库存，记录预约被拒绝及业务原因，并用独立事务保存申请的处理结果。

## 完整源码入口

[预约场景](../src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp)与[合约、校验和计算](../src/main/spp/petshop/reservation/petshop-35-reservation.spp)共同表达：

```spp
transaction { insertPetReservationAgreement; }
prepareReservationInventory; findStockLine; identify(StockLine[]);
transaction {
    reserveRequestedInventory bounds {
        StockLine[].available: [0, null]; StockLine[].reserved: [0, null]; };
    confirmPetReservation; updatePetReservationAgreement;
} fail {
    if (ResultInfo.failure.recoveryStatus == "ROLLED_BACK" || ResultInfo.failure.recoveryStatus == "REVERSED") {
        findStockLine; identify(StockLine[]);
        rejectPetReservation;
        transaction { updatePetReservationAgreement; }
    }
}
```

ResultInfo 是场景系统内置参与者，不出现在入口中，也不声明 Role。编译器在合约中提供 resultInfo；系统失败信息供场景读取，业务拒绝原因存放在合约自身的枚举属性 rejectionReason。原子计算只读取库存及申请数量，不读取异常对象或系统参与者。

|输入 / 故障|已受理申请|最终库存（可用 / 预占）|业务结果|
|---|---|---|---|
|可用 10，申请 11|保留同一预约号|10 / 0|REJECTED，INSUFFICIENT_STOCK|
|可用 10，申请 2|保留同一预约号|8 / 2|RESERVED，拒绝原因为空|
|预占足够，随后普通保存失败|保留同一预约号|恢复为 10 / 0|REJECTED，RESERVATION_NOT_COMPLETED；不能误记为库存不足|
|提交或恢复结果不确定|原申请可凭预约号核对|不得宣称已恢复|RECOVERY_REQUIRED；技术失败继续交给 APP/PHY|
|fail 的业务保存也失败|已受理事实仍保留|此前技术恢复不被改写|不宣称处置完成，原错误与附加处置错误交给 APP/PHY|

越界拒绝时没有成功量子成交，不需要再执行反交易；LOCAL 中已执行但未提交的变化随数据库事务回滚；非 LOCAL 中已成交的量子阶段由系统通过反交易恢复。fail 不手写库存加回，不删除已经受理的申请，不把查询得到的当前值覆盖回量子库。

处置完成后，本次 ResultInfo.status 仍为 FAILED，handled 为 true，表示原预占失败已处置。场景可正常返回该业务结果；远程幂等重放返回同一处理结果，不重复受理或补偿。查询历史申请读取持久化的业务状态和拒绝原因，系统 resultInfo 本身是本次返回元数据，不默认进业务表。

第一版支持串行场景中外层事务的 fail，嵌套或并行分支中的 fail 编译报错；多个入口合约时必须用 fail(目标合约) 选择。完整协议及限制见[系统结果与失败处理](../../../book/references/spp-transaction-failure-handling.md)。更一般的补偿政策仍需按业务定义，不能从此例自动推导。


本例的系统失败事实包括 QUANTUM_BOUND_REJECTED、QUANTUM_SETTLEMENT 阶段、失败服务、StockLine.available 属性、尝试值 -1 和下限 0；业务拒绝原因仍由恢复后的库存事实和申请数量确定，不从 Java 异常类推导。

## 验证记录

2026-10-13，develop 完整生成链路和回归通过，共 1,104 项测试，其中 Petstore 36 项。库存不足样例验证保留同一预约号、数量 11、状态 REJECTED、原因 INSUFFICIENT_STOCK，库存保持可用 10 / 预占 0；重发原始输入和相同流水号，回放相同预约号及 ResultInfo，不重复受理。普通保存故障样例验证恢复库存后另开事务保存 RESERVATION_NOT_COMPLETED，不误记为库存不足。

系统量子反交易另由运行框架的真实 JDBC 成交后失败测试验证；本轮 Petstore 使用 LOCAL 部署，未运行真实分布式 TCC 或外部量子服务验收。
