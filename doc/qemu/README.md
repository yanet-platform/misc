# Запуск yanet в qemu

---

В инструкции проекта создается диск сразу из `Dockerfile`, но удобнее разделить этот процесс на 2 части.

## Создание docker image
Подгтовлен `Dockerfile` в котором собрано то, что требовалось использовать на текущий момент в виртуальной машине. Запускаем создание образа:

```
docker build -f Dockerfile -t yanet-qemu:1.0 .
```

## Создание диска qcow2 для запуска qemu

Для создания дисков в формате `qcow2` можно использовать [d2vm](https://github.com/linka-cloud/d2vm).
Устанавливаем необходимые пакеты:
```
sudo apt install docker.io qemu-system-x86 iproute2
```
Загружаем образ `d2vm`:
```
docker pull linkacloud/d2vm:latest
```
Создаем alias для запуска `d2vm`:
```
alias d2vm="docker run --rm -i -t --privileged -v /var/run/docker.sock:/var/run/docker.sock -v \$PWD:/build -w /build linkacloud/d2vm:latest"
```
Создаем диск:
```
d2vm convert -v -p root -o yanet-qemu.qcow2 --bootloader grub-bios yanet-qemu:1.0
```
В системе пользователю root будет установлен пароль root (-p). Полезен параметр -v (verbose), если в процессе возникнет ошибка, проще будет разбираться.

Получается файл с образом диска чуть более 2 ГБ.

## Удаление образов в docker

В процессе создания диска `d2vm` создает несколько образов, большую часть потом удаляет (при возникновении ошибок они могут не удалиться). Лучше удалить все эти образы (возможно кроме yanet-qemu). Получаем список образов:
```
docker images
```
По колонке `CREATED` определяем образы которые были созданы только что. И удаляем их (вместо имени можно задать несколько первых символов `IMAGE ID`):
```
docker image rm <image>
```

---

## Запуск qemu
Пример запуска:
```
sudo qemu-system-x86_64 -name "Host A" \
    -enable-kvm -cpu host -m 1024 \
    -drive file=yanet-qemu.qcow2,format=qcow2,if=virtio \
    -nic tap,ifname=host_eth0,model=virtio-net-pci,mac=00:00:00:00:0a:00 \
    -virtfs local,path=share,mount_tag=host0,security_model=passthrough &
```
Параметры:
- `-name` - заголовок окна
- `-m` - размер выделяемой оперативной памяти
- `file` (drive) - путь к файлу с диском образа
- `ifname` (nic) - имя сетевого интерфейса, должно быть уникальным
- `mac` (nic) - при большом количестве виртуальных машин использую следующее правило: первые 4 пары - 00, 5-я пара - номер машины, 6-я пара - 00 (eth0), 01 (eth1), ...
- `path` (virtfs) - путь к каталогу который будет смонтирован в виртуальной машине

Для сетевой карты используемой yanet надо задать следующие параметры:
```
    -device virtio-net-pci,netdev=dev0,mac=00:00:00:00:0a:00,id=net0,vectors=17,mq=on -netdev tap,ifname=host_eth0,id=dev0,vhost=on,queues=8
```

---

## Настройка mount
Для удобства загрузки файлов на виртуальную машину удобно монтировать папку с хоста. Для этого при запуске надо добавить строку вида: 
```
    -virtfs local,path=share,mount_tag=host0,security_model=passthrough &
```
В параметре `path` задается путь к монтируемой папке. Далее, в виртуальной машине надо выполнить:
```
mount -t 9p -o trans=virtio host0 /mnt
```
Пока не получилось автоматизировать процесс монтирования при запуске системы. Пробовал следующие способы:
- `fstab` - приложен [пример](fstab) файла
- `rc.local` - приложен скрипт который содержит [команду](rc.local) монтирования
- `init.d` - пробовал также создавать [сервис](mount-parent)

Надо разобраться с порядком загрузки модулей. Пока запускаю вручную скрипт `rc.local`, он находится в домашнем каталоге root.

[Здесь](https://superuser.com/questions/502205/libvirt-9p-kvm-mount-in-fstab-fails-to-mount-at-boot-time) описано как это сделать, но у меня не заработало пока.

---

## Настройка сети
Настройка сетевых интерфейсов осуществялется через `netplan`. Надо в каталоге `/etc/netplan` на виртуальной машине создать файл `01-netcfg.yaml` ([пример файла](01-netcfg.yaml))

Для взаимодействия виртуальных машин по сети необходимо в хост системе создать bridge и добавить в него сетевые интерфейсы виртуальных машин. В примере ниже создается bridge с именем bridge_a, в нем хост система имеет адрес 10.19.0.1, добавлятся сетевые интерфейсы eth0 у hosta и hostb.
```
sudo ip link add bridge_a type bridge
sudo ip link set dev bridge_a up
sudo ip addr add 10.19.0.1/24 dev bridge_a
sudo ip link set dev hosta_eth0 master bridge_a
sudo ip link set dev hostb_eth0 master bridge_a
```

Процесс создания bridge удобно автоматизировать, пример [скрипта](bridges_yanet.sh).

После завершения тестирования можно удалить неиспользуемые более сетевые устройства ([пример скрипта] (clear_net_yanet.sh)):
```
sudo ip link delete bridge_a
sudo ip link delete hosta_eth0
sudo ip link delete hostb_eth0
```

---

## yanet low memory
Чтобы можно было запустить несколько виртуальных машин с yanet, надо его скомпилировать с меньшим потреблением памяти. Этого можно добиться путем уменьшения значения констант в `common/config.release.h`. Сделан [скрипт](make_slow_memory_dataplane.py) который уменьшает значения некоторых из них.

Запуск осуществляется из каталога `common`:
```
<path_to_script>/make_slow_memory_dataplane.py
```
В результате получается, что для dataplane достаточно 5 ГБ hugemem и для запуска виртуально машины всего требуется 8 ГБ.
