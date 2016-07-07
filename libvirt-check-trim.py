# Check if all libvirt domains are prepared for TRIM/fstrim

from __future__ import division, print_function

from lxml import objectify
import libvirt
import sys


conn = libvirt.openReadOnly('qemu:///system')
if not conn:
    print('Failed to open connection to the hypervisor!')
    sys.exit(1)

for domain in conn.listAllDomains():
    print('== {}'.format(domain.name()))

    xml = domain.XMLDesc()
    tree = objectify.fromstring(xml)

    # every disk should be scsi + discard=unmap
    for disk in tree.devices.disk:
        if disk.get('device') != 'disk':
            continue

        disk_desc = disk.target.get('dev')

        if disk.target.get('bus') != 'scsi':
            print('{} target should be scsi'.format(disk_desc))
        if disk.driver.get('discard') != 'unmap':
            print('{} driver should have discard=unmap'.format(disk_desc))

    # every scsi controller should be model='virtio-scsi'
    for controller in tree.devices.controller:
        if controller.get('type') != 'scsi':
            continue

        if controller.get('model') != 'virtio-scsi':
            print('scsi controller should be a virtio model')
