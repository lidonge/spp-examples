package free.servpp.xboddemo;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import org.junit.Test;
import static org.junit.Assert.*;

public class XbodIdempotencyTest {
    private JsonNode remote(XbodTestSupport demo, String service, Map<String,?> input, String caller, String serial) throws Exception {
        Object request = demo.request(service,input);
        demo.runtime.install();
        free.servpp.service.runtime.BusinessChecks.restoreScenarioResult(null);
        free.servpp.service.runtime.RemoteServiceIngress.execute(
                free.servpp.service.server.DefaultServiceContainer.getInstance().getService("cboddeposit",service),request,caller,serial);
        var checked = free.servpp.service.runtime.BusinessChecks.scenarioResult();
        if (!checked.passed()) throw new IllegalStateException(checked.code());
        return demo.mapper.valueToTree(request);
    }
    @Test public void reusedRequestSerialWithChangedFactsIsTechnicalRejection() throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo);
            remote(demo,"depositCash",XbodTransactionTest.deposit(100),"BANK-CLIENT","REUSED-SERIAL");
            var failure = assertThrows(IllegalStateException.class, () -> remote(demo,"depositCash",XbodTransactionTest.deposit(200),"BANK-CLIENT","REUSED-SERIAL"));
            assertEquals("REQUEST_ID_REUSED",failure.getMessage());
            var account = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
            XbodTransactionTest.amount("100",account.path("DepositAccount").path("interestBase"));
        }
    }
    @Test(timeout=60000) public void concurrentRemoteCopiesDoNotExecuteTwiceAndReplayAfterCompletion() throws Exception { concurrent(false); }
    @Test(timeout=60000) public void concurrentRemoteReversalsReturnOneReceiptAfterCompletion() throws Exception { concurrent(true); }
    private void concurrent(boolean reversing) throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo);
            var paid = reversing ? demo.call("depositCash",XbodTransactionTest.deposit(100)) : null;
            String service = reversing ? "reverseCash" : "depositCash";
            String agreement = reversing ? "CashReversalAgreement" : "CashDepositAgreement";
            String number = reversing ? "reversalNumber" : "depositNumber";
            var input = reversing ? XbodTransactionTest.reversal(paid.path("CashDepositAgreement"),20261007,false) : XbodTransactionTest.deposit(100);
            var executor = java.util.concurrent.Executors.newFixedThreadPool(2);
            var start = new java.util.concurrent.CyclicBarrier(2);
            try {
                java.util.concurrent.Callable<JsonNode> request = () -> {
                    start.await(10,java.util.concurrent.TimeUnit.SECONDS);
                    return remote(demo,service,input,"BANK-CLIENT","CONCURRENT-REQUEST");
                };
                var a = executor.submit(request); var b = executor.submit(request);
                JsonNode[] replies = new JsonNode[2];
                var calls = java.util.List.of(a,b);
                for (int index=0;index<2;index++) {
                    try { replies[index] = calls.get(index).get(40,java.util.concurrent.TimeUnit.SECONDS); }
                    catch (java.util.concurrent.ExecutionException failure) {
                        assertTrue(failure.toString(),failure.getCause() instanceof IllegalStateException);
                        assertEquals("REQUEST_IN_PROGRESS",failure.getCause().getMessage());
                    }
                }
                assertTrue("At least one original call must finish",replies[0]!=null || replies[1]!=null);
                for (int index=0;index<2;index++) if (replies[index]==null)
                    replies[index]=remote(demo,service,input,"BANK-CLIENT","CONCURRENT-REQUEST");
                var first = replies[0]; var second = replies[1];
                assertEquals(first.path(agreement).path(number),second.path(agreement).path(number));
                assertEquals(first.path(agreement).path("resultInfo"),second.path(agreement).path("resultInfo"));
                assertEquals("SUCCEEDED",first.path(agreement).path("resultInfo").path("status").asText());
                var stored = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
                XbodTransactionTest.amount(reversing ? "0" : "100",stored.path("DepositAccount").path("interestBase"));
                if (reversing) {
                    var receipt=demo.call("readCashReversal",Map.of("CashReversalAgreement",Map.of("reversalNumber",first.path(agreement).path(number).asText())));
                    assertEquals(8,receipt.path("CashReversalPostingLineArray").size());
                    try(var connection=java.sql.DriverManager.getConnection(System.getProperty("spp.xbod.datasource-url"));var statement=connection.createStatement();var rows=statement.executeQuery("SELECT COUNT(*) FROM CASH_REVERSALS")) {
                        assertTrue(rows.next());assertEquals(1,rows.getInt(1));
                    }
                }
            } finally { executor.shutdownNow(); assertTrue(executor.awaitTermination(5,java.util.concurrent.TimeUnit.SECONDS)); }
        }
    }
    @Test public void localCallsAreNotDeduplicatedByRepeatedTransportHeaders() throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo);
            var input = XbodTransactionTest.deposit(100);
            input.put("AppHeader",Map.of("callerId","CLAIMED-CLIENT","requestSerialNumber","REPEATED","callMode","REMOTE","callOrigin","USER"));
            var first = demo.call("depositCash",input); var second = demo.call("depositCash",input);
            assertFalse(free.servpp.service.idempotency.BusinessIdempotencyManager.wasReplay());
            assertNotEquals(first.path("CashDepositAgreement").path("depositNumber"),second.path("CashDepositAgreement").path("depositNumber"));
            var account = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
            XbodTransactionTest.amount("200",account.path("DepositAccount").path("interestBase"));
        }
    }
    @Test public void remoteDepositReplayReturnsOriginalReceiptWithoutDuplicatingFunds() throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo);
            var first = remote(demo,"depositCash",XbodTransactionTest.deposit(100),"BANK-CLIENT","DEPOSIT-001");
            var replay = remote(demo,"depositCash",XbodTransactionTest.deposit(100),"BANK-CLIENT","DEPOSIT-001");
            assertTrue(free.servpp.service.idempotency.BusinessIdempotencyManager.wasReplay());
            assertEquals(first.path("CashDepositAgreement").path("depositNumber"),replay.path("CashDepositAgreement").path("depositNumber"));
            var current = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
            XbodTransactionTest.amount("100",current.path("DepositAccount").path("interestBase"));
        }
    }
    @Test public void remoteReversalReplayDoesNotRepeatReversalOrAccountingLines() throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo); var paid = demo.call("depositCash",XbodTransactionTest.deposit(100));
            var input = XbodTransactionTest.reversal(paid.path("CashDepositAgreement"),20261007,false);
            var first = remote(demo,"reverseCash",input,"BANK-CLIENT","REVERSAL-001");
            var replay = remote(demo,"reverseCash",input,"BANK-CLIENT","REVERSAL-001");
            assertTrue(free.servpp.service.idempotency.BusinessIdempotencyManager.wasReplay());
            assertEquals(first.path("CashReversalAgreement").path("reversalNumber"),replay.path("CashReversalAgreement").path("reversalNumber"));
            var saved = demo.call("readCashReversal",Map.of("CashReversalAgreement",Map.of("reversalNumber",first.path("CashReversalAgreement").path("reversalNumber").asText())));
            assertEquals(8,saved.path("CashReversalPostingLineArray").size());
            var account = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
            XbodTransactionTest.amount("0",account.path("DepositAccount").path("interestBase"));
        }
    }
    @Test public void identicalSerialsFromDifferentCallersAreIndependentRequests() throws Exception {
        try (var demo = new XbodTestSupport()) {
            XbodTransactionTest.open(demo);
            var first = remote(demo,"depositCash",XbodTransactionTest.deposit(100),"BANK-A","SAME-SERIAL");
            var second = remote(demo,"depositCash",XbodTransactionTest.deposit(100),"BANK-B","SAME-SERIAL");
            assertFalse(free.servpp.service.idempotency.BusinessIdempotencyManager.wasReplay());
            assertNotEquals(first.path("CashDepositAgreement").path("depositNumber"),second.path("CashDepositAgreement").path("depositNumber"));
            var account = demo.call("findDepositAccount",Map.of("DepositAccount",Map.of("accountNumber","ACCOUNT-001")));
            XbodTransactionTest.amount("200",account.path("DepositAccount").path("interestBase"));
        }
    }
}
