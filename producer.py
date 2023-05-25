"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()

        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        # fiecare producator va avea un id unic dupa care va putea fi identificat
        self.producer_id = self.marketplace.register_producer()
        self.name = kwargs["name"]


                # [
                #     "id2",  ---------- product[0]  <=> id
                #     2,      ---------- product[1]  <=> cantitate
                #     0.18    ---------- product[2]  <=> timp-asteptare
                # ]


    def run(self):
        while 1:
            for crt_product in self.products:
                quantity = crt_product[1]
                # producatorul curent va fabrica quantity bucati din produsul crt
                while quantity > 0:
                    #astept sa produca o bucata din produsul curent
                    time.sleep(crt_product[2])

                    #adaug bucata produsa in marketplace
                    while 1:
                        success = self.marketplace.publish(self.producer_id, crt_product[0])
                        if success is True:
                            break
                        # daca nu mai am loc de depozitare, reincerc mai tarziu
                        if success is False:
                            time.sleep(self.republish_wait_time)

                    quantity -= 1 # am mai adaugat un produs in piata
