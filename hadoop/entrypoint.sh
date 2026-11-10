#!/bin/sh
set -eu
mkdir -p /root/.ssh /shared-ssh /data/output
chmod 700 /root/.ssh
if [ ! -f /shared-ssh/id_ed25519 ]; then
  ssh-keygen -q -t ed25519 -N '' -f /shared-ssh/id_ed25519
fi
chmod 600 /shared-ssh/id_ed25519
ln -sf /shared-ssh/id_ed25519 /root/.ssh/id_ed25519
cp /shared-ssh/id_ed25519.pub /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
ssh-keyscan -H localhost 2>/dev/null >> /root/.ssh/known_hosts || true
/usr/sbin/sshd
printf '
HADOOP VERSION
'
hadoop version | head -n 3
printf '
SSH LOCAL
'
ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes localhost 'echo SSH_LOCAL_OK'
DATASET=/data/input/ventas_125052722.csv
if [ ! -f "$DATASET" ]; then
  echo 'ERROR: falta datos/ventas_125052722.csv. Ejecuta python generar_dataset.py 125052722 en el anfitrion.' >&2
  exec sleep infinity
fi
python3 /opt/datamart/scripts/ejecutar_pipeline.py "$DATASET" /data/output
printf '
Pipeline terminado. SSH permanece activo para la demostracion.
'
exec sleep infinity
