"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]


    #                       {
    #                         "type": "add",  ----- crt_op["type"] <=> op_type
    #                         "product": "id1",---- crt_op["product"] <=> product_id
    #                         "quantity": 5    ---- crt_op["quantity"] <=> quantity
    #                     }


    def run(self):
        for crt_cart in self.carts:
            # asociez un id cosului curent de cumparaturi
            cart_id = self.marketplace.new_cart()

            # efectuez pe rand operatiile din cos
            for crt_op in crt_cart:
                quantity = crt_op["quantity"]
                product_id = crt_op["product"]

                # caz1: operatie de adaugare in cos
                if crt_op["type"] == "add":
                    while quantity > 0:
                        while True:
                            success = self.marketplace.add_to_cart(cart_id, product_id)

                            if success is True:
                                break
                            # daca produsul nu este in stoc, reincerc mai tarziu
                            time.sleep(self.retry_wait_time)

                        quantity -= 1
                # caz2: operatie de eliminare din cos
                else:
                    while quantity > 0:
                        self.marketplace.remove_from_cart(cart_id, product_id)
                        quantity -= 1
            # cand cosul de cumparaturi este gata, plasam comanda
            cart_products = self.marketplace.place_order(cart_id)

            with self.marketplace.print_lock:
                for product in cart_products:
                    print(self.name + " bought " + str(product))
