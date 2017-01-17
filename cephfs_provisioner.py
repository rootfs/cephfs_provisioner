import os

try:
    import ceph_volume_client
    ceph_module_found = True
except ImportError as e:
    ceph_volume_client = None
    ceph_module_found = False

VOlUME_GROUP="kubernetes"
CONF_PATH="/etc/ceph/"

class CephFSNativeDriver(object):
    """Driver for the Ceph Filesystem.

    This driver is 'native' in the sense that it exposes a CephFS filesystem
    for use directly by guests, with no intermediate layer like NFS.
    """

    def __init__(self, *args, **kwargs):
        self._volume_client = None


    def _create_conf(self, cluster_name, mons):
        """ Create conf using monitors 
        Create a minimal ceph conf with monitors and cephx
        """
        conf_path = CONF_PATH + cluster_name + ".conf"
        conf = open(conf_path, 'w')
        conf.write("[global]\n")
        conf.write("mon_host = " + mons + "\n")
        conf.write("auth_cluster_required = cephx\nauth_service_required = cephx\nauth_client_required = cephx\n")
        conf.close()
        return conf_path

    def _create_keyring(self, cluster_name, id, key):
        """ Create client keyring using id and key
        """
        keyring = open(CONF_PATH + cluster_name + "." + "client." + id + ".keyring", 'w')
        keyring.write("[client." + id + "]\n")
        keyring.write("key = " + key  + "\n")
        keyring.write("caps mds = \"allow *\"\n")
        keyring.write("caps mon = \"allow *\"\n")
        keyring.write("caps osd = \"allow *\"\n")
        keyring.close()

    @property
    def volume_client(self):
        if self._volume_client:
            return self._volume_client

        if not ceph_module_found:
            raise ValueError("Ceph client libraries not found.")

        try:
            cluster_name = os.environ["CEPH_CLUSTER_NAME"]
        except KeyError:
            cluster_name = "ceph"
        try:     
            mons = os.environ["CEPH_MON"]
        except KeyError:
            raise ValueError("Missing CEPH_MON env")
        try:
            auth_id = os.environ["CEPH_AUTH_ID"]
        except KeyError:
            raise ValueError("Missing CEPH_AUTH_ID")
        try: 
            auth_key = os.environ["CEPH_AUTH_KEY"]
        except:
            raise ValueError("Missing CEPH_AUTH_KEY")

        conf_path = self._create_conf(cluster_name, mons)
        self._create_keyring(cluster_name, auth_id, auth_key)

        self._volume_client = ceph_volume_client.CephFSVolumeClient(
            auth_id, conf_path, cluster_name)
        try:
            self._volume_client.connect(None)
        except Exception:
            self._volume_client = None
            raise

        return self._volume_client

    def create_share(self, path, size, data_isolated, user_id):
        """Create a CephFS volume.
        """
        volume_path = ceph_volume_client.VolumePath(VOlUME_GROUP, path)

        # Create the CephFS volume
        volume = self.volume_client.create_volume(
            volume_path, size=size, data_isolated=data_isolated)

        # To mount this you need to know the mon IPs and the path to the volume
        mon_addrs = self.volume_client.get_mon_addrs()

        export_location = "{addrs}:{path}".format(
            addrs=",".join(mon_addrs),
            path=volume['mount_path'])

        """TODO
        restrict to user_id
        """

        return {
            'path': export_location
        }


    def delete_share(self, path, data_isolated):
        volume_path = ceph_volume_client.VolumePath(VOlUME_GROUP, path)
        self.volume_client.delete_volume(volume_path, data_isolated=data_isolated)
        self.volume_client.purge_volume(volume_path, data_isolated=data_isolated)


    def __del__(self):
        if self._volume_client:
            self._volume_client.disconnect()
            self._volume_client = None

"""
RUN: CEPH_MON=172.24.0.4 CEPH_AUTH_ID=admin CEPH_AUTH_KEY=AQDuMX5YM/bHOBAAo0vAeJbyx1acKkvd3LLgiQ== python cephfs_provisioner.py
"""
cephfs = CephFSNativeDriver()
print cephfs.create_share("test1", 10, True, "foo")
cephfs.delete_share("test1", True)
