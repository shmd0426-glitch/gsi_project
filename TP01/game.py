
import pygame
import random
import math

# Initialisation du jeu
pygame.init()

LARGEUR = 800
HAUTEUR = 600

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu de tir")

horloge = pygame.time.Clock()
police = pygame.font.SysFont(None, 36)

# Couleurs
BLANC = (255, 255, 255)
BLEU = (40, 100, 255)
ROUGE = (230, 50, 50)
JAUNE = (255, 220, 0)
NOIR = (20, 20, 20)

# Joueur
joueur = pygame.Rect(380, 500, 40, 40)
vitesse_joueur = 5
vie = 3

# Monstre
monstre = pygame.Rect(350, 100, 45, 45)
vitesse_monstre = 2

# Balles
balles = []
vitesse_balle = 8

# Score et état du jeu
score = 0
fin_jeu = False
jeu_actif = True


def creer_monstre():
    x = random.randint(0, LARGEUR - 45)
    y = random.randint(0, HAUTEUR - 45)
    return pygame.Rect(x, y, 45, 45)


while jeu_actif:
    horloge.tick(60)

    # Gestion des événements
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            jeu_actif = False

        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                jeu_actif = False

            # Tirer avec la barre espace
            if evenement.key == pygame.K_SPACE and not fin_jeu:
                dx = monstre.centerx - joueur.centerx
                dy = monstre.centery - joueur.centery
                distance = math.hypot(dx, dy)

                if distance != 0:
                    vx = dx / distance * vitesse_balle
                    vy = dy / distance * vitesse_balle

                    balles.append([
                        float(joueur.centerx),
                        float(joueur.centery),
                        vx,
                        vy
                    ])

            # Recommencer le jeu
            if evenement.key == pygame.K_r and fin_jeu:
                joueur = pygame.Rect(380, 500, 40, 40)
                monstre = creer_monstre()
                balles = []
                score = 0
                vie = 3
                fin_jeu = False

    if not fin_jeu:
        # Déplacement du joueur
        touches = pygame.key.get_pressed()

        if touches[pygame.K_LEFT] or touches[pygame.K_q]:
            joueur.x -= vitesse_joueur
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            joueur.x += vitesse_joueur
        if touches[pygame.K_UP] or touches[pygame.K_z]:
            joueur.y -= vitesse_joueur
        if touches[pygame.K_DOWN] or touches[pygame.K_s]:
            joueur.y += vitesse_joueur

        # Empêcher le joueur de sortir de l'écran
        joueur.clamp_ip(ecran.get_rect())

        # Le monstre poursuit le joueur
        dx = joueur.centerx - monstre.centerx
        dy = joueur.centery - monstre.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            monstre.x += round(dx / distance * vitesse_monstre)
            monstre.y += round(dy / distance * vitesse_monstre)

        # Le monstre attaque le joueur
        if joueur.colliderect(monstre):
            vie -= 1

            if vie <= 0:
                fin_jeu = True
            else:
                monstre = creer_monstre()

        # Déplacement des balles
        for balle in balles[:]:
            balle[0] += balle[2]
            balle[1] += balle[3]

            rectangle_balle = pygame.Rect(
                int(balle[0]), int(balle[1]), 10, 10
            )

            # Collision entre la balle et le monstre
            if rectangle_balle.colliderect(monstre):
                score += 10
                monstre = creer_monstre()
                balles.remove(balle)
                continue

            # Supprimer les balles sorties de l'écran
            if not ecran.get_rect().colliderect(rectangle_balle):
                balles.remove(balle)

    # Affichage du jeu
    ecran.fill(BLANC)

    pygame.draw.rect(ecran, BLEU, joueur)
    pygame.draw.rect(ecran, ROUGE, monstre)

    for balle in balles:
        pygame.draw.circle(
            ecran,
            JAUNE,
            (int(balle[0]), int(balle[1])),
            6
        )

    texte_score = police.render(
        f"Score : {score}", True, NOIR
    )
    texte_vie = police.render(
        f"Vies : {vie}", True, NOIR
    )

    ecran.blit(texte_score, (10, 10))
    ecran.blit(texte_vie, (10, 45))

    if fin_jeu:
        texte_fin = police.render(
            "GAME OVER - Appuyez sur R pour recommencer",
            True,
            ROUGE
        )
        ecran.blit(texte_fin, (70, 280))

    pygame.display.flip()

pygame.quit()
