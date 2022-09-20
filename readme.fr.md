# Splatplost

[中文](readme.zh-CN.md)

Splatplost est un utilitaire qui vous permet d'imprimer des images dans un dessin Splatoon, basé sur [libnxctrl](https://github.com/Victrid/libnxctrl). Pas comme les micro-controlleurs Teensy, ou les microcontrolleurs AVR, Vous avez seulement besoin d'utiliser le bluetooth de votre machine, ce qui est facile à faire. Avec un algorithme d'impression optimisé, cela peut vous sauver 1/3 du temps d'impression.

## Usage basique

### Installation

Il est recommandé d'utiliser une machine sous Linux. Ou si vous en avez pas, utiliser une [image flashable](docs/image.md). Windows ou MacOS ne sont pas supportés, car libnxctrl est basé sur bluez, le stack bluetooth de Linux.

Vous aurez besoin d'utiliser `sudo`, ou le compte root, vu que altérer le bluetooth est une opération privilégiée.

```bash
sudo pip install splatplost
```

Ceci va installer splatplost et toutes ses dépendances au niveau des paquets.

Si vous avez besoin de mettre à jour Splatplost, faites la commande `pip install --upgrade splatplost`.

### Utiliser

Générer un plan de dessin avec :

```bash
sudo splatplan -i <your image> -o <output filename>
```

Lancer l'impression :

```bash
sudo splatplot --order <output filename>
```

Vous devriez peut être voir les options de splatplot avec :

```bash
sudo splatplot --help
```

Quand "Open the pairing menu on the Switch" apparaît, allez dans le menu d'apparaige, et la Switch devrait être reconnue et associée.

Ensuite, allez dans le jeu et entrez dans l'interface de dessin avec votre propre manette. Il est important de mettre la taille du pinceau au minimum.

Quand tout est préparé, déconnectez votre manette, (un exemple : appuyez sur le petit bouton d'apparaige sur votre manette), et vous serez dans le menu pour connecter une manette.

Appuyez sur le bouton "A" sur votre ordinateur comme c'est écrit et l'impression va démarrer. Vous devriez pouvoir voir la barre de progrès durant l'impression.

## Prolème trouvé

Cliquez sur "Issues" et ouvrez une Issue.

Si vous rencontrez des bugs de connections, ouvrez une Issue sur le repo de libnxctrl : [libnxctrl](https://github.com/Victrid/libnxctrl).

## Contribuer



## License

Ce projet est basé sur libnxctrl, donc il est licensié GPLv3.

