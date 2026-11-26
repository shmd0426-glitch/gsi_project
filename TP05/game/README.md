# Lila et les Cauchemars — TP5 : design patterns de création

Jeu de plateforme et de tir 2D en Python / Pygame, organisé en MVC (TP4).
Pour le TP5, on ajoute **trois patterns de création** au modèle (`model.py`) :

| Tâche du devoir | Pattern | Où dans le code |
|---|---|---|
| Monstres différents à la demande (Zombie, Dragon, Robot) | **Factory Method** | `MonsterFactory` + `ZombieFactory`, `DragonFactory`, `RobotFactory`... |
| Mondes différents (monstres, armes, rewards compatibles) | **Abstract Factory** | `WorldFactory` + `ClassicWorldFactory`, `FantasyWorldFactory`, `SpaceWorldFactory` |
| Construction d'un niveau étape par étape | **Builder** | `LevelBuilder`, `ConcreteLevelBuilder`, `LevelDirector`, produit `Level` |

## Lancer

    pip install pygame
    python main.py              # le jeu
    python demo_patterns.py     # démonstration des patterns en console

## Commandes

| Action | Touches |
|---|---|
| Avancer / reculer | `Q` `D` ou flèches gauche / droite |
| Sauter (appui long = saut plus haut) | `Z` ou flèche haut |
| Tirer | `ESPACE` (auto-visée) ou clic gauche (vers la souris) |
| Changer d'arme | `1`, `2`, `3` (la 3e arme est à ramasser dans le niveau) |
| **Faire apparaître un monstre à la demande** | `N` |
| Pause | `P` ou `Échap` |

Saute sur la tête d'un monstre pour l'écraser.

## Les trois patterns

### 1. Factory Method — monstres à la demande
`MonsterFactory` est le créateur : sa méthode abstraite `create_monster(x, y)` est
redéfinie par chaque fabrique concrète (`ZombieFactory` renvoie un `Zombie`, etc.).
La méthode commune `spawn()` place le monstre (au sol ou en l'air) et applique la
difficulté du niveau. Le modèle peut créer un monstre à tout moment avec
`GameModel.spawn_monster(kind)` (touche `N` en jeu), donc plusieurs types
coexistent dans la même partie.

| Nouveau monstre | Comportement |
|---|---|
| **Zombie** | lent, 3 PV, faible au feu, se relève une fois après sa mort |
| **Dragon** | vole au-dessus du joueur, crache des boules de feu, résiste au feu |
| **Robot** | avance puis s'arrête et tire au laser, résiste au Blaster |

### 2. Abstract Factory — mondes
Un monde est une **famille d'objets compatibles**. `WorldFactory` définit ce que tout
monde doit fournir ; chaque monde concret fabrique sa propre famille et refuse les
objets des autres familles (ex. : pas de dragon dans le monde classique).

| Monde | Niveau | Décor | Monstres | Armes (départ + bonus) | Rewards |
|---|---|---|---|---|---|
| Classique | 1. Le coucher | coucher de soleil | normal | Pistolet, Laser + Fusil | `+` `$` |
| Fantastique | 2. Minuit | nuit et lune | zombie, dragon, rapide, bouclier | Étincelle, Boule de feu + Arc enchanté | potion `P`, gemme `G` |
| Spatial | 3. Au-delà des étoiles | ciel étoilé violet | robot, drone, tourelle, fort | Blaster, Plasma + Rafale | cellule `E`, cristal `C` |

Les rewards `S` (vitesse), `B` (bouclier) et `W` (arme) existent dans tous les mondes.
Un monde utilise aussi les fabriques de monstres : l'Abstract Factory s'appuie sur la
Factory Method.

### 3. Builder — construction d'un niveau
`LevelDirector.build()` appelle les étapes dans l'ordre, et `ConcreteLevelBuilder` sait
les réaliser :

1. `set_world` : choisit le monde (donc le décor) ;
2. `set_size` : longueur du niveau et drapeau ;
3. `build_platforms` : sol et plateformes ;
4. `place_monsters` : monstres et leurs positions ;
5. `place_weapons` : arme bonus sur une plateforme ;
6. `place_rewards` : pièces et soin ;
7. `get_result` : renvoie l'objet `Level` terminé.

`GameModel.load_level()` n'a plus qu'à demander un niveau au Builder.

## Ajouter du contenu (principe ouvert/fermé)
- **Nouveau monstre** : une classe qui hérite de `Monster` + une `MonsterFactory`, puis on
  l'ajoute au dictionnaire `monster_factories()` des mondes concernés.
- **Nouveau monde** : une classe qui hérite de `WorldFactory` (monstres, armes, rewards) +
  un thème dans `THEMES` de `view.py`.
- **Nouveau niveau** : une ligne dans la liste `LEVELS` de `model.py`.

## Architecture MVC

| Fichier | Rôle |
|---|---|
| `model.py` | MODÈLE : logique du jeu + les trois patterns. Aucun dessin, aucun clavier. |
| `view.py` | VUE : affichage uniquement (décors, monstres, HUD, menus). Lit le modèle. |
| `controller.py` | CONTRÔLEUR : clavier / souris, états du jeu, boucle principale. |
| `main.py` | Point d'entrée. |
| `demo_patterns.py` | Démonstration des patterns en console. |
| `assets/player.png` | Image de la poupée (facultative). |

## Équipe
(à compléter : noms et rôles)