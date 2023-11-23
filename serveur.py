import socket
import pickle

class joueur:
    def __init__(self, client, nb) -> None:
        # Initialisation d'un joueur avec ses grilles, numéro, client et correspondance de lettres
        self.grille = [[0 for _ in range(5)] for _ in range(5)]
        self.grille_atk = [[0 for _ in range(5)] for _ in range(5)]
        self.nb = nb
        self.client = client
        self.lettre = {}
        abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(len(self.grille)):
            self.lettre[abc[i]] = i

    def positionnement(self):
        # Positionnement automatique des bateaux
        bateaux = [4, 3, 2]
        signe = ["€", "&", "#"]
        for i, largeur in enumerate(bateaux):
            ver = False
            while ver == False:
                msg = self.grille_str(self.grille) + f"\nChoisissez l'emplacement du bateau {largeur * signe[i]} sous cette forme : HA1 ou VC4, etc."
                print(msg)
                print(type(msg))
                self.send(msg)
                reponse = self.load()
                ver = self.verif(reponse, largeur)
                print(ver)
                if ver == False:
                    self.send("Erreur de placement")
            self.placement(reponse, largeur, signe[i])

    def send(self, msg):
        # Envoie un message au client
        self.client.send(pickle.dumps(msg))

    def load(self):
        # Charge et renvoie un message du client
        return pickle.loads(self.client.recv(1024))

    def placement(self, r, largeur, signe):
        # Place un bateau sur la grille en fonction de la réponse du joueur
        pos = (int(self.lettre[r[1]]), int(r[2]))
        if r[0] == 'H':
            for x in range(pos[0], pos[0] + largeur):
                self.grille[pos[1]][x] = signe
        elif r[0] == 'V':
            for y in range(pos[1], pos[1] + largeur):
                self.grille[y][pos[0]] = signe

    def verif(self, r, largeur):
        # Vérifie si la réponse du joueur est valide pour le placement du bateau
        print(r)
        pos = (int(self.lettre[r[1]]), int(r[2]))
        print(type(pos[0]), type(pos[1]), type(largeur))
        if r[0] == "H":
            if (pos[0] + int(largeur)) > len(self.grille):
                return False
            for x in range(pos[0], pos[0] + largeur):
                if self.grille[pos[1]][x] != 0:
                    return False
        elif r[0] == "V":
            if (pos[1] + int(largeur)) > len(self.grille):
                return False
            for y in range(pos[1], pos[1] + largeur):
                if self.grille[y][pos[0]] != 0:
                    return False

    def message_attaque(self):
        # Envoie la grille ennemie et demande au joueur de lancer une attaque
        msg = "Grille ennemie:\n"
        msg += self.grille_str(self.grille_atk)
        msg += "\nLancer une attaque (A1/B4/D0) :"
        self.send(msg)

    def verif_attaque(self, j2):
        # Vérifie le résultat de l'attaque et envoie la grille mise à jour
        res = self.load()
        msg = ""
        x, y = self.lettre[res[0]], int(res[1])
        if j2.grille[y][x] != 0:
            self.grille_atk[y][x] = "X"
            if j2.verif_coulé(j2.grille[y][x]):
                msg += "Bateau coulé!!\n"
            j2.grille[y][x] = "T"
            msg += "Tir réussi\n"
        else:
            self.grille_atk[y][x] = "%"
            msg = "Tir manqué\n"
        msg += self.grille_str(self.grille_atk) + "\nAppuyez sur Entrée pour passer au tour de l'adversaire"
        self.send(msg)
        self.load()

    def verif_coulé(self, signe):
        # Vérifie si un bateau est coulé
        count = 0
        for y in range(len(self.grille)):
            for x in range(len(self.grille[y])):
                if self.grille[y][x] == signe:
                    count += 1
        if count == 1:
            return True
        else:
            return False

    def verif_bateaux(self):
        # Vérifie si le joueur a des bateaux restants
        for y in range(len(self.grille)):
            for x in range(len(self.grille[y])):
                if self.grille[y][x] != "0" or self.grille[y][x] != "T":
                    return True
        return False

    def grille_str(self, grille):
        # Crée une représentation textuelle de la grille
        txt = "¤ A B C D E"
        print(grille)
        for i in range(len(grille)):
            print(i, grille[i])
            txt += f"\n{i} "
            for j in grille[i]:
                txt += str(j) + " "

        return txt


if __name__ == "__main__":
    # Création du serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(1)
    print("Attente du joueur 1...")
    client1, addr1 = server_socket.accept()
    j1 = joueur(client1, 1)
    print("Joueur 1 connecté depuis", addr1)

    print("Attente du joueur 2...")
    client2, addr2 = server_socket.accept()
    j2 = joueur(client2, 1)
    print("Joueur 2 connecté depuis", addr2)

    shot = "Bataille Navale python"
    j1.send(shot)
    j2.send(shot)

    # Positionnement des bateaux
    j1.positionnement()
    j2.positionnement()

    # Déroulement du jeu
    while j1.verif_bateaux() and j2.verif_bateaux():
        j1.message_attaque()
        j1.verif_attaque(j2)
        j2.message_attaque()
        j2.verif_attaque(j1)

    # Fin du jeu
    if j1.verif_bateaux():
        j1.send("WINNNNNNNNNNN")
        j2.send("GAME OVER")
    else:
        j2.send("WINNNNNNNNNNN")
        j1.send("GAME OVER")

#michhel23 code