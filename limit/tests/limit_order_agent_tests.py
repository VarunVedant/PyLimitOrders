import unittest
from unittest.mock import Mock
from limit.limit_order_agent import LimitOrderAgent
from trading_framework.execution_client import ExecutionClient, ExecutionException

class LimitOrderAgentTest(unittest.TestCase):

    def test_add_order(self):
        execution_client_mock = Mock(ExecutionClient)
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.add_order(buy=True, product_id='Foo', amount=500, limit=50)
        agent.add_order(buy=False, product_id='Foo', amount=500, limit=50)
        self.assertEqual(len(agent.orders_to_fill), 2)

    def test_buy_order_at_limit(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.buy.return_value = None
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 100)
        self.assertFalse(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 2)

    def test_buy_order_over_limit(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.buy.return_value = None
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 101)
        self.assertFalse(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 2)

    def test_buy_order_below_limit(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.buy.return_value = None
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 99)
        self.assertTrue(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 1)

    def test_sell_order_at_limit(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.sell.return_value = None
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 99)
        agent.on_price_tick('IBM', 100)
        self.assertTrue(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 0)

    def test_sell_order_over_limit(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.sell.return_value = None
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 99)
        agent.on_price_tick('IBM', 101)
        self.assertTrue(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 0)

    def test_buy_order_failure(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.buy.side_effect = ExecutionException()
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 99)
        self.assertTrue(execution_client_mock.buy.called)
        self.assertEqual(len(agent.orders_to_fill), 2)

    def test_sell_order_failure(self):
        execution_client_mock = Mock(ExecutionClient)
        execution_client_mock.sell.side_effect = ExecutionException()
        agent = LimitOrderAgent(execution_client=execution_client_mock)
        agent.on_price_tick('IBM', 99)
        agent.on_price_tick('IBM', 101)
        self.assertTrue(execution_client_mock.sell.called)
        self.assertEqual(len(agent.orders_to_fill), 1)
