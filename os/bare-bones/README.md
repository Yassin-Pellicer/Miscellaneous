### Terminal Session Variables

```
export PREFIX="$HOME/code/Miscellaneous/os/cross"
export TARGET=i686-elf
export PATH="$PREFIX/bin:$PATH"
```

### Writing Kernel in C

```
i686-elf-gcc -c kernel.c -o kernel.o -std=gnu99 -ffreestanding -O2 -Wall -Wextra
```

### Linking Kernel in C

```
i686-elf-gcc -T linker.ld -o myos -ffreestanding -O2 -nostdlib boot.o kernel.o -lgcc
```

### Creating ISO img to boot with QEMU

```
mkdir -p isodir/boot/grub
cp myos isodir/boot/myos
cp grub.cfg isodir/boot/grub/grub.cfg
grub-mkrescue -o myos.iso isodir
```

### Running QEMU

```
qemu-system-i386 -cdrom myos.iso
```