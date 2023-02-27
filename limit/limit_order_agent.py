from enum import Enum
from trading_framework.execution_client import ExecutionClient, ExecutionException
from trading_framework.price_listener import PriceListener

class OrderType(Enum):
    BUY = 1
    SELL = 2

class LimitOrderAgent(PriceListener):

    def __init__(self, execution_client: ExecutionClient) -> None:
        """

        :param execution_client: can be used to buy or sell - see ExecutionClient protocol definition
        """
        super().__init__()
        self.execution_client = execution_client
        self.interested_pid = "IBM"
        self.limiting_price = 100.00
        self.shares_to_purchase = 1000
        self.orders_to_fill = list()

    def on_price_tick(self, product_id: str, price: float) -> bool:
        """
        Invoked on Market data change. Creates a new buy/sell order and executes buy or sell of shares
        by comparing market price against limiting price.
        Note:- Creation of limiting orders and execution of held orders should ideally be done in a separate method.
        This will ensure on-price_tick only updates a class variable with current market price.
        The separate method will run in parallel and complete the orders when the price meets limiting conditions.
        This is currently not done here as this will require
        creation of threads in a module separate from LimitOrderAgent.
        :param product_id: id of product that has price change
        :param price: the current market price of the product
        :return: Returns a boolean status with success=True & failure=False
        """
        if product_id == self.interested_pid:
            if len(self.orders_to_fill) == 0:
                # Placing buy and sell order pair only if there are no orders left to fulfill.
                # This behaviour is assumed since there is no restriction on how many orders are to be placed and when.
                # It can be changed if there are more restrictions in place such as
                # maximum number of orders to place, cooldown period between orders, etc.
                self.add_order(buy=True, product_id=product_id, amount=self.shares_to_purchase,
                               limit=self.limiting_price)
                self.add_order(buy=False, product_id=product_id, amount=self.shares_to_purchase,
                               limit=self.limiting_price)

            if self.orders_to_fill[0]['order_type'] == OrderType.BUY and price < self.orders_to_fill[0]['limit']:
                amount = self.orders_to_fill[0]['amount']
                try:
                    self.execution_client.buy(product_id=product_id, amount=amount)
                    self.orders_to_fill.pop(0)
                except ExecutionException:
                    print('Could not complete buy order')
                    return False
            elif self.orders_to_fill[0]['order_type'] == OrderType.SELL and price >= self.orders_to_fill[0]['limit']:
                amount = self.orders_to_fill[0]['amount']
                try:
                    self.execution_client.sell(product_id=product_id, amount=amount)
                    self.orders_to_fill.pop(0)
                except ExecutionException:
                    print('Could not complete sell order')
                    return False
            return True
        return False

    def add_order(self, buy: bool, product_id: str, amount: int, limit: float):
        """
        Places a buy or a sell order.
        :param buy: Boolean flag which buys shares if set to True and sells if set to False.
        :param product_id: id of product on which limiting order is placed
        :param amount: Number of shares to buy or sell
        :param limit: limit at which to buy or sell
        :return: None
        """
        order_type = OrderType(1)
        if buy:
            order_type = OrderType.BUY
        else:
            order_type = OrderType.SELL
        self.orders_to_fill.append({'order_type': order_type, 'product_id': product_id, 'amount': amount, 'limit': limit})
