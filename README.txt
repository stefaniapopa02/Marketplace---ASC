Popa Stefania
336CB

    Implementarea temei simuleaza functionarea unei piete in viata reala, in care
exista atat producatori, cat si consumatori, cei dintai putand fabrica produse 
de acelasi tip.
    Pentru stocarea si prelucrarea tuturor datelor, am folosit 3 structuri de date:

- un dictionar in care fiecare producator are asociata o lista cu produse
----- acesta reprezinta stocul oficial si se modifica doar la publicare unui nou
produs (se adauga produse) sau la plasarea unei comenzi (se elimina produse) 

- un dictionar in care fiecare produs existent la un moment dat pe piata are asociata
o lista de producatori
----- daca un producator are in stoc 2 bucati din produsul curent, atunci respectivul
producator va aparea de 2 ori in lista asociata produsului
----- il folosim ca pe un dictionar ajutator pentru gestionarea produselor si a 
cosurilor de cumparaturi

- un dictionar in care stocam asocierea dintre un cos de cumparaturi si o lista de 
perechi (produs din cos, producatorul acestuia)

    Pentru a nu avea probleme de sincronizare si de gestionare a produselor, folosesc 
cate un lock pentru fiecare producator din self.marketplace si de asemenea, cate un 
lock pentru fiecare produs din self.products.

    Deoarece id-urile producatorilor si ale cosurilor de cumparaturi trebuie sa fie 
unice, folosesc cate un contor pentru fiecare dintre cele 2.

    Producatorul are asociata operatia de publicare a unui produs, iar consumatorul
are asociate operatiile de adaugare sau eliminare a unui produs in/din cosul de 
cumparaturi.
    
    De fiecare data cand se publica un produs, il adaug in stocul oficial al pietei
(self.marketplace) la producatorul corespunzator lui. Totodata adaug producatorul
in lista corespunzatoare produsului curent, in dictionarul ajutator.
    Cand se doreste adaugarea unui produs in cosul de cumparaturi, se verifica mai 
intai daca acesta exista in stoc, iar daca da, se adauga in cos si se elimina din
dictionarul ajutator (se elimina producatorul din lista corespunzatoare produsului
curent).
    Cand se doreste eliminarea unui produs din cosul de cumparaturi, se face aceasta 
operatie, urmata de adaugarea produsului respectiv inapoi in stoc (in lista coresp 
produsului, din dictionarul ajutator, se adauga producatorul sau).
    Cand operatiile de modificare ale cosului de cumparaturi au luat sfarsit, comanda
este gata sa fie plasata. Pentru fiecare produs din comanda, modificam stocul 
corespunzator producatorului sau in piata (adica in self.marketplace).

    Mai multe amanunte de implementare se gasesc pe tot parcursul liniilor de cod, in
comentarii.


