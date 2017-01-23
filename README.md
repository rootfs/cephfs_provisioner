# cephfs provisioner
Using Ceph's Volume Client to create and destroy a CephFS volume. 

# How to use it
## Create a Share
```console
# CEPH_CLUSTER_NAME=test CEPH_MON=172.24.0.4 CEPH_AUTH_ID=admin CEPH_AUTH_KEY=AQCMpH9YM4Q1BhAAXGNQyyOne8ZsXqWGon/dIQ== ./cephfs_provisioner.py -n foo -u bar
{"path": "172.24.0.4:6789:/volumes/kubernetes/foo", "user": "client.bar", "auth": "AQAE1IBYkM24NRAAV9JiNSDZuAh3xwExMv5gsw=="}
```

## Mount the share
```console
# mount -t ceph 172.24.0.4:6789:/volumes/kubernetes/foo /mnt -o name=bar,secret=AQAE1IBYkM24NRAAV9JiNSDZuAh3xwExMv5gsw==
# df -h |grep foo
172.24.0.4:6789:/volumes/kubernetes/foo  1.3G  136M  1.2G  11% /mnt
```
## Delete the Share that is created before
```console
# CEPH_CLUSTER_NAME=test CEPH_MON=172.24.0.4 CEPH_AUTH_ID=admin CEPH_AUTH_KEY=AQCMpH9YM4Q1BhAAXGNQyyOne8ZsXqWGon/dIQ== ./cephfs_provisioner.py -r -n foo -u bar
```
