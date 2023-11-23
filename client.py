import socket
import pickle
#veuillez entrer l'ip du pc serveur ci-dessous
ip_serveur = "x.x.x.x"

def display_grid(grid):
    for row in grid:
        print(' '.join(row))
    print()

def main():
    # Création du socket client et connexion au serveur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_serveur, 12345))

    # Réception de la grille initiale
    mess = pickle.loads(client_socket.recv(1024))
    print(mess)

    while True:
        # Affichage de la grille actuelle
        mess = pickle.loads(client_socket.recv(1024))
        print(mess)

        # Choix du tir
        shot = input("Entrez votre coup (ex. A1) : ")
        client_socket.send(pickle.dumps(shot))

        # La grille mise à jour sera reçue lors de la prochaine itération

if __name__ == "__main__":
    main()


#michhel23 code
