# Lila et les Cauchemars — jeu de plateforme et de tir 2D (MVC)

## Histoire
Lila est une petite poupée de chiffon qui veille sur une chambre d'enfant.
Chaque nuit, des **cauchemars** sortent du placard pour envahir le rêve de l'enfant.
Lila doit traverser trois heures de la nuit, repousser les cauchemars et atteindre
le drapeau avant le lever du jour. Les jouets l'aident en lui laissant des objets magiques.

## Lancer le jeu

    pip install pygame
    python main.py

## Commandes

| Action | Touches |
|---|---|
| Avancer / reculer | `Q` `D` ou flèches gauche / droite |
| Sauter (appui long = saut plus haut) | `Z` ou flèche haut |
| Tirer | `ESPACE` (auto-visée, sinon tout droit) ou clic gauche (vers la souris) |
| Changer d'arme | `1` Pistolet, `2` Laser, `3` Fusil (après l'avoir trouvé) |
| Pause | `P` ou `Échap` |

Saute sur la tête d'un monstre pour l'écraser.

## Niveaux
Chaque niveau est un long chemin à parcourir (défilement horizontal). On peut avancer
et reculer librement. Le niveau est gagné en atteignant le drapeau d'arrivée.

| Niveau | Décor | Longueur | Monstres |
|---|---|---|---|
| 1. Le coucher | coucher de soleil | 4 800 px | ombres rampantes |
| 2. Minuit | nuit, lune, lucioles | 6 400 px | + rapides, forts, volants |
| 3. Avant l'aube | aube | 8 000 px | tous les types, plus rapides et plus résistants |

## Éléments du jeu
- **Player** : position, vitesse, santé, arme, score (saut, gravité, recul quand il est touché).
- **Monster** : position, vitesse, santé. 6 types :
  - normal : marche vers le joueur
  - rapide : petit et vif
  - fort : gros, lent, résiste au pistolet
  - volant : zigzag, faible contre le laser
  - tourelle : immobile, tire sur le joueur
  - bouclier : devient invulnérable par intermittence
- **Bullet** : position, vitesse, direction, dégâts.
- **Reward** : position, type, valeur.

| Symbole | Effet |
|---|---|
| + | soigne le joueur |
| $ | donne des points |
| S | vitesse temporaire |
| B | bouclier temporaire |
| W | débloque le Fusil (tir en éventail) |

Les monstres vaincus laissent parfois un reward. Des étoiles, un soin et une arme sont
aussi posés sur les plateformes.

## Architecture MVC

| Fichier | Rôle |
|---|---|
| `model.py` | MODÈLE : logique du jeu (joueur, physique, monstres, armes, rewards, niveaux, collisions, caméra, score). Aucun dessin, aucun clavier. |
| `view.py` | VUE : affichage uniquement (décor en couches parallaxes, poupée, monstres, HUD, menus). Lit le modèle, ne le modifie jamais. |
| `controller.py` | CONTRÔLEUR : lit le clavier et la souris, envoie des commandes au modèle, gère les écrans (menu, pause, game over...) et la boucle principale. |
| `main.py` | Point d'entrée : lance le contrôleur. |
| `assets/player.png` | Image de la poupée (facultative, voir ci-dessous). |

Flux : le contrôleur envoie des commandes au modèle (`set_input`, `fire`, `select_weapon`),
puis la vue dessine l'état du modèle.

## Principes SOLID
- **S** : le dessin est dans `view.py`, séparé de la logique des monstres et du joueur.
- **O** : un nouveau monstre est une nouvelle classe, un nouveau niveau est une ligne de la liste `LEVELS`, un nouveau reward est une entrée de `REWARD_TABLE`.
- **L** : tous les monstres respectent le même contrat : `update(target_rect)` et `take_damage(weapon)`.
- **I** : chaque monstre ne définit que son propre comportement (la tourelle ne marche pas, le monstre à bouclier gère son bouclier).
- **D** : `Monster` dépend de l'abstraction `DamageCalculator` (dégâts normaux, résistants ou faibles), pas d'une arme précise.

## Personnaliser

- **Image du personnage** : remplace `assets/player.png` par ton image (PNG à fond transparent, personnage tourné vers la droite). Elle est redimensionnée à 76 px de haut. Si le fichier est absent, la poupée dessinée par le code est utilisée.
- **Longueur et difficulté** : modifie la liste `LEVELS` dans `model.py` (longueur, nombre de monstres, types, vitesse).
- **Saut** : modifie `JUMP_SPEED` et `GRAVITY` dans `model.py`.

## Équipe
(à compléter : noms et rôles)