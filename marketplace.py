"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import logging
import unittest
from threading import Lock
from logging.handlers import RotatingFileHandler
from .product import Tea, Coffee

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer

        self.market = {}
        # dictionar ce asociaza un producator cu o lista cu toate produsele din stoc
        # daca un producator are in stoc 2 buc. dintr-un produs, acesta va aparea de 2 ori in lista
        # !!! acesta se va modifica doar la publicarea de noi produse sau la plasarea comenzilor

        self.products = {}
        # dictionar ce asociaza un produs cu o lista ce contine id-urile producatorilor ce au in ->
        # -> stoc produsul respectiv
        # daca produsul 1 e in stocul a 2 producatori => ambii vor aparea in lista ->
        # -> corespunzatoare produsului 1
        # !!! ne ajutam de acesta pentru gestionarea stocului in timpul adaugarilor/eliminarilor->
        # -> de produse in/din cos


        self.carts = {}
        # dictionar ce asociaza id-ul fiecarui cos de cumparaturi cu o lista de perechi formate ->
        # -> din produsul curent si producatorul corespunzator acestuia

        self.no_producers = 0
        self.no_carts = 0

        self.no_producers_lock = Lock() # lock pt inreg de noi producatori
        self.no_carts_lock = Lock() # lock pt inreg de noi cosuri de cumparaturi
        self.modify_cart_lock = Lock() # lock pt modificarea continutului carts-urilor
        self.print_lock = Lock()

        self.producers_lock = {} # dictionar intre producator si lock-ul asociat lui
        # un lock pt fiecare producator-cheie din dict self.market

        self.products_lock = {} # dictionar intre produs si lock-ul asociat lui
        # un lock pt fiecare produs-cheie din dict self.products

        self.logger = logging.getLogger(Marketplace.__name__)
        self.logger.setLevel(logging.INFO)

        self.rotating_file_handler = RotatingFileHandler("file.log", maxBytes = 30 * 1024, backupCount = 20)

        self.formatter = logging.Formatter("%(asctime)s – %(name)s – %(levelname)s:%(message)s", datefmt = "%d/%m/%Y %I:%M:%S")
        self.rotating_file_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.rotating_file_handler)


    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info("Start function register_producer()")

        with self.no_producers_lock:
            # id-ul producatorilor vor arata astfel: p0, p1, p2 ...
            producer_id = "p" + str(self.no_producers)
            self.no_producers += 1 #am inregistrat un nou producator

        #initializez lock-ul corespunzator noului producator
        self.producers_lock[producer_id] = Lock()

        self.logger.info("Producer %s was registered", producer_id)

        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        self.logger.info("Start function publish(%s, %s)", producer_id, str(product))

        # folosit doar pentru checkstyle errors, pentru a micsora lungimea liniilor de cod
        prod_id = ""
        prod_id = producer_id

        # verific daca mai am loc in stocul producatorului curent
        if prod_id in self.market and len(self.market[prod_id]) >= self.queue_size_per_producer:
            self.logger.info("Product %s can't be published", str(product))
            return False # nu e loc in stoc! :(

        # daca produsul nu a fost inregistrat anterior
        if product not in self.products_lock:
            self.products_lock[product] = Lock()

        with self.producers_lock[producer_id]:
            # inregistrez produsul in stocul oficial
            if producer_id in self.market:
                self.market[producer_id].append(product)
            else:
                # daca producatorul este nou pe piata, initalizez lista lui vida de produse
                self.market[producer_id] = []
                self.market[producer_id].append(product)

        with self.products_lock[product]:
            #adaug produsul in dictionarul ajutator
            if product in self.products:
                self.products[product].append(producer_id)
            else:
                # daca e prima aparitie a produsului pe piata, initializez lista vida de ->
                # producatori corespunzatoare lui
                self.products[product] = []
                self.products[product].append(producer_id)

        self.logger.info("Product %s was published", str(product))

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info("Start function new_cart()")

        # inregistrez un nou cos de cumparaturi
        with self.no_carts_lock:
            cart_id = self.no_carts
            with self.modify_cart_lock:
                self.carts[cart_id] = [] # la inceput acesta e gol
            self.no_carts += 1

        self.logger.info("Cart %d was created", cart_id)

        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        self.logger.info("Start function add_to_cart(%d, %s)", cart_id, str(product))

        # daca produsul nu a mai fost fabricat anterior sau daca a fost fabricat,->
        # -> dar momentan nu exista nicio bucata
        if product not in self.products or product in self.products and self.products[product]==[]:
            self.logger.info("Product %s can't be added to cart", str(product))
            return False

        # ma asigur ca nu modifica 2 thread-uri in acelasi timp acelasi produs
        with self.products_lock[product]:
            if len(self.products[product]) > 0:
                # prin conventie aleg primul producator din lista
                producer_id = self.products[product][0]
                # marchez produsul curent ca fiind indisponibil pentru ceilalti consumatori
                self.products[product].remove(producer_id)

        # adaug in cosul de cumparaturi produsul dorit
        self.carts[cart_id].append((product, producer_id))

        self.logger.info("Product %s was added to cart", str(product))
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("Start function remove_from_cart(%d, %s)", cart_id, str(product))

        producer_id = ""
        # caut in cos produsul pe care doresc sa-l elimin
        for pair in self.carts[cart_id]:
            if pair[0] == product:
                # retin producatorul acestuia pt a-l putea pune la loc in dictionar
                producer_id = pair[1]
                break

        # pun produsul inapoi la raft, il fac disponibil pentru ceilalti consumatori
        with self.products_lock[product]:
            if producer_id != "":
                self.products[product].append(producer_id)

        with self.modify_cart_lock:
            # scot din cos produsul
            self.carts[cart_id].remove((product, producer_id))

        self.logger.info("Product %s was removed from cart", str(product))

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        self.logger.info("Start function place_order(%d)", cart_id)

        #lista in care voi adauga toate produsele din cosul de cumparaturi
        products_list = []
        # corner case cand mi se da un cart_id inexistent
        if cart_id not in self.carts:
            return products_list

        # lista de perechi (produs, producator) pt toate produsele din cos
        pairs_list = self.carts[cart_id]

        for pair in pairs_list:
            product = pair[0]
            producer_id = pair[1]

            # adaug produsul in lista ce reprezinta rezultatul final
            products_list.append(product)

            with self.producers_lock[producer_id]:
                # elimin produsul de pe piata, corespunzator producatorului sau
                self.market[producer_id].remove(product)

        with self.modify_cart_lock:
            # cand am terminat cu toate produsele din cos, nu mai am nevoie de ->
            # -> acesta, deci il elimin
            self.carts.pop(cart_id)

        self.logger.info("Finish function place_order")

        return products_list

class TestMarketplace(unittest.TestCase):
    """
    Unit tests for Marketplace class methods.
    """
    def setUp(self):
        # Tested class
        self.marketplace = Marketplace(5)
        self.producer0 = self.marketplace.register_producer()
        self.cart0 = self.marketplace.new_cart()
        self.product0 = Tea(name="Cactus fig", type="Green", price=3)
        self.product1 = Coffee(name="Indonezia", acidity="5.05", roast_level="MEDIUM", price=1)

    def test_register_producer(self):
        """
        Test pentru functia register_producer() -> verifica daca id-ul intors de acesta
        respecta formatul impus de noi.
        """
        producer1 = self.marketplace.register_producer()
        producer2 = self.marketplace.register_producer()
        producer3 = self.marketplace.register_producer()

        self.assertTrue(producer1 == 'p1')
        self.assertTrue(producer2 == 'p2')
        self.assertTrue(producer3 == 'p3')

    def test_publish(self):
        """
        Test pentru functia publish(producer_id, product) -> verifica atat
        daca se adauga produsul cum trebuie atunci cand coada producatorului
        nu este plina, cat si daca nu se mai adauga atunci cand coada este plina.
        """

        # Adaugam 5 produse pana umplem coada producatorului, toate operatiile
        # ar trebui sa se execute cu succes.
        self.assertTrue(self.marketplace.publish(self.producer0, self.product0))
        self.assertTrue(self.marketplace.publish(self.producer0, self.product1))
        self.assertTrue(self.marketplace.publish(self.producer0, self.product0))
        self.assertTrue(self.marketplace.publish(self.producer0, self.product1))
        self.assertTrue(self.marketplace.publish(self.producer0, self.product0))

        # Incercam sa mai adaugam unul, dar coada producatorului este plina, deci
        # ar trebui sa se intoarca false.
        self.assertFalse(self.marketplace.publish(self.producer0, self.product1))

    def test_new_cart(self):
        """
        Test pentru functia new_cart() -> verifica daca id-ul intors de acesta este
        corect.
        """
        cart1 = self.marketplace.new_cart()
        cart2 = self.marketplace.new_cart()
        cart3 = self.marketplace.new_cart()

        self.assertTrue(cart1 == 1)
        self.assertTrue(cart2 == 2)
        self.assertTrue(cart3 == 3)

    def test_add_to_cart(self):
        """
        Testeaza metoda add_to_cart(cart_id, product) -> verifica atat daca se
        adauga cu succes atunci cand produsul este disponibil, cat si daca acesta
        nu se adauga cand nu este disponibil.
        """
        # Incercam sa adaugam un produs indisponibil.
        self.assertFalse(self.marketplace.add_to_cart(self.cart0, self.product0))
        # Cart-ul trebuie sa fie tot gol.
        self.assertTrue(self.marketplace.carts[self.cart0] == [])

        self.marketplace.publish(self.producer0, self.product0)
        self.marketplace.publish(self.producer0, self.product1)

        # Acum incercam sa adaugam 2 produse disponibile si ambele apeluri
        # ar trebui sa intoarca True.
        self.assertTrue(self.marketplace.add_to_cart(self.cart0, self.product0))
        self.assertTrue(self.marketplace.add_to_cart(self.cart0, self.product1))

    def test_remove_from_cart(self):
        """
        Testeaza metoda remove_from_cart(cart_id, product) -> verifica daca
        se sterge produsul din cart.
        """
        self.marketplace.publish(self.producer0, self.product0)
        self.marketplace.publish(self.producer0, self.product1)

        self.marketplace.add_to_cart(self.cart0, self.product0)
        self.marketplace.add_to_cart(self.cart0, self.product1)

        self.marketplace.remove_from_cart(self.cart0, self.product1)

        # Produsul self.product1 n-ar trebui sa mai existe in cart
        # dupa remove.
        cart_content = self.marketplace.carts[self.cart0]
        result = True
        if (self.product1, self.producer0) in cart_content:
            result = False
        self.assertTrue(result)

    def test_place_order(self):
        """
        Testeaza metoda place_order(cart_id) -> verifica daca produsele
        intoarse de metoda sunt exact cele din cart.
        """
        self.marketplace.publish(self.producer0, self.product0)
        self.marketplace.publish(self.producer0, self.product1)

        self.marketplace.add_to_cart(self.cart0, self.product0)
        self.marketplace.add_to_cart(self.cart0, self.product1)

        # Lista intoarsa de place_order trebuie sa contina aceleasi produse
        # ca acelea pe care le-am introdus in c0.
        cart_products = self.marketplace.place_order(self.cart0)
        self.assertListEqual(cart_products, [self.product0, self.product1])

        # Cartul trebuie sters din dictionar.
        result = True
        if self.cart0 in self.marketplace.carts:
            result = False

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
