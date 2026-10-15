# 第31章 取消退货预约与失败处置

> © 2026 S++ project contributors. All rights reserved. [Book copyright](https://github.com/lidonge/spp-examples/blob/main/book/COPYRIGHT.md).

订单已经完成到哪一步，决定后续办理需要哪些服务。取消、退货是新的业务活动；执行失败后的回滚和反交易，是恢复原活动的一致性。这两类过程都可能产生反向变化，却具有不同业务含义。

## 取消与退货按照已发生事实办理

以下各行是不同分支，不能连续套用到同一订单：

|办理起点|业务活动|资金变化|库存变化|
|已经下单，尚未付款|取消未付订单|无|预留两件转回可售|
|已经付款，尚未发货|取消已付订单|商家退回 108 元给买家|预留两件转回可售|
|已经交付，符合退货政策|申请退货|无|无，记录申请与理由|
|退货申请满足批准资格|批准退货|商家退回约定退款金额|对应已售数量转回可售|

[申请退货](../../demos/petstore/src/main/spp/petshop/returns/petshop-scene-requestShopReturn.spp) 使用买家、原订单和申请合约即可表达受理范围。批准退货还需要资金与库存参与，源码见 [批准场景](../../demos/petstore/src/main/spp/petshop/returns/petshop-scene-approveShopReturn.spp)。如果商店要求先收到退回商品，业务模型还应加入收货事实与相应资格，演示规则不能代替所有商店政策。

业务退款使用已经确认的金额和数量。不能直接恢复旧钱包和旧库存快照，因为付款之后可能已经发生其他业务。

## 业务退款与自动反交易的区别

一笔成功付款后来被取消，退款是新业务，具有取消资格、退款合约和办理回执。一笔付款在执行过程中失败，需要自动撤销已完成的量子变化，则是原执行的恢复；业务开发者不用再编写一套量子反交易服务。

普通更新的恢复也要保护后续版本。根据第四篇第21章的契约，恢复必须确认当前版本仍符合撤销条件；存在新版本时不能直接覆盖。当前实现中的普通更新恢复仍需相应补偿能力，不能因为保存逻辑简单，就声称所有部署已经自动完成版本条件反交易。

如果付款跨普通库与量子库，量子资金已成交而订单保存失败，APP 应组织已完成阶段的恢复。恢复全部确认后，才可以认定原付款已撤销；部分恢复失败，则保留待恢复状态。SPP 不应接管远程结果查询和数据库技术重试。

## 预约有意保留已经受理的申请

[预约场景](../../demos/petstore/src/main/spp/petshop/reservation/petshop-scene-reserveShopPet.spp) 使用两个顺序事务。第一个保存受理合约和预约号，第二个执行库存预占并保存确认状态。它允许受理完成后，预占因为库存竞争而失败。

假设可售库存为 10，申请预约 11 件。申请首先被受理，量子预占因下限要求不能成交。系统确认原预占已回滚或反交易之后，业务流程将申请记为拒绝，预约号继续供顾客查询。

与第三篇第17章的流程组织、第四篇第19章的失败处置对应，第二个边界的真实源码如下：

```spp
transaction {
    reserveRequestedInventory bounds {
        StockLine[].available: [0, null];
        StockLine[].reserved: [0, null];
    };
    confirmPetReservation; updatePetReservationAgreement;
} fail {
    if (ResultInfo.failure.recoveryStatus == "ROLLED_BACK" ||
        ResultInfo.failure.recoveryStatus == "REVERSED") {
        findStockLine; identify(StockLine[]);
        rejectPetReservation;
        transaction { updatePetReservationAgreement; }
    }
}
```

`fail` 中的重新查询服务于业务判断：当前库存不足，拒绝原因是库存不足；库存仍够但预约未完成，则采用另一种业务原因。原因定义及计算见 [预约模型](../../demos/petstore/src/main/spp/petshop/reservation/petshop-35-reservation.spp)。这不是让业务人员捕获数据库异常，而是在已确认恢复的前提下，明确处理已经受理的申请。

## 三类失败走不同的路径

|情况|资源与业务状态|处理方式|
|输入数量不合法|尚未成交|校验拒绝，不进入库存交易|
|预占失败且恢复已确认|受理记录保留，原预占已经撤销|执行 fail 中的业务处置，保存拒绝原因|
|预占或恢复结果不明|不能确认资源是否变化|由 APP 确认和恢复，不能直接认定业务拒绝|

技术层可以把已经确定、具有业务含义的失败交给业务层处理。超时不能自动等同库存不足，更不能让 `fail` 再预占一次。当前例子的恢复状态判断正是为了避免这一误判。

如果业务处置本身保存失败，申请也不能假装已经持久化为拒绝。需要保留执行证据，继续确认与恢复。`ResultInfo` 表达本次执行情况，持久预约状态和拒绝原因表达业务办理结果，两者用途不同。

## 用故障验证完成条件

至少检查库存不足、量子成交后普通保存失败和结果未知三种情况。前两类应分别核对库存、申请状态与拒绝原因；未知情况应核对技术恢复记录，确认没有因为重复请求再次预占。

当前预约验证及其范围见 [失败处置说明](../../demos/petstore/docs/reservation-failure-handling.md)。Petstore 的 LOCAL 用例不能单独证明真实跨域资源的全部恢复能力，技术资源与测试证据还要在下一章一起核对。

---

[本篇目录](README.md) · [全书目录](../README.md) · [上一章](30-order-lifecycle.md) · [下一章](32-validation-and-performance.md)
