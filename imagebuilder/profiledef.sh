#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="archsplatplost"
iso_label="ARCH_SPLATPLOST_$(date +%Y%m)"
iso_publisher="Weihao Jiang <weihau.chiang@gmail.com>"
iso_application="Arch Linux Live CD with Splatplost environment"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito'
           'uefi-ia32.grub.esp' 'uefi-x64.grub.esp'
           'uefi-ia32.grub.eltorito' 'uefi-x64.grub.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/sudoers.d"]="0:0:0440"
  ["/etc/sudoers.d/splatplost"]="0:0:0440"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/etc/skel/bin/splatplan"]="1000:1000:777"
  ["/etc/skel/bin/splatplot"]="1000:1000:777"
  ["/etc/skel/bin/install_splatplost"]="1000:1000:777"
)
