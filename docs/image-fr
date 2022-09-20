# Utiliser une image préconfigurée

Si vous avez des problèmes comme:
- `Type is not subscriptable` (qui est un problème lié à la grammaire qui a changé à la version python qui est environ 3.9)
- N'importe quel problème lié à `dbus-python` ou bluetooth
- Ne peut pas voir la Switch, coincé dans le menu d'apparaige (ce qui peut être un problème lié au bluetooth de votre machine virtuelle)
- N'a pas de machine sous linux ou ne connait rien en macihne virtuelle

Vous devriez pouvoir télécharger l'image flashable et [Balena Etcher](https://www.balena.io/etcher/) pour flasher l'image flashable sur une clé USB.

Liens de téléchargements (~1.8GB):
> mega.nz: https://mega.nz/file/CSBgnZpT#Us49WL1WAp0S_qww1qobISAWMDZ-COvCAOq14NHej3k
> 
> cloud.189.cn (need login): https://cloud.189.cn/web/share?code=NNviyqZjuUZn (code d'accès: sfo9)
> 
> pan.baidu.com: https://pan.baidu.com/s/1182YwpjhaqwoLjEvUeM_9g?pwd=jxdb  (code d'accès: jxdb)

(Si vous avez une meilleure idée pour partager l'image flashable, soumettez un Issue sur la page Issues (en anglais))

Redémarrez votre ordi et allez dans le boot menu. Cela est fait en appuyant soit sur F12, F2, F10, ou F8, ou d'autres touches, cela dépend de l'ordinateur. Vous aurez probablement besoin du manuel de votre ordinateur pour connaître la touche en question. Sélectionnez votre clé USB pour continuer.

Si votre ordi est préinstallé avec Windows, vous aurez des problèmes en erreurs comme "Secure boot forbids you from booting from USB". Vous devez désactiver donc Secure Boot dans le BIOS (Vous pouvez le réactiver par la suite, ou Windows ne démarrera probablement pas)

Après avoir démarré sur l'USB, vous verrez un bureau avec une application nommée console, il s'agit du terminal, double cliquez dessus.

Écrivez `install_splatplost` dans le terminal, et après ça, ça devrait être bon. Continuez dans la section "Usage" du fichier readme.fr.md (sur Github).

Notice: L'image ne va pas essayer de écrire/éffacer sur votre disque dur, car cela nécessite des connaissances avec Linux. Si vous êtes pas familier avec Linux, il est recommandé de contenir vos arts dans un netdisk, et de les télécharger avec Firefox.

## Créer une image locale (seulement pour Guru Linux)

Utilisez une machine sous Arch Linux (machine virtuelle ou non) et installez `archiso`. Allez dans le dossier `imagebuilder` et lancez ces commandes:

```bash
make build_packages
make build
```

Lancez la commande `make clean_all` pour tout nettoyer.
